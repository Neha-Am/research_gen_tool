#!/usr/bin/env python3
"""
Setup script for the IEEE Conference Paper Generator Flask API
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path('../../Desktop/Flaskkk-resgen-finalversion/.env')
    
    if env_file.exists():
        print("📄 .env file already exists")
        return True
    
    print("📄 Creating .env file...")
    
    env_content = """# IEEE Conference Paper Generator API Configuration

# Google Gemini API Key (Required)
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_google_api_key_here

# Flask Configuration (Optional)
FLASK_CONFIG=development
FLASK_DEBUG=True

# Security (Optional - change in production)
SECRET_KEY=your-secret-key-change-in-production
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully")
        print("💡 Please edit .env file and add your Google API key")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {str(e)}")
        return False

def check_api_key():
    """Check if API key is configured"""
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key or api_key == 'your_google_api_key_here':
        print("❌ Google API key not configured")
        print("💡 Please edit .env file and add your Google API key")
        print("🔗 Get your API key from: https://makersuite.google.com/app/apikey")
        return False
    
    print(f"✅ Google API key configured (length: {len(api_key)} characters)")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully")
            return True
        else:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing dependencies: {str(e)}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['uploads', 'logs']
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir()
            print(f"📁 Created directory: {directory}")
        else:
            print(f"📁 Directory exists: {directory}")

def main():
    """Main setup function"""
    print("🚀 IEEE Conference Paper Generator API Setup")
    print("=" * 50)
    
    # Create .env file
    if not create_env_file():
        return
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("💡 You can manually install dependencies with: pip install -r requirements.txt")
    
    # Check API key
    if not check_api_key():
        print("\n📋 Next steps:")
        print("1. Edit .env file and add your Google API key")
        print("2. Run: python run.py")
        print("3. Test with: python test_api.py")
        return
    
    print("\n✅ Setup completed successfully!")
    print("\n🚀 You can now run the API:")
    print("   python run.py")
    print("\n🧪 Test the API:")
    print("   python test_api.py")

if __name__ == "__main__":
    main() 