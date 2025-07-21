import google.generativeai as genai
from datetime import datetime
from .math_formatter import MathFormatter

class ContentGenerator:
    """Handles content generation for IEEE conference papers"""
    
    def __init__(self, api_key=None):
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.math_formatter = MathFormatter()
    
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
        
        # CRITICAL MATHEMATICAL NOTATION REQUIREMENTS:
        # 1. Use proper superscript notation: E^T for transpose, W_K^T for matrix transpose
        # 2. Use proper subscript notation: W_V, W_K, W_Q for different weight matrices
        # 3. Use proper Greek letter symbols: φ (phi), θ (theta), α (alpha), β (beta), γ (gamma), δ (delta), ε (epsilon), μ (mu), σ (sigma), λ (lambda)
        # 4. Use proper mathematical symbols: ⊙ (Hadamard product), ⊗ (tensor product), ← (assignment), ∈ (element of), ∑ (summation), ∏ (product), ∫ (integral), ∂ (partial derivative), ∇ (gradient)
        # 5. Use bold letters for vectors: **v**, **x**, **y**
        # 6. Use capital letters for matrices: **W**, **A**, **B**
        # 7. NEVER use black squares (■) or corrupted characters in place of mathematical symbols
        # 8. NEVER omit superscripts or subscripts
        # 9. NEVER use plain text for Greek letters when symbols are available
        # 10. Ensure all mathematical operations are clearly indicated
        
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
        6. Pay special attention to mathematical notation - ensure all equations use proper symbols and formatting.
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Format the response to ensure proper mathematical notation
            formatted_content = self.format_content_with_math(response.text)
            return formatted_content
        except Exception as e:
            raise Exception(f"Error generating content: {str(e)}")
    
    def format_content_with_math(self, content):
        """Format content to ensure proper mathematical notation"""
        return self.math_formatter.format_content_with_equations(content)
    
    def validate_equations_in_content(self, content):
        """Validate all equations in the content for proper mathematical notation"""
        lines = content.split('\n')
        validation_results = []
        
        for i, line in enumerate(lines, 1):
            if self.math_formatter._is_math_line(line):
                result = self.math_formatter.validate_equation(line)
                if result['issues'] or result['warnings']:
                    validation_results.append({
                        'line_number': i,
                        'line': line,
                        'issues': result['issues'],
                        'warnings': result['warnings'],
                        'formatted_line': result['formatted_equation']
                    })
        
        return validation_results
    
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
