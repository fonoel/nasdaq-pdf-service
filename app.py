#!/usr/bin/env python3
"""
Flask API Service to generate Nasdaq Daily Report PDFs
This service receives JSON from Make.com and returns a professional PDF
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
        
        # Date on right
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
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
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
        'SubsectionHeader',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#3B82F6'),
        spaceAfter=8,
        spaceBefore=10,
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


def get_nested_value(data, path, default="N/A"):
    """Safely get nested dictionary values"""
    keys = path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key, default)
        else:
            return default
    return value if value is not None else default


def parse_vix_term_html(html_text):
    """Extract VIX term structure data from HTML"""
    import re
    
    result = {
        'vix_1m': 'N/A',
        'vix_3m': 'N/A',
        'spread': 'N/A',
        'regime': 'N/A'
    }
    
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
    
    return result


def generate_pdf(data):
    """Generate PDF from Make.com data"""
    
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
    
    # Extract data (Make.com format has nested collections)
    macro = data.get('macro_dashboard', {})
    exec_summary = data.get('Executive summary', {})
    market_stats = data.get('Market statistics', {})
    breadth = data.get('breadth_nasdaq_10', {})
    top_movers = data.get('Top movers', {})
    stocks = data.get('Stocks', {})
    sectors = data.get('Sector performance', {})
    forecast = data.get('Forecast 5days', {})
    actions = data.get('Action items', {})
    vix_term_html = data.get('vix_term_structure_html', '')
    
    # ==== MACRO DASHBOARD ====
    story.append(Paragraph("🌐 MACRO DASHBOARD", styles['SectionHeader']))
    story.append(Paragraph(macro.get('regime_summary', 'N/A'), styles['CustomBody']))
    story.append(Spacer(1, 0.2*inch))
    
    # ==== VIX ====
    vix_content = [
        Paragraph("📊 VIX (VOLATILITY)", styles['SectionHeader']),
        Spacer(1, 0.1*inch),
    ]
    
    vix = macro.get('vix', {})
    vix_data = [
        ['VIX Level', 'Change', 'Regime'],
        [
            str(vix.get('level', 'N/A')),
            f"+{vix.get('change', 'N/A')} (+{vix.get('change_pct', 'N/A')}%)",
            str(vix.get('regime', 'N/A'))
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
    vix_content.append(Paragraph(vix.get('interpretation', 'N/A'), styles['CustomBody']))
    
    story.append(KeepTogether(vix_content))
    story.append(Spacer(1, 0.2*inch))
    
    # ==== VIX TERM STRUCTURE ====
    vix_term_content = [
        Paragraph("📈 VIX TERM STRUCTURE", styles['SectionHeader']),
        Spacer(1, 0.1*inch),
    ]
    
    # Parse VIX Term Structure from HTML (module 82)
    vix_term_parsed = parse_vix_term_html(vix_term_html) if vix_term_html else {}
    
    vix_term_data = [
        ['VIX 1-Month', 'VIX 3-Month', 'Spread', 'Regime'],
        [
            str(vix_term_parsed.get('vix_1m', 'N/A')),
            str(vix_term_parsed.get('vix_3m', 'N/A')),
            f"{vix_term_parsed.get('spread', 'N/A')} pts",
            str(vix_term_parsed.get('regime', 'N/A'))
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
    vix_term_content.append(Spacer(1, 0.1*inch))
    
    # Add interpretation from macro_dashboard if available
    vix_term_struct = macro.get('📈 VIX TERM STRUCTURE', {})
    if vix_term_struct and vix_term_struct.get('interpretation'):
        vix_term_text = f"<b>Analysis:</b><br/>{vix_term_struct.get('interpretation', 'N/A')}"
        vix_term_content.append(Paragraph(vix_term_text, styles['CustomBody']))
    
    story.append(KeepTogether(vix_term_content))
    story.append(Spacer(1, 0.2*inch))
    
    # ==== US TREASURY 10Y ====
    treasury_content = [
        Paragraph("💰 US TREASURY 10Y", styles['SectionHeader']),
        Spacer(1, 0.1*inch),
    ]
    
    ust = macro.get('ust10y', {})
    treasury_data = [
        ['Yield', 'Change', 'Stance', 'Valuation Pressure'],
        [
            f"{ust.get('level', 'N/A')}%",
            f"{ust.get('change_bps', 'N/A')} bp",
            str(ust.get('stance', 'N/A')),
            str(ust.get('valuation_pressure', 'N/A'))
        ]
    ]
    
    treasury_table = Table(treasury_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 2*inch])
    treasury_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FEF3C7')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#FDE68A')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    treasury_content.append(treasury_table)
    treasury_content.append(Spacer(1, 0.1*inch))
    treasury_content.append(Paragraph(ust.get('interpretation', 'N/A'), styles['CustomBody']))
    
    story.append(KeepTogether(treasury_content))
    story.append(PageBreak())
    
    # ==== EXECUTIVE SUMMARY ====
    exec_content = [
        Paragraph("📊 EXECUTIVE SUMMARY", styles['SectionHeader']),
        Spacer(1, 0.1*inch),
    ]
    
    summary_data = [
        ['Market Performance', 'Regime', 'Sentiment', 'Confidence'],
        [
            str(exec_summary.get('Headline', 'N/A')),
            str(exec_summary.get('Market regime', 'N/A')),
            str(exec_summary.get('Sentiment', 'N/A')),
            f"{exec_summary.get('Confidence score', 'N/A')}/100"
        ]
    ]
    
    summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366F1')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E0E7FF')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#C7D2FE')),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
    ]))
    
    exec_content.append(summary_table)
    exec_content.append(Spacer(1, 0.15*inch))
    
    exec_text = f"<b>Key Insight:</b><br/>{exec_summary.get('Key insight', 'N/A')}<br/><br/>"
    exec_text += f"<b>Trading Thesis:</b><br/>{exec_summary.get('Trading thesis', 'N/A')}"
    exec_content.append(Paragraph(exec_text, styles['CustomBody']))
    
    story.append(KeepTogether(exec_content))
    story.append(Spacer(1, 0.25*inch))
    
    # ==== ACTION ITEMS ====
    action_content = [
        Paragraph("✅ ACTION ITEMS - TACTICAL TRADES", styles['SectionHeader']),
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
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        logger.info("Generating PDF from Make.com data")
        
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
    # Run on port 5000 by default
    app.run(host='0.0.0.0', port=5000, debug=False)
