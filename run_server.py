#!/usr/bin/env python3
"""
Signature Recognition System - Server Startup Script
Run this script to start the FastAPI server
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def main():
    """Start the FastAPI server"""
    print("🚀 Starting Signature Recognition System...")
    print("📁 Backend directory:", backend_dir)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("models/trained_models", exist_ok=True)
    
    print("✅ Directories created")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔧 Interactive API: http://localhost:8000/redoc")
    print("\n" + "="*50)
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        reload_dirs=["app"]
    )

if __name__ == "__main__":
    main()
