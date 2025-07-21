#!/usr/bin/env python3
"""
Startup script for the IEEE Conference Paper Generator Flask API
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check for Google API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY environment variable is required")
        print("💡 Create a .env file with: GOOGLE_API_KEY=your_api_key_here")
        return False
    
    # Validate API key format (basic check)
    if len(api_key) < 10:
        print("⚠️  GOOGLE_API_KEY seems too short. Please check your API key.")
        return False
    
    print(f"✅ Google API key found (length: {len(api_key)} characters)")
    
    # Test API key with a simple call
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Hello")
        print("✅ Google API key is valid and working")
    except Exception as e:
        print(f"❌ Google API key test failed: {str(e)}")
        print("💡 Please check your API key and internet connection")
        return False
    
    # Check for required files
    required_files = ['instructions.txt']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    # Check for required modules
    try:
        from modules.math_formatter import MathFormatter
        from modules.content_generator import ContentGenerator
        print("✅ Math formatting modules loaded successfully")
    except ImportError as e:
        print(f"❌ Math formatting module import failed: {str(e)}")
        return False
    
    print("✅ All requirements met!")
    return True

def create_upload_folder():
    """Create upload folder if it doesn't exist"""
    upload_folder = 'uploads'
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"📁 Created upload folder: {upload_folder}")

def main():
    """Main startup function"""
    print("🚀 Starting IEEE Conference Paper Generator API")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Create upload folder
    create_upload_folder()
    
    # Import and run the app
    try:
        from app import app
        
        # Get configuration
        from config import get_config
        config = get_config()
        
        print(f"📊 API Configuration:")
        print(f"  - Environment: {os.getenv('FLASK_CONFIG', 'default')}")
        print(f"  - Debug Mode: {config.DEBUG}")
        print(f"  - API Version: {config.API_VERSION}")
        print(f"  - Max File Size: {config.MAX_CONTENT_LENGTH // (1024*1024)}MB")
        
        print(f"\n🌐 Starting server...")
        print(f"  - Local: http://localhost:5001")
        print(f"  - Health Check: http://localhost:5001/health")
        print(f"  - API Docs: Check README.md for endpoint documentation")
        
        print(f"\n💡 Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Run the app
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=config.DEBUG
        )
        
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Startup error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 