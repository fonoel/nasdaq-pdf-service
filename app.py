#!/usr/bin/env python3
"""
Flask API Service to generate Nasdaq Daily Report PDFs - FIXED VERSION
Better error handling and more tolerant JSON parsing
"""

from flask import Flask, request, jsonify, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from datetime import datetime
import io
import logging
import traceback

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class ReportCanvas(canvas.Canvas):
    """Custom canvas for header and footer"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []
        
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        page_count = len(self.pages)
        for page_num, page in enumerate(self.pages, 1):
            self.__dict__.update(page)
            self.draw_page_decorations(page_num, page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_page_decorations(self, page_num, page_count):
        """Draw header and footer"""
        width, height = letter
        
        # Header
        self.saveState()
        self.setFillColor(colors.HexColor('#1E3A8A'))
        self.rect(0, height - 0.5*inch, width, 0.5*inch, fill=True, stroke=False)
        
        self.setFillColor(colors.white)
        self.setFont('Helvetica-Bold', 16)
        self.drawString(0.5*inch, height - 0.35*inch, "Nasdaq Daily Report")
        
        self.setFont('Helvetica', 10)
        report_date = datetime.now().strftime("%B %d, %Y")
        self.drawRightString(width - 0.5*inch, height - 0.35*inch, report_date)
        
        # Footer
        self.setFillColor(colors.HexColor('#E5E7EB'))
        self.rect(0, 0, width, 0.4*inch, fill=True, stroke=False)
        
        self.setFillColor(colors.HexColor('#6B7280'))
        self.setFont('Helvetica', 8)
        self.drawString(0.5*inch, 0.15*inch, 
                       "Powered by Finnhub API + Yahoo Finance + FRED + OpenAI + Make Automation")
        self.drawRightString(width - 0.5*inch, 0.15*inch, f"Page {page_num} of {page_count}")
        
        self.restoreState()


def create_styles():
    """Create custom paragraph styles"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    ))
    
    return styles


def safe_get(data, *keys, default="N/A"):
    """Safely navigate nested dictionaries"""
    try:
        result = data
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key, default)
            else:
                return default
        return result if result is not None else default
    except:
        return default


def parse_vix_term_html(html_text):
    """Extract VIX term structure data from HTML"""
    import re
    
    result = {
        'vix_1m': 'N/A',
        'vix_3m': 'N/A',
        'spread': 'N/A',
        'regime': 'N/A'
    }
    
    if not html_text:
        return result
    
    try:
        # Extract VIX 1-Month
        match = re.search(r'VIX 1-Month.*?font-size:1\.8em.*?>([\d.]+)</div>', html_text, re.DOTALL)
        if match:
            result['vix_1m'] = match.group(1)
        
        # Extract VIX 3-Month
        match = re.search(r'VIX 3-Month.*?font-size:1\.8em.*?>([\d.]+)</div>', html_text, re.DOTALL)
        if match:
            result['vix_3m'] = match.group(1)
        
        # Extract Spread
        match = re.search(r'<strong>Spread:</strong>\s*([\d.]+)\s*points', html_text)
        if match:
            result['spread'] = match.group(1)
        
        # Extract Regime
        match = re.search(r'<strong>Regime:</strong>\s*([^<]+)', html_text)
        if match:
            result['regime'] = match.group(1).strip()
    except Exception as e:
        logger.error(f"Error parsing VIX HTML: {e}")
    
    return result


