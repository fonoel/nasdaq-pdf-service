#!/usr/bin/env python3
"""
Flask API Service - COMPLETE VERSION
Generates full Nasdaq Daily Report PDFs with all sections
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
import json
import re

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
        self.drawString(0.5*inch, 0.15*inch, "Powered by Make.com Automation")
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
        'SubHeader',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=8,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    ))
    
    styles.add(ParagraphStyle(
        'CustomBodySmall',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#374151'),
        spaceAfter=4,
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
        return result if result is not None and result != "" else default
    except:
        return default


def safe_str(value, default="N/A"):
    """Safely convert to string"""
    try:
        if value is None or value == "":
            return default
        return str(value)
    except:
        return default


def parse_vix_term_html(html_text):
    """Extract VIX term structure data from HTML"""
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
        match = re.search(r'VIX 1-Month.*?font-size:1\.8em.*?>([\d.]+)</div>', str(html_text), re.DOTALL)
        if match:
            result['vix_1m'] = match.group(1)
        
        # Extract VIX 3-Month
        match = re.search(r'VIX 3-Month.*?font-size:1\.8em.*?>([\d.]+)</div>', str(html_text), re.DOTALL)
        if match:
            result['vix_3m'] = match.group(1)
        
        # Extract Spread
        match = re.search(r'<strong>Spread:</strong>\s*([\d.]+)\s*points', str(html_text))
        if match:
            result['spread'] = match.group(1)
        
        # Extract Regime
        match = re.search(r'<strong>Regime:</strong>\s*([^<]+)', str(html_text))
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
        
        # Extract main data structures
        macro = data.get('macro_dashboard', {})
        exec_summary = data.get('Executive summary', {})
        market_stats = data.get('Market statistics', {})
        breadth = data.get('breadth_nasdaq_10', {})
        top_movers = data.get('Top movers', {})
        stocks = data.get('Stocks', {})
        sectors = data.get('Sector performance', {})
        forecast = data.get('Forecast 5days', {})
        actions = data.get('Action items', {})
        
        # Title
        report_date = safe_get(data, 'report_date', default=datetime.now().strftime('%Y-%m-%d'))
        story.append(Paragraph("NASDAQ DAILY REPORT", styles['SectionHeader']))
        story.append(Paragraph(f"<b>Report Date:</b> {report_date}", styles['CustomBody']))
        story.append(Spacer(1, 0.2*inch))
        
        # ==== MACRO DASHBOARD ====
        if macro:
            story.append(Paragraph("🌐 MACRO DASHBOARD", styles['SectionHeader']))
            
            regime_summary = safe_get(macro, 'regime_summary', default='')
            if regime_summary and regime_summary != 'N/A':
                story.append(Paragraph(regime_summary, styles['CustomBody']))
            
            story.append(Spacer(1, 0.15*inch))
        
        # ==== VIX (VOLATILITY) ====
        vix = safe_get(macro, 'vix', default={})
        if vix and isinstance(vix, dict):
            vix_content = [
                Paragraph("📊 VIX (VOLATILITY)", styles['SectionHeader']),
                Spacer(1, 0.1*inch),
            ]
            
            vix_level = safe_get(vix, 'level')
            vix_change = safe_get(vix, 'change')
            vix_change_pct = safe_get(vix, 'change_pct')
            vix_regime = safe_get(vix, 'regime')
            
            vix_data = [
                ['VIX Level', 'Change', 'Regime'],
                [
                    str(vix_level),
                    f"{vix_change} ({vix_change_pct}%)",
                    str(vix_regime)
                ]
            ]
            
            vix_table = Table(vix_data, colWidths=[2*inch, 2.3*inch, 2*inch])
            vix_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#EFF6FF')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#DBEAFE')),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ]))
            
            vix_content.append(vix_table)
            vix_content.append(Spacer(1, 0.1*inch))
            
            interpretation = safe_get(vix, 'interpretation', default='')
            if interpretation and interpretation != 'N/A':
                vix_content.append(Paragraph(interpretation, styles['CustomBodySmall']))
            
            story.append(KeepTogether(vix_content))
            story.append(Spacer(1, 0.15*inch))
        
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
                    str(vix_term_parsed['regime'])[:50]
                ]
            ]
            
            vix_term_table = Table(vix_term_data, colWidths=[1.3*inch, 1.3*inch, 1.3*inch, 3.4*inch])
            vix_term_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#D1FAE5')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#A7F3D0')),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            vix_term_content.append(vix_term_table)
            story.append(KeepTogether(vix_term_content))
            story.append(Spacer(1, 0.15*inch))
        
        # ==== OTHER MACRO INDICATORS ====
        # Treasury 10Y
        ust10y = safe_get(macro, 'ust10y', default={})
        if ust10y and isinstance(ust10y, dict):
            treasury_content = [
                Paragraph("💰 US TREASURY 10Y", styles['SectionHeader']),
                Spacer(1, 0.05*inch),
            ]
            
            level = safe_get(ust10y, 'level')
            change = safe_get(ust10y, 'change_bps')
            stance = safe_get(ust10y, 'stance')
            
            treasury_content.append(Paragraph(
                f"<b>{level}%</b> (Change: {change} bps) | <b>Stance:</b> {stance}",
                styles['CustomBody']
            ))
            
            interpretation = safe_get(ust10y, 'interpretation', default='')
            if interpretation and interpretation != 'N/A':
                treasury_content.append(Spacer(1, 0.05*inch))
                treasury_content.append(Paragraph(interpretation, styles['CustomBodySmall']))
            
            story.append(KeepTogether(treasury_content))
            story.append(Spacer(1, 0.1*inch))
        
        # Dollar Index
        dxy = safe_get(macro, 'dxy', default={})
        if dxy and isinstance(dxy, dict):
            dxy_content = [
                Paragraph("💵 DOLLAR INDEX (DXY)", styles['SectionHeader']),
                Spacer(1, 0.05*inch),
            ]
            
            level = safe_get(dxy, 'level')
            change = safe_get(dxy, 'change')
            change_pct = safe_get(dxy, 'change_pct')
            trend = safe_get(dxy, 'trend')
            
            dxy_content.append(Paragraph(
                f"<b>{level}</b> ({change}, {change_pct}%) | <b>Trend:</b> {trend}",
                styles['CustomBody']
            ))
            
            interpretation = safe_get(dxy, 'interpretation', default='')
            if interpretation and interpretation != 'N/A':
                dxy_content.append(Spacer(1, 0.05*inch))
                dxy_content.append(Paragraph(interpretation, styles['CustomBodySmall']))
            
            story.append(KeepTogether(dxy_content))
            story.append(Spacer(1, 0.1*inch))
        
        # Fed Funds Rate
        fed = safe_get(macro, 'fed_funds', default={})
        if fed and isinstance(fed, dict):
            fed_content = [
                Paragraph("🏛️ FED FUNDS RATE", styles['SectionHeader']),
                Spacer(1, 0.05*inch),
            ]
            
            rate = safe_get(fed, 'rate')
            next_meeting = safe_get(fed, 'next_meeting')
            hold_prob = safe_get(fed, 'hold_probability')
            cut_prob = safe_get(fed, 'cut_probability')
            
            fed_content.append(Paragraph(
                f"<b>{rate}%</b> | Next Meeting: {next_meeting} | Hold: {hold_prob}% | Cut: {cut_prob}%",
                styles['CustomBody']
            ))
            
            interpretation = safe_get(fed, 'interpretation', default='')
            if interpretation and interpretation != 'N/A':
                fed_content.append(Spacer(1, 0.05*inch))
                fed_content.append(Paragraph(interpretation, styles['CustomBodySmall']))
            
            story.append(KeepTogether(fed_content))
            story.append(Spacer(1, 0.15*inch))
        
        # ==== EXECUTIVE SUMMARY ====
        if exec_summary and isinstance(exec_summary, dict):
            exec_content = [
                Paragraph("📊 EXECUTIVE SUMMARY", styles['SectionHeader']),
                Spacer(1, 0.1*inch),
            ]
            
            headline = safe_get(exec_summary, 'Headline', default='')
            if headline and headline != 'N/A':
                exec_content.append(Paragraph(f"<b>{headline}</b>", styles['CustomBody']))
                exec_content.append(Spacer(1, 0.08*inch))
            
            regime = safe_get(exec_summary, 'Market regime', default='')
            sentiment = safe_get(exec_summary, 'Sentiment', default='')
            confidence = safe_get(exec_summary, 'Confidence score', default='')
            
            if regime != 'N/A' or sentiment != 'N/A':
                exec_content.append(Paragraph(
                    f"<b>Regime:</b> {regime} | <b>Sentiment:</b> {sentiment} | <b>Confidence:</b> {confidence}/100",
                    styles['CustomBody']
                ))
                exec_content.append(Spacer(1, 0.08*inch))
            
            key_insight = safe_get(exec_summary, 'Key insight', default='')
            if key_insight and key_insight != 'N/A':
                exec_content.append(Paragraph(f"<b>Key Insight:</b><br/>{key_insight}", styles['CustomBody']))
                exec_content.append(Spacer(1, 0.08*inch))
            
            trading_thesis = safe_get(exec_summary, 'Trading thesis', default='')
            if trading_thesis and trading_thesis != 'N/A':
                exec_content.append(Paragraph(f"<b>Trading Thesis:</b><br/>{trading_thesis}", styles['CustomBodySmall']))
            
            story.append(KeepTogether(exec_content))
            story.append(Spacer(1, 0.15*inch))
        
        # ==== MARKET STATISTICS ====
        if market_stats and isinstance(market_stats, dict):
            stats_content = [
                Paragraph("📈 MARKET STATISTICS", styles['SectionHeader']),
                Spacer(1, 0.1*inch),
            ]
            
            stats_data = [
                ['Advancers', 'Decliners', 'A/D Ratio', 'Avg Perf', 'Median', 'Dispersion'],
                [
                    safe_str(safe_get(market_stats, 'Advancers')),
                    safe_str(safe_get(market_stats, 'Decliners')),
                    safe_str(safe_get(market_stats, 'ad_ratio')),
                    safe_str(safe_get(market_stats, 'Avg performance')),
                    safe_str(safe_get(market_stats, 'Median performance')),
                    safe_str(safe_get(market_stats, 'dispersion'))
                ]
            ]
            
            stats_table = Table(stats_data, colWidths=[1.1*inch, 1.1*inch, 1.0*inch, 1.0*inch, 1.0*inch, 1.1*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366F1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#E0E7FF')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#C7D2FE')),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ]))
            
            stats_content.append(stats_table)
            story.append(KeepTogether(stats_content))
            story.append(Spacer(1, 0.15*inch))
        
        # ==== TOP MOVERS ====
        if top_movers and isinstance(top_movers, dict):
            story.append(Paragraph("🔥 TOP 3 MOVERS", styles['SectionHeader']))
            story.append(Spacer(1, 0.1*inch))
            
            for i in range(1, 4):
                mover = top_movers.get(str(i), {})
                if mover and isinstance(mover, dict):
                    symbol = safe_get(mover, 'symbol')
                    price = safe_get(mover, 'price')
                    change_pct = safe_get(mover, 'change_pct')
                    momentum = safe_get(mover, 'momentum')
                    risk = safe_get(mover, 'risk_level')
                    reason = safe_get(mover, 'reason')
                    analysis = safe_get(mover, 'analysis', default='')
                    
                    mover_content = [
                        Paragraph(
                            f"<b>{symbol}</b> ${price} ({change_pct}%) | "
                            f"Momentum: {momentum} | Risk: {risk}",
                            styles['CustomBody']
                        ),
                    ]
                    
                    if reason and reason != 'N/A':
                        mover_content.append(Paragraph(f"<b>Reason:</b> {reason}", styles['CustomBodySmall']))
                    
                    if analysis and analysis != 'N/A' and len(analysis) > 10:
                        mover_content.append(Spacer(1, 0.03*inch))
                        mover_content.append(Paragraph(analysis[:400], styles['CustomBodySmall']))
                    
                    story.append(KeepTogether(mover_content))
                    story.append(Spacer(1, 0.1*inch))
        
        # ==== SECTOR PERFORMANCE ====
        if sectors and isinstance(sectors, dict):
            story.append(Paragraph("📊 SECTOR PERFORMANCE", styles['SectionHeader']))
            story.append(Spacer(1, 0.1*inch))
            
            for sector_name in ['Technology', 'Consumer', 'Semiconductors']:
                sector = sectors.get(sector_name, {})
                if sector and isinstance(sector, dict):
                    avg_perf = safe_get(sector, 'Avg performance')
                    best = safe_get(sector, 'Best performer')
                    worst = safe_get(sector, 'Worst performer')
                    comment = safe_get(sector, 'Comment', default='')
                    
                    sector_content = [
                        Paragraph(f"<b>{sector_name}:</b> {avg_perf} | Best: {best} | Worst: {worst}", 
                                styles['CustomBody']),
                    ]
                    
                    if comment and comment != 'N/A' and len(comment) > 10:
                        sector_content.append(Spacer(1, 0.03*inch))
                        sector_content.append(Paragraph(comment[:300], styles['CustomBodySmall']))
                    
                    story.append(KeepTogether(sector_content))
                    story.append(Spacer(1, 0.08*inch))
            
            story.append(Spacer(1, 0.1*inch))
        
        # ==== 5-DAY FORECAST ====
        if forecast and isinstance(forecast, dict):
            forecast_content = [
                Paragraph("🔮 5-DAY FORECAST", styles['SectionHeader']),
                Spacer(1, 0.1*inch),
            ]
            
            direction = safe_get(forecast, 'Direction')
            expected_return = safe_get(forecast, 'Expected return pct')
            probability = safe_get(forecast, 'Probability')
            
            forecast_content.append(Paragraph(
                f"<b>Direction:</b> {direction} | <b>Expected Return:</b> {expected_return} | <b>Probability:</b> {probability}",
                styles['CustomBody']
            ))
            forecast_content.append(Spacer(1, 0.1*inch))
            
            # Bull/Base/Bear cases
            for case_name in ['bull_case', 'base_case', 'bear_case']:
                case_text = safe_get(forecast, case_name, default='')
                if case_text and case_text != 'N/A' and len(case_text) > 10:
                    case_label = case_name.replace('_', ' ').title()
                    forecast_content.append(Paragraph(f"<b>{case_label}:</b>", styles['CustomBody']))
                    forecast_content.append(Paragraph(case_text[:300], styles['CustomBodySmall']))
                    forecast_content.append(Spacer(1, 0.06*inch))
            
            # Key Catalysts
            catalysts = safe_get(forecast, 'key_catalysts', default={})
            if catalysts and isinstance(catalysts, dict):
                forecast_content.append(Paragraph("<b>Key Catalysts:</b>", styles['CustomBody']))
                for i in range(1, 4):
                    catalyst = catalysts.get(str(i), '')
                    if catalyst and catalyst != 'N/A':
                        forecast_content.append(Paragraph(f"• {catalyst}", styles['CustomBodySmall']))
            
            story.append(KeepTogether(forecast_content))
            story.append(Spacer(1, 0.15*inch))
        
        # ==== ACTION ITEMS ====
        if actions:
            action_content = [
                Paragraph("✅ ACTION ITEMS", styles['SectionHeader']),
                Spacer(1, 0.1*inch),
            ]
            
            # Handle both dict and list formats
            if isinstance(actions, dict):
                for i in range(1, 6):
                    action_item = actions.get(str(i), '')
                    if action_item and action_item != 'N/A':
                        action_content.append(Paragraph(f"• {action_item}", styles['CustomBody']))
                        action_content.append(Spacer(1, 0.05*inch))
            elif isinstance(actions, list):
                for action_item in actions:
                    if action_item:
                        action_content.append(Paragraph(f"• {action_item}", styles['CustomBody']))
                        action_content.append(Spacer(1, 0.05*inch))
            
            story.append(KeepTogether(action_content))
        
        # Disclaimer
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph(
            "<i>This report is generated automatically and should not be considered as financial advice. "
            "Always do your own research before making investment decisions.</i>",
            styles['CustomBodySmall']
        ))
        
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
    """Main endpoint to generate PDF"""
    try:
        logger.info("Received PDF generation request")
        logger.info(f"Content-Type: {request.content_type}")
        
        # Try multiple ways to get the data
        data = None
        
        try:
            data = request.get_json(force=True, silent=True)
            if data:
                logger.info("✅ Parsed as JSON")
        except:
            pass
        
        if not data:
            try:
                data = request.form.to_dict()
                if data:
                    logger.info("✅ Parsed as form data")
                    for key in data:
                        try:
                            data[key] = json.loads(data[key])
                        except:
                            pass
            except:
                pass
        
        if not data:
            try:
                raw_data = request.data.decode('utf-8')
                data = json.loads(raw_data)
                if data:
                    logger.info("✅ Parsed raw data as JSON")
            except:
                pass
        
        if not data:
            logger.warning("⚠️ Could not parse request data, creating minimal structure")
            data = {
                "report_date": datetime.now().strftime('%Y-%m-%d'),
            }
        
        logger.info(f"Data keys: {list(data.keys()) if isinstance(data, dict) else 'not a dict'}")
        
        # Generate PDF
        pdf_buffer = generate_pdf(data)
        
        # Get report date for filename
        report_date = data.get('report_date', datetime.now().strftime('%Y-%m-%d'))
        filename = f"Nasdaq_Daily_Report_{report_date}.pdf"
        
        logger.info(f"✅ PDF generated successfully: {filename}")
        
        # Return PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"❌ Error generating PDF: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with API information"""
    return jsonify({
        "service": "Nasdaq Daily Report PDF Generator",
        "version": "2.0.0 - Complete Edition",
        "endpoints": {
            "health": "/health",
            "generate_pdf": "/generate-pdf (POST)"
        },
        "usage": "POST your Make.com data to /generate-pdf to receive a PDF"
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
