import PyPDF2
import google.generativeai as genai
from io import BytesIO
import os
from datetime import datetime

class PDFHandler:
    """Handles PDF file operations including text extraction and content analysis"""
    
    def __init__(self, api_key=None):
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def extract_text_from_pdf(self, uploaded_file):
        """Extract text from uploaded PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def analyze_pdf_content(self, pdf_text):
        """Analyze PDF content and extract relevant information for paper generation"""
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
            response = self.model.generate_content(analysis_prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error analyzing PDF content: {str(e)}")
    
    def parse_analysis_result(self, analysis_text):
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
    
    def read_instructions(self):
        """Read IEEE formatting instructions from file"""
        try:
            with open('instructions.txt', 'r') as file:
                return file.read()
        except FileNotFoundError:
            return "IEEE conference paper formatting guidelines"
        except Exception as e:
            raise Exception(f"Error reading instructions: {str(e)}")
    
    def read_pdf_template(self):
        """Read the IEEE conference template PDF"""
        try:
            with open('ieee-conference-template.pdf', 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except FileNotFoundError:
            return ""
        except Exception as e:
            raise Exception(f"Error reading template PDF: {str(e)}") 