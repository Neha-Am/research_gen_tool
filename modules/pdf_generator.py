from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Frame, PageTemplate, NextPageTemplate
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import FrameBreak, KeepTogether
from io import BytesIO

class PDFGenerator:
    """Handles PDF generation in IEEE conference format"""
    
    def __init__(self):
        pass
    
    def create_ieee_pdf(self, content_dict, filename, author_info=None):
        """Create IEEE format PDF from content dictionary"""
        buffer = BytesIO()
        
        # Initialize document with IEEE specs
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Calculate column widths
        page_width = A4[0]
        page_height = A4[1]
        margin_left = 0.75 * inch
        margin_right = 0.75 * inch
        margin_top = 0.75 * inch
        margin_bottom = 0.75 * inch
        column_gap = 0.25 * inch
        column_width = (page_width - margin_left - margin_right - column_gap) / 2
        
        # Create frames for two-column layout
        frame1 = Frame(
            margin_left, 
            margin_bottom,
            column_width,
            page_height - margin_top - margin_bottom,
            id='col1'
        )
        frame2 = Frame(
            margin_left + column_width + column_gap,
            margin_bottom,
            column_width,
            page_height - margin_top - margin_bottom,
            id='col2'
        )
        
        # Create page template
        template = PageTemplate(
            id='TwoCol',
            frames=[frame1, frame2]
        )
        doc.addPageTemplates([template])
        
        # Define styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'IEEETitle',
            parent=styles['Heading1'],
            fontSize=24,
            leading=28,
            alignment=TA_CENTER,
            spaceAfter=30,
            fontName='Times-Bold'
        )
        
        author_style = ParagraphStyle(
            'IEEEAuthor',
            parent=styles['Normal'],
            fontSize=12,
            leading=14,
            alignment=TA_CENTER,
            spaceAfter=12,
            fontName='Times-Roman'
        )
        
        heading_style = ParagraphStyle(
            'IEEEHeading',
            parent=styles['Heading2'],
            fontSize=10,
            leading=12,
            alignment=TA_LEFT,
            spaceBefore=12,
            spaceAfter=6,
            fontName='Times-Bold',
            keepWithNext=True
        )
        
        body_style = ParagraphStyle(
            'IEEEBody',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=TA_JUSTIFY,
            fontName='Times-Roman',
            firstLineIndent=18
        )
        
        abstract_style = ParagraphStyle(
            'IEEEAbstract',
            parent=body_style,
            fontSize=9,
            leading=11,
            alignment=TA_JUSTIFY,
            firstLineIndent=0
        )
        
        keywords_style = ParagraphStyle(
            'IEEEKeywords',
            parent=abstract_style,
            firstLineIndent=0,
            alignment=TA_LEFT,
            spaceBefore=6
        )
        
        # Build document content
        story = []
        
        # Title (spans both columns)
        story.append(NextPageTemplate('TwoCol'))
        story.append(Paragraph(content_dict['title'].upper(), title_style))
        
        # Author information - use provided info or placeholder
        if author_info and (author_info.get('Author Name') or author_info.get('Email ID') or author_info.get('Institution/Organization')):
            author_text = ""
            if author_info.get('Author Name'):
                author_text += author_info['Author Name'] + "<br/>"
            if author_info.get('Institution/Organization'):
                author_text += author_info['Institution/Organization'] + "<br/>"
            if author_info.get('Email ID'):
                author_text += author_info['Email ID']
            
            if not author_text:
                author_text = "Author Name(s)<br/>Institution(s)<br/>Email Address(es)"
        else:
            author_text = "Author Name(s)<br/>Institution(s)<br/>Email Address(es)"
        
        story.append(Paragraph(author_text, author_style))
        
        # Abstract
        abstract_heading = Paragraph('<b>Abstract</b>&mdash;' + content_dict['abstract'], abstract_style)
        story.append(KeepTogether([abstract_heading]))
        
        # Keywords
        keywords_text = '<i>Keywords</i>&mdash;' + content_dict['keywords']
        story.append(Paragraph(keywords_text, keywords_style))
        story.append(Spacer(1, 12))
        
        # Main sections
        sections = [
            ('I. INTRODUCTION', content_dict['introduction']),
            ('II. METHODOLOGY', content_dict['methodology']),
            ('III. EXPECTED RESULTS AND DISCUSSION', content_dict['results']),
            ('IV. CONCLUSION', content_dict['conclusion'])
        ]
        
        for heading, content in sections:
            story.append(Paragraph(heading, heading_style))
            # Handle content with better paragraph splitting
            if content and content.strip():
                # Split by double newlines first, then by single newlines
                paragraphs = content.split('\n\n')
                for p in paragraphs:
                    if p.strip():
                        # Further split by single newlines if needed
                        sub_paragraphs = p.split('\n')
                        for sub_p in sub_paragraphs:
                            if sub_p.strip():
                                story.append(Paragraph(sub_p.strip(), body_style))
                        # Add spacing between paragraphs
                        story.append(Spacer(1, 6))
            else:
                # If section is empty, add a placeholder
                story.append(Paragraph(f"[{heading} content will be generated]", body_style))
                story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def create_simple_pdf(self, content_dict, filename):
        """Create a simple single-column PDF (fallback option)"""
        buffer = BytesIO()
        
        # Initialize document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1*inch,
            leftMargin=1*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
        )
        
        # Define styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=14,
            leading=16,
            spaceBefore=12,
            spaceAfter=6
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=12,
            leading=14,
            alignment=TA_JUSTIFY
        )
        
        # Build document content
        story = []
        
        # Title
        story.append(Paragraph(content_dict['title'], title_style))
        
        # Abstract
        if content_dict.get('abstract'):
            story.append(Paragraph('<b>Abstract</b>', heading_style))
            story.append(Paragraph(content_dict['abstract'], body_style))
            story.append(Spacer(1, 12))
        
        # Keywords
        if content_dict.get('keywords'):
            story.append(Paragraph('<b>Keywords</b>', heading_style))
            story.append(Paragraph(content_dict['keywords'], body_style))
            story.append(Spacer(1, 12))
        
        # Main sections
        sections = [
            ('Introduction', content_dict.get('introduction', '')),
            ('Methodology', content_dict.get('methodology', '')),
            ('Results and Discussion', content_dict.get('results', '')),
            ('Conclusion', content_dict.get('conclusion', ''))
        ]
        
        for heading, content in sections:
            if content:
                story.append(Paragraph(f'<b>{heading}</b>', heading_style))
                story.append(Paragraph(content, body_style))
                story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer 