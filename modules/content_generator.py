import google.generativeai as genai
from datetime import datetime

class ContentGenerator:
    """Handles content generation for IEEE conference papers"""
    
    def __init__(self, api_key=None):
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    def generate_paper_content(self, title, research_field, methodology, expected_results, additional_context="", custom_parameters=None):
        """Generate IEEE conference paper content based on inputs"""
        
        # Read instructions
        instructions = self._read_instructions()
        
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
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error generating content: {str(e)}")
    
    def parse_generated_content(self, content):
        """Parse generated content into sections"""
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
    
    def _read_instructions(self):
        """Read IEEE formatting instructions from file"""
        try:
            with open('instructions.txt', 'r') as file:
                return file.read()
        except FileNotFoundError:
            return "IEEE conference paper formatting guidelines"
        except Exception as e:
            raise Exception(f"Error reading instructions: {str(e)}") 