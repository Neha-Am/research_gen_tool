import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import PyPDF2
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
import tempfile
import json
from datetime import datetime


load_dotenv()


genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Initialize session state for edit functionality
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = ""
if 'content_dict' not in st.session_state:
    st.session_state.content_dict = {}
if 'custom_parameters' not in st.session_state:
    st.session_state.custom_parameters = {}
if 'paper_title' not in st.session_state:
    st.session_state.paper_title = ""
if 'displaying_existing' not in st.session_state:
    st.session_state.displaying_existing = False
if 'api_calls' not in st.session_state:
    st.session_state.api_calls = 0

# API Call Tracking Functions
def load_api_call_count():
    """Load API call count from file"""
    try:
        if os.path.exists('api_call_tracker.json'):
            with open('api_call_tracker.json', 'r') as f:
                data = json.load(f)
                return data.get('total_calls', 0), data.get('call_history', [])
        return 0, []
    except Exception as e:
        st.error(f"Error loading API call count: {str(e)}")
        return 0, []

def save_api_call_count(total_calls, call_history):
    """Save API call count to file"""
    try:
        data = {
            'total_calls': total_calls,
            'call_history': call_history,
            'last_updated': datetime.now().isoformat()
        }
        with open('api_call_tracker.json', 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving API call count: {str(e)}")

def increment_api_call(function_name):
    """Increment API call count and save to file"""
    # Load current count
    total_calls, call_history = load_api_call_count()
    
    # Increment count
    total_calls += 1
    st.session_state.api_calls = total_calls
    
    # Add to history
    call_record = {
        'timestamp': datetime.now().isoformat(),
        'function': function_name,
        'call_number': total_calls
    }
    call_history.append(call_record)
    
    # Keep only last 100 records to prevent file from growing too large
    if len(call_history) > 100:
        call_history = call_history[-100:]
    
    # Save updated count
    save_api_call_count(total_calls, call_history)
    
    return total_calls

def reset_api_call_count():
    """Reset API call count to zero"""
    try:
        data = {
            'total_calls': 0,
            'call_history': [],
            'last_updated': datetime.now().isoformat(),
            'reset_at': datetime.now().isoformat()
        }
        with open('api_call_tracker.json', 'w') as f:
            json.dump(data, f, indent=2)
        st.session_state.api_calls = 0
        return True
    except Exception as e:
        st.error(f"Error resetting API call count: {str(e)}")
        return False

def read_instructions():
    with open('instructions.txt', 'r') as file:
        return file.read()

def read_pdf_template():
    with open('ieee-conference-template.pdf', 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_uploaded_pdf(uploaded_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def create_ieee_pdf(content_dict, filename, author_info=None):
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

def parse_generated_content(content):
    sections = {
        'title': '',
        'abstract': '',
        'keywords': '',
        'introduction': '',
        'methodology': '',
        'results': '',
        'conclusion': ''
    }
    
    current_section = None
    current_content = []
    
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        lower_line = line.lower()
        
        # Check for section headers with more flexible matching
        if any(keyword in lower_line for keyword in ['abstract']) and len(line) < 30:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'abstract'
            current_content = []
            
        elif any(keyword in lower_line for keyword in ['keywords', 'keyword']) and len(line) < 50:
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'keywords'
            current_content = []
            
        elif any(keyword in lower_line for keyword in ['introduction', 'i. introduction', '1. introduction']):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'introduction'
            current_content = []
            
        elif any(keyword in lower_line for keyword in ['methodology', 'methods', 'ii. methodology', '2. methodology']):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'methodology'
            current_content = []
            
        elif any(keyword in lower_line for keyword in ['results', 'discussion', 'expected results', 'iii. expected results', '3. expected results']):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'results'
            current_content = []
            
        elif any(keyword in lower_line for keyword in ['conclusion', 'conclusions', 'iv. conclusion', '4. conclusion']):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = 'conclusion'
            current_content = []
            
        elif current_section and line:
            # Add content to current section
            current_content.append(line)
    
    # Save the last section
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
    
    # Clean up sections - remove any empty sections
    for key in sections:
        if not sections[key]:
            sections[key] = f"[{key.title()} content will be generated]"
    
    return sections

def generate_paper_content(title, research_field, methodology, expected_results, additional_context="", custom_parameters=None):
    
    instructions = read_instructions()
    
    # Build context from uploaded PDF if available
    context_info = ""
    if additional_context:
        context_info = f"\nAdditional Context from uploaded material:\n{additional_context}\n"
    
    # Build custom parameters info if provided
    custom_params_info = ""
    if custom_parameters:
        custom_params_info = "\nAdditional Parameters:\n"
        for param_name, param_value in custom_parameters.items():
            if param_value:  # Only include non-empty parameters
                custom_params_info += f"- {param_name}: {param_value}\n"
    
    prompt = f"""
    Generate an IEEE conference paper content based on the following details:
    
    Title: {title}
    Research Field: {research_field}
    Methodology: {methodology}
    Expected Results: {expected_results}{context_info}{custom_params_info}
    
    Follow these IEEE formatting instructions:
    {instructions}
    
    Generate the content in the following sections with clear headers:
    
    Abstract
    [Generate 150-250 word abstract here]
    
    Keywords
    [Generate 3-5 keywords separated by commas]
    
    I. INTRODUCTION
    [Generate introduction content here]
    
    II. METHODOLOGY
    [Generate methodology content here]
    
    III. EXPECTED RESULTS AND DISCUSSION
    [Generate results and discussion content here]
    
    IV. CONCLUSION
    [Generate conclusion content here]
    
    IMPORTANT: 
    1. Generate only the academic paper content. Do NOT include any conversation, explanations, or meta-commentary about the generation process.
    2. Use the exact section headers as shown above (Abstract, Keywords, I. INTRODUCTION, etc.)
    3. The output should be a clean, professional research paper that could be directly submitted to an IEEE conference.
    4. Ensure each section has substantial content (at least 2-3 paragraphs for main sections).
    5. Make sure the content is academic, well-structured, and follows IEEE guidelines.
    """
    
    # Track API call
    increment_api_call("generate_paper_content")
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content(prompt)
    return response.text

def extract_and_analyze_pdf_content(pdf_text):
    """Extract and analyze content from uploaded PDF to generate paper details"""
    if not pdf_text or len(pdf_text.strip()) < 50:
        return None
    
    # Use LLM to analyze PDF content and extract relevant information
    analysis_prompt = f"""
    Analyze the following PDF content and extract relevant information for generating an IEEE conference paper:
    
    PDF Content:
    {pdf_text[:2000]}  # Limit to first 2000 characters for analysis
    
    Please extract and provide the following information in a structured format:
    1. Suggested Title (based on the content)
    2. Research Field/Area
    3. Methodology/Approach mentioned
    4. Expected Results/Findings
    5. Key Topics/Keywords
    
    Format your response as:
    TITLE: [suggested title]
    FIELD: [research field]
    METHODOLOGY: [methodology]
    RESULTS: [expected results]
    KEYWORDS: [keywords]
    
    If any information is not clearly available, use "Not specified" for that field.
    """
    
    try:
        # Track API call
        increment_api_call("extract_and_analyze_pdf_content")
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(analysis_prompt)
        return response.text
    except Exception as e:
        st.error(f"Error analyzing PDF content: {str(e)}")
        return None

def parse_analysis_result(analysis_text):
    """Parse the analysis result from PDF content"""
    if not analysis_text:
        return {}
    
    result = {}
    lines = analysis_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().upper()
            value = value.strip()
            if value and value.lower() != "not specified":
                result[key] = value
    
    return result

def validate_inputs(title, research_field, methodology, expected_results):
    """Validate inputs and return validation status and messages"""
    errors = []
    warnings = []
    
    # Check for required fields
    if not title or title.strip() == "" or title.lower() in ["na", "n/a", "none", ""]:
        errors.append("Paper title is required")
    elif len(title.strip()) < 5:
        warnings.append("Paper title seems too short")
    
    if not research_field or research_field.strip() == "" or research_field.lower() in ["na", "n/a", "none", ""]:
        errors.append("Research field is required")
    elif len(research_field.strip()) < 10:
        warnings.append("Research field description seems too brief")
    
    if not methodology or methodology.strip() == "" or methodology.lower() in ["na", "n/a", "none", ""]:
        errors.append("Methodology is required")
    elif len(methodology.strip()) < 10:
        warnings.append("Methodology description seems too brief")
    
    if not expected_results or expected_results.strip() == "" or expected_results.lower() in ["na", "n/a", "none", ""]:
        errors.append("Expected results are required")
    elif len(expected_results.strip()) < 10:
        warnings.append("Expected results description seems too brief")
    
    return errors, warnings

def main():
    st.set_page_config(page_title="IEEE Conference Paper Generator", layout="wide")
    
    # Load API call count at startup
    total_calls, call_history = load_api_call_count()
    st.session_state.api_calls = total_calls
    
    st.title("IEEE Conference Paper Content Generator")
    st.markdown("Generate professional IEEE conference paper content based on your inputs.")
    
    # Display API call tracking
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total API Calls", total_calls)
    with col2:
        if call_history:
            last_call = call_history[-1]
            last_call_time = datetime.fromisoformat(last_call['timestamp']).strftime("%Y-%m-%d %H:%M")
            st.metric("🕒 Last API Call", last_call_time)
        else:
            st.metric("🕒 Last API Call", "None")
    with col3:
        if call_history:
            today_calls = len([call for call in call_history 
                             if datetime.fromisoformat(call['timestamp']).date() == datetime.now().date()])
            st.metric("📅 Today's Calls", today_calls)
        else:
            st.metric("📅 Today's Calls", 0)
    with col4:
        if total_calls > 0:
            # Calculate estimated cost
            estimated_input_tokens = total_calls * 2000
            estimated_output_tokens = total_calls * 1000
            estimated_cost_input = (estimated_input_tokens / 1000000) * 0.075
            estimated_cost_output = (estimated_output_tokens / 1000000) * 0.30
            estimated_total_cost = estimated_cost_input + estimated_cost_output
            st.metric("💰 Est. Cost (USD)", f"${estimated_total_cost:.4f}")
        else:
            st.metric("💰 Est. Cost (USD)", "$0.0000")
    
    # Add download button for API call counter details
    if total_calls > 0:
        # Calculate estimated cost (Gemini 2.0 Flash pricing as of 2024)
        # Input: $0.075 per 1M tokens, Output: $0.30 per 1M tokens
        # Assuming average of 2000 input tokens and 1000 output tokens per call
        estimated_input_tokens = total_calls * 2000
        estimated_output_tokens = total_calls * 1000
        estimated_cost_input = (estimated_input_tokens / 1000000) * 0.075
        estimated_cost_output = (estimated_output_tokens / 1000000) * 0.30
        estimated_total_cost = estimated_cost_input + estimated_cost_output
        
        # Create detailed JSON data for download
        api_details = {
            "summary": {
                "total_calls": total_calls,
                "today_calls": len([call for call in call_history 
                                  if datetime.fromisoformat(call['timestamp']).date() == datetime.now().date()]) if call_history else 0,
                "last_call_time": call_history[-1]['timestamp'] if call_history else None,
                "last_updated": datetime.now().isoformat(),
                "estimated_cost": {
                    "input_tokens": estimated_input_tokens,
                    "output_tokens": estimated_output_tokens,
                    "input_cost_usd": round(estimated_cost_input, 4),
                    "output_cost_usd": round(estimated_cost_output, 4),
                    "total_cost_usd": round(estimated_total_cost, 4)
                }
            },
            "call_history": call_history,
            "function_breakdown": {}
        }
        
        # Calculate function breakdown
        for call in call_history:
            func_name = call['function']
            if func_name not in api_details["function_breakdown"]:
                api_details["function_breakdown"][func_name] = 0
            api_details["function_breakdown"][func_name] += 1
        
        # Download buttons in a row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                label="📊 Download API Details (JSON)",
                data=json.dumps(api_details, indent=2),
                file_name=f"api_call_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        with col2:
            # Create CSV format for easier analysis
            csv_data = "Call Number,Function,Timestamp,Date,Time\n"
            for call in call_history:
                call_time = datetime.fromisoformat(call['timestamp'])
                csv_data += f"{call['call_number']},{call['function']},{call['timestamp']},{call_time.strftime('%Y-%m-%d')},{call_time.strftime('%H:%M:%S')}\n"
            
            st.download_button(
                label="📈 Download API History (CSV)",
                data=csv_data,
                file_name=f"api_call_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        with col3:
            # Create summary report
            summary_text = f"""API Call Summary Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TOTAL API CALLS: {total_calls}
TODAY'S CALLS: {api_details['summary']['today_calls']}
LAST CALL: {api_details['summary']['last_call_time']}

COST ESTIMATION:
- Estimated Input Tokens: {api_details['summary']['estimated_cost']['input_tokens']:,}
- Estimated Output Tokens: {api_details['summary']['estimated_cost']['output_tokens']:,}
- Input Cost: ${api_details['summary']['estimated_cost']['input_cost_usd']}
- Output Cost: ${api_details['summary']['estimated_cost']['output_cost_usd']}
- Total Estimated Cost: ${api_details['summary']['estimated_cost']['total_cost_usd']}

FUNCTION BREAKDOWN:
"""
            for func, count in api_details["function_breakdown"].items():
                summary_text += f"- {func}: {count} calls\n"
            
            summary_text += f"\nDETAILED HISTORY (Last 20 calls):\n"
            summary_text += "="*50 + "\n"
            for call in call_history[-20:]:
                call_time = datetime.fromisoformat(call['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                summary_text += f"#{call['call_number']} - {call['function']} - {call_time}\n"
            
            st.download_button(
                label="📋 Download Summary Report",
                data=summary_text,
                file_name=f"api_call_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    # Show API call history in expander
    if call_history:
        with st.expander("📈 API Call History & Analytics"):
            # Function breakdown
            function_counts = {}
            for call in call_history:
                func_name = call['function']
                if func_name not in function_counts:
                    function_counts[func_name] = 0
                function_counts[func_name] += 1
            
            st.markdown("### 📊 Function Breakdown")
            for func, count in function_counts.items():
                percentage = (count / total_calls) * 100
                st.progress(percentage / 100)
                st.text(f"{func}: {count} calls ({percentage:.1f}%)")
            
            st.markdown("### 📝 Recent Calls (Last 10)")
            recent_calls = call_history[-10:]
            for call in reversed(recent_calls):
                call_time = datetime.fromisoformat(call['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                st.text(f"#{call['call_number']} - {call['function']} - {call_time}")
            
            # Add download button for full history
            if len(call_history) > 10:
                history_text = "API Call History\n" + "="*50 + "\n"
                for call in call_history:
                    call_time = datetime.fromisoformat(call['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                    history_text += f"#{call['call_number']} - {call['function']} - {call_time}\n"
                
                st.download_button(
                    label="📥 Download Full History",
                    data=history_text,
                    file_name=f"api_call_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    # Add reset button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🔄 Reset API Counter", key="reset_api_btn"):
            if reset_api_call_count():
                st.success("✅ API call counter reset successfully!")
                st.rerun()
    
    st.markdown("---")
    
    # PDF Upload Section
    st.markdown("## 📄 Upload Reference Material (Optional)")
    st.markdown("Upload a PDF to provide additional context for the paper generation. If you don't provide detailed inputs, the system will try to extract information from your PDF.")
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    additional_context = ""
    pdf_analysis = None
    
    if uploaded_file is not None:
        additional_context = extract_text_from_uploaded_pdf(uploaded_file)
        if additional_context:
            st.success("PDF uploaded successfully! Content will be used as additional context.")
            with st.expander("Preview uploaded content"):
                st.text(additional_context[:500] + "..." if len(additional_context) > 500 else additional_context)
            
            # Analyze PDF content for automatic extraction
            with st.spinner("Analyzing PDF content..."):
                pdf_analysis = extract_and_analyze_pdf_content(additional_context)
                if pdf_analysis:
                    st.info("📋 PDF analysis complete! You can use the extracted information below.")
                    with st.expander("📄 Extracted Information from PDF"):
                        st.text(pdf_analysis)
    
    # Main Input Section
    st.markdown("## 📝 Paper Details")
    
    # Parse PDF analysis if available
    extracted_info = {}
    if pdf_analysis:
        extracted_info = parse_analysis_result(pdf_analysis)
    
    # Check if we have existing generated content to display
    if st.session_state.generated_content:
        st.markdown("## 📄 Previously Generated Content")
        
        # Add clear content button
        if st.button("🗑️ Clear All Content", key="clear_content_btn"):
            st.session_state.generated_content = ""
            st.session_state.content_dict = {}
            st.session_state.custom_parameters = {}
            st.session_state.paper_title = ""
            st.session_state.edit_mode = False
            st.session_state.displaying_existing = False
            st.success("✅ Content cleared! You can generate new content below.")
            st.rerun()
        
        # Set flag to indicate we're displaying existing content
        st.session_state.displaying_existing = True
        display_generated_content()
        provide_download_buttons()
        st.markdown("---")
        st.markdown("### 🔄 Generate New Content")
        st.info("💡 You can generate new content below, or continue editing the existing content above.")
    else:
        st.session_state.displaying_existing = False
    
    # Required inputs with auto-fill from PDF
    title_placeholder = extracted_info.get('TITLE', "Enter the title of your research paper")
    title = st.text_input("Paper Title *", value=extracted_info.get('TITLE', ''), placeholder=title_placeholder)
    
    col1, col2 = st.columns(2)
    with col1:
        research_field_placeholder = extracted_info.get('FIELD', "Describe your research field and context")
        research_field = st.text_area("Research Field *", 
                                    value=extracted_info.get('FIELD', ''),
                                    placeholder=research_field_placeholder)
        
        methodology_placeholder = extracted_info.get('METHODOLOGY', "Describe your research methodology")
        methodology = st.text_area("Methodology *", 
                                 value=extracted_info.get('METHODOLOGY', ''),
                                 placeholder=methodology_placeholder)
    
    with col2:
        expected_results_placeholder = extracted_info.get('RESULTS', "Describe your expected results or findings")
        expected_results = st.text_area("Expected Results *", 
                                      value=extracted_info.get('RESULTS', ''),
                                      placeholder=expected_results_placeholder)
    
    # Optional Parameters Section
    st.markdown("## ⚙️ Additional Parameters (Optional)")
    st.markdown("These parameters are optional and will provide additional context for paper generation.")
    
    # Author Information Section
    st.markdown("### 👤 Author Information (Optional)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        author_name = st.text_input("Author Name", placeholder="e.g., John Smith")
    
    with col2:
        email_id = st.text_input("Email ID", placeholder="e.g., john.smith@university.edu")
    
    with col3:
        institution = st.text_input("Institution/Organization", placeholder="e.g., University of Technology")
    
    # Additional Custom Parameters
    st.markdown("### 🔧 Additional Parameters (Optional)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        custom_param1 = st.text_input("Parameter 1", placeholder="e.g., Dataset size, Algorithm type")
        custom_param2 = st.text_input("Parameter 2", placeholder="e.g., Evaluation metrics")
    
    with col2:
        custom_param3 = st.text_input("Parameter 3", placeholder="e.g., Implementation details")
        custom_param4 = st.text_input("Parameter 4", placeholder="e.g., Related work focus")
    
    with col3:
        custom_param5 = st.text_input("Parameter 5", placeholder="e.g., Future work direction")
        custom_param6 = st.text_input("Parameter 6", placeholder="e.g., Technical constraints")
    
    # Collect custom parameters including author information
    custom_parameters = {
        "Author Name": author_name,
        "Email ID": email_id,
        "Institution/Organization": institution,
        "Parameter 1": custom_param1,
        "Parameter 2": custom_param2,
        "Parameter 3": custom_param3,
        "Parameter 4": custom_param4,
        "Parameter 5": custom_param5,
        "Parameter 6": custom_param6
    }
    
    if st.button("Generate Paper Content", key="generate_paper_btn"):
        # Validate inputs
        errors, warnings = validate_inputs(title, research_field, methodology, expected_results)
        
        # Show warnings if any
        if warnings:
            for warning in warnings:
                st.warning(f"⚠️ {warning}")
        
        # Show errors and stop if any
        if errors:
            st.error("❌ Please fix the following issues:")
            for error in errors:
                st.error(f"• {error}")
            
            # Provide helpful suggestions
            if uploaded_file and additional_context:
                st.info("💡 Tip: The system has analyzed your uploaded PDF. You can use the extracted information above or provide your own details.")
            else:
                st.info("💡 Tip: Consider uploading a PDF reference document to help generate content, or provide more detailed information in the required fields.")
            
            return
        
        # Check if we have enough content to generate
        if len(title.strip()) < 5 or len(research_field.strip()) < 10 or len(methodology.strip()) < 10 or len(expected_results.strip()) < 10:
            st.warning("⚠️ The provided information seems insufficient. Consider providing more detailed descriptions or uploading a reference PDF.")
            if not uploaded_file:
                st.info("💡 Tip: Uploading a PDF can help the system generate better content even with minimal input.")
        
        with st.spinner("Generating paper content..."):
            try:
                generated_content = generate_paper_content(
                    title, research_field, methodology, expected_results, 
                    additional_context, custom_parameters
                )
                
                if not generated_content or len(generated_content.strip()) < 100:
                    st.error("❌ Generated content is too short or empty. Please try again with more detailed inputs or upload a reference PDF.")
                    return
                
                st.success("Content generated successfully!")
                st.markdown("## Generated Paper Content")
                
                # Store generated content in session state
                st.session_state.generated_content = generated_content
                st.session_state.content_dict = parse_generated_content(generated_content)
                st.session_state.content_dict['title'] = title  # Use the original title
                st.session_state.custom_parameters = custom_parameters
                st.session_state.paper_title = title
                
                # Only display content if we're not already displaying existing content
                if not st.session_state.get('displaying_existing', False):
                    # Display content with edit functionality
                    display_generated_content()
                    
                    # Generate and provide download buttons
                    provide_download_buttons()
                
            except Exception as e:
                st.error(f"❌ An error occurred during generation: {str(e)}")
                st.info("💡 Try providing more detailed information or uploading a reference PDF to improve results.")

def display_generated_content():
    """Display generated content with edit functionality"""
    if not st.session_state.generated_content:
        return
    
    # Edit/Preview toggle with better styling
    st.markdown("### 📝 Content Editor")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.button("✏️ Edit Content" if not st.session_state.edit_mode else "👁️ Preview", key="edit_toggle_btn"):
            st.session_state.edit_mode = not st.session_state.edit_mode
            st.rerun()
    
    with col2:
        if st.session_state.edit_mode:
            st.info("💡 **Edit Mode Active** - Make your changes below and save to update the PDF")
        else:
            st.success("📖 **Preview Mode** - Content is ready for download")
    
    with col3:
        # Word count display
        word_count = len(st.session_state.generated_content.split())
        st.metric("Words", word_count)
    
    # Display content based on mode
    if st.session_state.edit_mode:
        # Edit mode - show text area with better styling
        with st.form("edit_content_form"):
            st.markdown("#### ✏️ Edit Your Paper Content")
            edited_content = st.text_area(
                "Paper Content",
                value=st.session_state.generated_content,
                height=600,
                help="Make your edits to the generated content. The PDF will be updated with your changes when you save.",
                placeholder="Your paper content will appear here..."
            )
            
            # Show character count
            char_count = len(edited_content)
            st.caption(f"Characters: {char_count:,}")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                save_button = st.form_submit_button("💾 Save Changes", type="primary")
            with col2:
                cancel_button = st.form_submit_button("❌ Cancel")
            with col3:
                # Preview button to see changes without saving
                preview_button = st.form_submit_button("👁️ Preview Changes")
            
            if save_button:
                st.session_state.generated_content = edited_content
                st.session_state.content_dict = parse_generated_content(edited_content)
                st.session_state.content_dict['title'] = st.session_state.paper_title
                st.session_state.edit_mode = False
                st.success("✅ Content updated successfully! PDF has been regenerated with your changes.")
                st.rerun()
            
            if cancel_button:
                st.session_state.edit_mode = False
                st.rerun()
            
            if preview_button:
                st.session_state.edit_mode = False
                st.session_state.generated_content = edited_content
                st.session_state.content_dict = parse_generated_content(edited_content)
                st.session_state.content_dict['title'] = st.session_state.paper_title
                st.rerun()
    else:
        # Preview mode - show formatted content with better styling
        st.markdown("#### 📖 Paper Preview")
        with st.expander("📄 View Paper Content", expanded=True):
            st.markdown(st.session_state.generated_content)

def provide_download_buttons():
    """Provide download buttons for the current content"""
    if not st.session_state.content_dict:
        return
    
    st.markdown("## 📥 Download Options")
    
    # Show current content status
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sections", len([k for k, v in st.session_state.content_dict.items() if v and k != 'title']))
    with col2:
        word_count = len(st.session_state.generated_content.split())
        st.metric("Words", word_count)
    with col3:
        char_count = len(st.session_state.generated_content)
        st.metric("Characters", f"{char_count:,}")
    
    # Generate PDF with current content
    try:
        with st.spinner("🔄 Generating PDF..."):
            pdf_buffer = create_ieee_pdf(
                st.session_state.content_dict, 
                "generated_paper.pdf", 
                st.session_state.custom_parameters
            )
        
        # Add download buttons for both formats
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📄 Download as Text",
                data=st.session_state.generated_content,
                file_name="generated_paper.txt",
                mime="text/plain",
                help="Download the paper content as a plain text file"
            )
        with col2:
            st.download_button(
                label="📋 Download as PDF",
                data=pdf_buffer,
                file_name="generated_paper.pdf",
                mime="application/pdf",
                help="Download the paper as a formatted PDF following IEEE standards"
            )
        
        # Show info about current state
        if st.session_state.edit_mode:
            st.info("💡 Make your edits above and click 'Save Changes' to update the downloadable PDF.")
        else:
            st.success("✅ PDF is ready for download with the current content!")
            
        # Add refresh PDF button
        if st.button("🔄 Refresh PDF", key="refresh_pdf_btn"):
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error generating PDF: {str(e)}")
        st.info("💡 Try editing the content and saving again, or regenerate the paper.")

if __name__ == "__main__":
    main() 