def generate_pdf(data):
    """Generate PDF from Make.com data"""
    
    try:
        # Create in-memory PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=0.75*inch,
            bottomMargin=0.6*inch,
            leftMargin=0.5*inch,
            rightMargin=0.5*inch
        )
        
        styles = create_styles()
        story = []
        
        # Title
        story.append(Paragraph("NASDAQ DAILY REPORT", styles['SectionHeader']))
        story.append(Spacer(1, 0.3*inch))
        
        # ==== MACRO DASHBOARD ====
        macro = data.get('macro_dashboard', {})
        if macro:
            story.append(Paragraph("🌐 MACRO DASHBOARD", styles['SectionHeader']))
            
            regime_summary = safe_get(macro, 'regime_summary', default='')
            if regime_summary:
                story.append(Paragraph(regime_summary, styles['CustomBody']))
            story.append(Spacer(1, 0.2*inch))
        
        # ==== VIX ====
        vix = safe_get(macro, 'vix', default={})
        if vix:
            vix_content = [
                Paragraph("📊 VIX (VOLATILITY)", styles['SectionHeader']),
                Spacer(1, 0.1*inch),
            ]
            
            vix_data = [
                ['VIX Level', 'Change', 'Regime'],
                [
                    str(safe_get(vix, 'level')),
                    f"+{safe_get(vix, 'change')} (+{safe_get(vix, 'change_pct')}%)",
                    str(safe_get(vix, 'regime'))
                ]
            ]
            
            vix_table = Table(vix_data, colWidths=[2*inch, 2*inch, 2*inch])
            vix_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#EFF6FF')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DBEAFE')),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ]))
            
            vix_content.append(vix_table)
            vix_content.append(Spacer(1, 0.15*inch))
            
            interpretation = safe_get(vix, 'interpretation', default='')
            if interpretation:
                vix_content.append(Paragraph(interpretation, styles['CustomBody']))
            
            story.append(KeepTogether(vix_content))
            story.append(Spacer(1, 0.2*inch))
        
        # ==== VIX TERM STRUCTURE ====
        vix_term_html = data.get('vix_term_structure_html', '')
        vix_term_parsed = parse_vix_term_html(vix_term_html)
        
        if vix_term_parsed['vix_1m'] != 'N/A':
            vix_term_content = [
                Paragraph("📈 VIX TERM STRUCTURE", styles['SectionHeader']),
                Spacer(1, 0.1*inch),
            ]
            
            vix_term_data = [
                ['VIX 1-Month', 'VIX 3-Month', 'Spread', 'Regime'],
                [
                    str(vix_term_parsed['vix_1m']),
                    str(vix_term_parsed['vix_3m']),
                    f"{vix_term_parsed['spread']} pts",
                    str(vix_term_parsed['regime'])
                ]
            ]
            
            vix_term_table = Table(vix_term_data, colWidths=[1.6*inch, 1.6*inch, 1.6*inch, 2.3*inch])
            vix_term_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D1FAE5')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#A7F3D0')),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ]))
            
            vix_term_content.append(vix_term_table)
            story.append(KeepTogether(vix_term_content))
            story.append(Spacer(1, 0.2*inch))
        
        # ==== EXECUTIVE SUMMARY ====
        exec_summary = data.get('Executive summary', {})
        if exec_summary:
            exec_content = [
                Paragraph("📊 EXECUTIVE SUMMARY", styles['SectionHeader']),
                Spacer(1, 0.1*inch),
            ]
            
            headline = safe_get(exec_summary, 'Headline', default='')
            if headline:
                exec_content.append(Paragraph(f"<b>{headline}</b>", styles['CustomBody']))
                exec_content.append(Spacer(1, 0.1*inch))
            
            key_insight = safe_get(exec_summary, 'Key insight', default='')
            if key_insight:
                exec_content.append(Paragraph(f"<b>Key Insight:</b><br/>{key_insight}", styles['CustomBody']))
            
            story.append(KeepTogether(exec_content))
            story.append(Spacer(1, 0.25*inch))
        
        # ==== ACTION ITEMS ====
        actions = data.get('Action items', {})
        if actions:
            action_content = [
                Paragraph("✅ ACTION ITEMS", styles['SectionHeader']),
                Spacer(1, 0.15*inch),
            ]
            
            for i in range(1, 4):
                action_item = actions.get(str(i), '')
                if action_item:
                    action_content.append(Paragraph(f"• {action_item}", styles['CustomBody']))
                    action_content.append(Spacer(1, 0.1*inch))
            
            story.append(KeepTogether(action_content))
        
        # Build PDF
        doc.build(story, canvasmaker=ReportCanvas)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        logger.error(f"Error in generate_pdf: {e}")
        logger.error(traceback.format_exc())
        raise


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Nasdaq PDF Generator"}), 200


@app.route('/generate-pdf', methods=['POST'])
def generate_pdf_endpoint():
    """
    Main endpoint to generate PDF
    Expects JSON payload from Make.com
    """
    try:
        # Log the raw request
        logger.info("Received PDF generation request")
        
        # Get JSON data from request
        if not request.is_json:
            logger.error("Request is not JSON")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json(force=True)
        
        if not data:
            logger.error("No data in request")
            return jsonify({"error": "No data provided"}), 400
        
        logger.info(f"Data keys received: {list(data.keys())}")
        
        # Generate PDF
        pdf_buffer = generate_pdf(data)
        
        # Get report date for filename
        report_date = data.get('report_date', datetime.now().strftime('%Y-%m-%d'))
        filename = f"Nasdaq_Daily_Report_{report_date}.pdf"
        
        logger.info(f"PDF generated successfully: {filename}")
        
        # Return PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        "service": "Nasdaq Daily Report PDF Generator",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "generate_pdf": "/generate-pdf (POST)"
        },
        "usage": "POST your Make.com JSON data to /generate-pdf to receive a PDF"
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
