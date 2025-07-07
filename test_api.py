#!/usr/bin/env python3
"""
Test script for the IEEE Conference Paper Generator Flask API
"""

import requests
import json
import time
from datetime import datetime

# API base URL
BASE_URL = "http://localhost:5001"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False

def test_validate_inputs():
    """Test input validation endpoint"""
    print("\n🔍 Testing input validation...")
    
    # Test valid inputs
    valid_data = {
        "title": "Machine Learning Applications in Healthcare",
        "research_field": "Healthcare AI and machine learning for medical diagnosis",
        "methodology": "Deep learning approach using convolutional neural networks",
        "expected_results": "Improved accuracy in disease detection and patient outcomes"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/validate-inputs", json=valid_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Validation passed: {data['valid']}")
            if data['warnings']:
                print(f"⚠️  Warnings: {data['warnings']}")
            return True
        else:
            print(f"❌ Validation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Validation error: {str(e)}")
        return False

def test_generate_paper():
    """Test paper generation endpoint"""
    print("\n🔍 Testing paper generation...")
    
    data = {
        "title": "Machine Learning Applications in Healthcare",
        "research_field": "Healthcare AI and machine learning for medical diagnosis and treatment planning",
        "methodology": "Deep learning approach using convolutional neural networks and transfer learning techniques",
        "expected_results": "Improved accuracy in disease detection, reduced diagnosis time, and better patient outcomes",
        "custom_parameters": {
            "Author Name": "Dr. John Smith",
            "Email ID": "john.smith@university.edu",
            "Institution/Organization": "University of Technology",
            "Dataset Size": "10,000 medical images",
            "Evaluation Metrics": "Accuracy, Precision, Recall, F1-Score"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/generate-paper", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Paper generated successfully!")
            print(f"📊 Word count: {result['word_count']}")
            print(f"📊 Character count: {result['character_count']}")
            print(f"📅 Generated at: {result['generated_at']}")
            
            # Print sections
            sections = result['sections']
            print(f"📄 Sections generated:")
            for section, content in sections.items():
                if content and content != f"[{section.title()} content will be generated]":
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"  - {section}: {preview}")
            
            return result
        else:
            print(f"❌ Paper generation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Paper generation error: {str(e)}")
        return None

def test_generate_pdf(paper_result):
    """Test PDF generation endpoint"""
    if not paper_result:
        print("\n⚠️  Skipping PDF generation (no paper content)")
        return False
    
    print("\n🔍 Testing PDF generation...")
    
    data = {
        "sections": paper_result['sections'],
        "author_info": {
            "Author Name": "Dr. John Smith",
            "Email ID": "john.smith@university.edu",
            "Institution/Organization": "University of Technology"
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/generate-pdf", json=data)
        if response.status_code == 200:
            # Save PDF to file
            filename = f"generated_paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"✅ PDF generated successfully: {filename}")
            return True
        else:
            print(f"❌ PDF generation failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ PDF generation error: {str(e)}")
        return False

def test_api_stats():
    """Test API statistics endpoint"""
    print("\n🔍 Testing API statistics...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ API stats retrieved:")
            print(f"📊 Total calls: {stats['summary']['total_calls']}")
            print(f"📅 Today's calls: {stats['summary']['today_calls']}")
            print(f"💰 Estimated cost: ${stats['summary']['estimated_cost']['total_cost_usd']}")
            
            if stats['function_breakdown']:
                print(f"📈 Function breakdown:")
                for func, count in stats['function_breakdown'].items():
                    print(f"  - {func}: {count} calls")
            
            return True
        else:
            print(f"❌ Stats retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stats retrieval error: {str(e)}")
        return False

def run_all_tests():
    """Run all API tests"""
    print("🚀 Starting IEEE Conference Paper Generator API Tests")
    print("=" * 60)
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed. Make sure the API is running on port 5001.")
        return
    
    # Test input validation
    test_validate_inputs()
    
    # Test paper generation
    paper_result = test_generate_paper()
    
    # Test PDF generation
    test_generate_pdf(paper_result)
    
    # Test API stats
    test_api_stats()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")

if __name__ == "__main__":
    run_all_tests() 