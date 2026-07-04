import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

def clean_text(text: str) -> str:
    if not text: return ""
    # Strip emojis and smart quotes that crash ReportLab's default fonts
    return text.encode('ascii', 'ignore').decode('ascii').strip()

def generate_pdf(report_data: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Custom styles
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.grey,
        spaceAfter=20,
        alignment=1 # Center
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph(clean_text(report_data.get('company_name', 'Company Report')), title_style))
    elements.append(Paragraph("Research & Competitor Report", subtitle_style))
    elements.append(Spacer(1, 12))
    
    # Info Block
    website = clean_text(report_data.get('website', 'N/A'))
    phone = clean_text(report_data.get('phone') or 'N/A')
    address = clean_text(report_data.get('address') or 'N/A')
    
    elements.append(Paragraph(f"<b>Website:</b> {website}", normal_style))
    elements.append(Paragraph(f"<b>Phone:</b> {phone}", normal_style))
    elements.append(Paragraph(f"<b>Address:</b> {address}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Summary
    elements.append(Paragraph("Executive Summary", heading_style))
    summary_text = clean_text(report_data.get('summary', 'No summary available.'))
    for paragraph in summary_text.split('\n'):
        if paragraph.strip():
            elements.append(Paragraph(paragraph.strip(), normal_style))
            elements.append(Spacer(1, 8))
    elements.append(Spacer(1, 12))
    
    # Products & Services
    elements.append(Paragraph("Products & Services", heading_style))
    for item in report_data.get('products_services', []):
        elements.append(Paragraph(f"• {clean_text(item)}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Pain Points
    elements.append(Paragraph("Key Pain Points Solved", heading_style))
    for point in report_data.get('pain_points', []):
        elements.append(Paragraph(f"• {clean_text(point)}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Competitors
    elements.append(Paragraph("Top Competitors", heading_style))
    competitors = report_data.get('competitors', [])
    if competitors:
        data = [['Competitor Name', 'Website']]
        for comp in competitors:
            data.append([clean_text(comp.get('name', '')), clean_text(comp.get('website', ''))])
            
        table = Table(data, colWidths=[200, 300])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No major competitors identified.", normal_style))
        
    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
