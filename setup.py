#!/usr/bin/env python3
"""
Setup script for Signature Recognition System
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Setup the Signature Recognition System"""
    print("🔧 Setting up Signature Recognition System...")
    print("="*50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create necessary directories
    directories = [
        "backend/uploads",
        "backend/models/trained_models",
        "data/templates",
        "data/test_signatures",
        "tests/test_backend",
        "tests/test_frontend"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Install Python dependencies
    if not run_command("pip install -r backend/requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Create .env file if it doesn't exist
    env_file = Path("backend/.env")
    env_example = Path("backend/env.example")
    
    if not env_file.exists() and env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("📄 Created .env file from template")
        print("⚠️  Please edit backend/.env file with your configuration")
    
    print("\n" + "="*50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit backend/.env file with your configuration")
    print("2. Run: python run_server.py")
    print("3. Open: http://localhost:8000")
    print("4. Open frontend/index.html in your browser")
    print("\n📚 Documentation:")
    print("- API Docs: http://localhost:8000/docs")
    print("- README.md for detailed instructions")

if __name__ == "__main__":
    main()
