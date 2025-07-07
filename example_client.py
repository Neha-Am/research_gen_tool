#!/usr/bin/env python3
"""
Example client for the IEEE Conference Paper Generator Flask API
"""

import requests
import json
import time
from datetime import datetime

class IEEEConferencePaperClient:
    """Client for the IEEE Conference Paper Generator API"""
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self):
        """Check API health"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            return None
    
    def validate_inputs(self, title, research_field, methodology, expected_results):
        """Validate paper inputs"""
        data = {
            "title": title,
            "research_field": research_field,
            "methodology": methodology,
            "expected_results": expected_results
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/validate-inputs", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Validation failed: {e}")
            return None
    
    def generate_paper(self, title, research_field, methodology, expected_results, 
                      additional_context="", custom_parameters=None):
        """Generate IEEE conference paper content"""
        data = {
            "title": title,
            "research_field": research_field,
            "methodology": methodology,
            "expected_results": expected_results,
            "additional_context": additional_context,
            "custom_parameters": custom_parameters or {}
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/generate-paper", json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Paper generation failed: {e}")
            return None
    
    def upload_pdf(self, pdf_file_path):
        """Upload and analyze PDF file"""
        try:
            with open(pdf_file_path, 'rb') as f:
                files = {'file': f}
                response = self.session.post(f"{self.base_url}/api/upload-pdf", files=files)
                response.raise_for_status()
                return response.json()
        except FileNotFoundError:
            print(f"PDF file not found: {pdf_file_path}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"PDF upload failed: {e}")
            return None
    
    def generate_pdf(self, sections, author_info=None, output_file=None):
        """Generate PDF from content sections"""
        data = {
            "sections": sections,
            "author_info": author_info or {}
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/generate-pdf", json=data)
            response.raise_for_status()
            
            if output_file:
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                print(f"PDF saved to: {output_file}")
            
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"PDF generation failed: {e}")
            return None
    
    def get_stats(self):
        """Get API usage statistics"""
        try:
            response = self.session.get(f"{self.base_url}/api/stats")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Stats retrieval failed: {e}")
            return None
    
    def reset_stats(self):
        """Reset API usage statistics"""
        try:
            response = self.session.post(f"{self.base_url}/api/reset-stats")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Stats reset failed: {e}")
            return None

def main():
    """Example usage of the client"""
    print("🚀 IEEE Conference Paper Generator API Client Example")
    print("=" * 60)
    
    # Initialize client
    client = IEEEConferencePaperClient()
    
    # Check API health
    print("1. Checking API health...")
    health = client.health_check()
    if health:
        print(f"✅ API is healthy: {health['status']} (v{health['version']})")
    else:
        print("❌ API is not responding. Make sure it's running.")
        return
    
    # Validate inputs
    print("\n2. Validating inputs...")
    validation = client.validate_inputs(
        title="Machine Learning in Healthcare",
        research_field="Healthcare AI and machine learning applications for medical diagnosis",
        methodology="Deep learning approach using convolutional neural networks",
        expected_results="Improved accuracy in disease detection and patient outcomes"
    )
    
    if validation:
        if validation['valid']:
            print("✅ Inputs are valid")
            if validation['warnings']:
                print(f"⚠️  Warnings: {validation['warnings']}")
        else:
            print(f"❌ Validation failed: {validation['errors']}")
            return
    
    # Generate paper content
    print("\n3. Generating paper content...")
    paper_result = client.generate_paper(
        title="Machine Learning Applications in Healthcare",
        research_field="Healthcare AI and machine learning for medical diagnosis and treatment planning",
        methodology="Deep learning approach using convolutional neural networks and transfer learning techniques",
        expected_results="Improved accuracy in disease detection, reduced diagnosis time, and better patient outcomes",
        custom_parameters={
            "Author Name": "Dr. John Smith",
            "Email ID": "john.smith@university.edu",
            "Institution/Organization": "University of Technology",
            "Dataset Size": "10,000 medical images",
            "Evaluation Metrics": "Accuracy, Precision, Recall, F1-Score"
        }
    )
    
    if paper_result:
        print(f"✅ Paper generated successfully!")
        print(f"📊 Word count: {paper_result['word_count']}")
        print(f"📊 Character count: {paper_result['character_count']}")
        
        # Show sections
        sections = paper_result['sections']
        print(f"📄 Generated sections:")
        for section, content in sections.items():
            if content and content != f"[{section.title()} content will be generated]":
                preview = content[:100] + "..." if len(content) > 100 else content
                print(f"  - {section}: {preview}")
        
        # Generate PDF
        print("\n4. Generating PDF...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        pdf_file = f"generated_paper_{timestamp}.pdf"
        
        author_info = {
            "Author Name": "Dr. John Smith",
            "Email ID": "john.smith@university.edu",
            "Institution/Organization": "University of Technology"
        }
        
        pdf_content = client.generate_pdf(sections, author_info, pdf_file)
        if pdf_content:
            print(f"✅ PDF generated successfully: {pdf_file}")
        
        # Get API statistics
        print("\n5. Getting API statistics...")
        stats = client.get_stats()
        if stats:
            print(f"📊 Total API calls: {stats['summary']['total_calls']}")
            print(f"📅 Today's calls: {stats['summary']['today_calls']}")
            print(f"💰 Estimated cost: ${stats['summary']['estimated_cost']['total_cost_usd']}")
            
            if stats['function_breakdown']:
                print(f"📈 Function breakdown:")
                for func, count in stats['function_breakdown'].items():
                    print(f"  - {func}: {count} calls")
    
    print("\n" + "=" * 60)
    print("✅ Example completed!")

if __name__ == "__main__":
    main() 