import re
from datetime import datetime

class InputValidator:
    """Handles input validation for the API"""
    
    def __init__(self):
        pass
    
    def validate_paper_inputs(self, title, research_field, methodology, expected_results):
        """Validate paper generation inputs and return validation status and messages"""
        errors = []
        warnings = []
        
        # Check for required fields
        if not title or title.strip() == "" or title.lower() in ["na", "n/a", "none", ""]:
            errors.append("Paper title is required")
        elif len(title.strip()) < 5:
            warnings.append("Paper title seems too short")
        elif len(title.strip()) > 200:
            warnings.append("Paper title seems too long")
        
        if not research_field or research_field.strip() == "" or research_field.lower() in ["na", "n/a", "none", ""]:
            errors.append("Research field is required")
        elif len(research_field.strip()) < 10:
            warnings.append("Research field description seems too brief")
        elif len(research_field.strip()) > 1000:
            warnings.append("Research field description seems too long")
        
        if not methodology or methodology.strip() == "" or methodology.lower() in ["na", "n/a", "none", ""]:
            errors.append("Methodology is required")
        elif len(methodology.strip()) < 10:
            warnings.append("Methodology description seems too brief")
        elif len(methodology.strip()) > 2000:
            warnings.append("Methodology description seems too long")
        
        if not expected_results or expected_results.strip() == "" or expected_results.lower() in ["na", "n/a", "none", ""]:
            errors.append("Expected results are required")
        elif len(expected_results.strip()) < 10:
            warnings.append("Expected results description seems too brief")
        elif len(expected_results.strip()) > 2000:
            warnings.append("Expected results description seems too long")
        
        # Additional validation checks
        if title and self._contains_suspicious_content(title):
            warnings.append("Title contains potentially inappropriate content")
        
        if research_field and self._contains_suspicious_content(research_field):
            warnings.append("Research field contains potentially inappropriate content")
        
        if methodology and self._contains_suspicious_content(methodology):
            warnings.append("Methodology contains potentially inappropriate content")
        
        if expected_results and self._contains_suspicious_content(expected_results):
            warnings.append("Expected results contain potentially inappropriate content")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'validated_at': datetime.now().isoformat()
        }
    
    def validate_pdf_upload(self, file):
        """Validate PDF file upload"""
        errors = []
        warnings = []
        
        if not file:
            errors.append("No file provided")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check file extension
        if not file.filename.lower().endswith('.pdf'):
            errors.append("Only PDF files are allowed")
        
        # Check file size (limit to 10MB)
        try:
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > 10 * 1024 * 1024:  # 10MB
                errors.append("File size exceeds 10MB limit")
            elif file_size < 1024:  # 1KB
                warnings.append("File seems very small, may not contain readable text")
        except Exception:
            warnings.append("Could not determine file size")
        
        # Check filename
        if file.filename and len(file.filename) > 255:
            warnings.append("Filename is very long")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'validated_at': datetime.now().isoformat()
        }
    
    def validate_custom_parameters(self, custom_parameters):
        """Validate custom parameters"""
        errors = []
        warnings = []
        
        if not custom_parameters:
            return {'valid': True, 'errors': errors, 'warnings': warnings}
        
        if not isinstance(custom_parameters, dict):
            errors.append("Custom parameters must be a dictionary")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Check for too many parameters
        if len(custom_parameters) > 20:
            warnings.append("Too many custom parameters (max 20 recommended)")
        
        # Check parameter values
        for param_name, param_value in custom_parameters.items():
            if param_value and len(str(param_value)) > 500:
                warnings.append(f"Parameter '{param_name}' value is very long")
            
            if param_value and self._contains_suspicious_content(str(param_value)):
                warnings.append(f"Parameter '{param_name}' contains potentially inappropriate content")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'validated_at': datetime.now().isoformat()
        }
    
    def validate_author_info(self, author_info):
        """Validate author information"""
        errors = []
        warnings = []
        
        if not author_info:
            return {'valid': True, 'errors': errors, 'warnings': warnings}
        
        if not isinstance(author_info, dict):
            errors.append("Author info must be a dictionary")
            return {'valid': False, 'errors': errors, 'warnings': warnings}
        
        # Validate email if provided
        if author_info.get('Email ID'):
            email = author_info['Email ID']
            if not self._is_valid_email(email):
                errors.append("Invalid email format")
        
        # Validate author name
        if author_info.get('Author Name'):
            name = author_info['Author Name']
            if len(name.strip()) < 2:
                warnings.append("Author name seems too short")
            elif len(name.strip()) > 100:
                warnings.append("Author name seems too long")
        
        # Validate institution
        if author_info.get('Institution/Organization'):
            institution = author_info['Institution/Organization']
            if len(institution.strip()) < 3:
                warnings.append("Institution name seems too short")
            elif len(institution.strip()) > 200:
                warnings.append("Institution name seems too long")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'validated_at': datetime.now().isoformat()
        }
    
    def _is_valid_email(self, email):
        """Check if email format is valid"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _contains_suspicious_content(self, text):
        """Check for potentially inappropriate content"""
        if not text:
            return False
        
        # Convert to lowercase for checking
        text_lower = text.lower()
        
        # List of potentially inappropriate words/phrases
        suspicious_patterns = [
            'hack', 'crack', 'illegal', 'unauthorized', 'malware', 'virus',
            'spam', 'phishing', 'fraud', 'scam', 'fake', 'counterfeit'
        ]
        
        # Check for suspicious patterns
        for pattern in suspicious_patterns:
            if pattern in text_lower:
                return True
        
        # Check for excessive repetition
        words = text.split()
        if len(words) > 10:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            # If any word appears more than 30% of the time
            max_repetition = max(word_counts.values()) if word_counts else 0
            if max_repetition > len(words) * 0.3:
                return True
        
        return False
    
    def sanitize_input(self, text):
        """Sanitize input text to prevent injection attacks"""
        if not text:
            return ""
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<script>', '</script>', 'javascript:', 'onload=', 'onerror=']
        sanitized = text
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Limit length
        if len(sanitized) > 5000:
            sanitized = sanitized[:5000]
        
        return sanitized.strip() 