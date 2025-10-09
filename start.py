"""
Startup script for Pakistan Legal AI
Runs both API and UI servers
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_requirements():
    """Check if all required packages are installed"""
    try:
        import langchain
        import langchain_groq
        import langchain_huggingface
        import faiss
        import streamlit
        import fastapi
        import uvicorn
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def start_api_server():
    """Start the FastAPI server"""
    print("🚀 Starting API server...")
    return subprocess.Popen([
        sys.executable, "api.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def start_streamlit_app():
    """Start the Streamlit app"""
    print("🌐 Starting Streamlit UI...")
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "ui.py", 
        "--server.port=8501", "--server.headless=true"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main():
    print("🇵🇰 Pakistan Legal AI - Startup Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("api.py").exists() or not Path("ui.py").exists():
        print("❌ Please run this script from the project directory")
        return
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check if vector store exists
    if not Path("legal_vector_store").exists():
        print("⚠️ Vector store not found. Building from PDFs...")
        print("This may take a few minutes...")
        
        try:
            from main import PakistanLegalAI
            legal_ai = PakistanLegalAI()
        except Exception as e:
            print(f"❌ Error building vector store: {e}")
            return
    
    try:
        # Start API server
        api_process = start_api_server()
        
        # Wait a bit for API to start
        print("⏳ Waiting for API server to start...")
        time.sleep(3)
        
        # Start Streamlit app
        ui_process = start_streamlit_app()
        
        print("✅ Both servers started successfully!")
        print("📊 API Server: http://localhost:8000")
        print("🌐 Web Interface: http://localhost:8501")
        print("\nPress Ctrl+C to stop both servers")
        
        # Keep both processes running
        try:
            api_process.wait()
        except KeyboardInterrupt:
            print("\n⏹️ Stopping servers...")
            api_process.terminate()
            ui_process.terminate()
            print("👋 Servers stopped!")
            
    except Exception as e:
        print(f"❌ Error starting servers: {e}")

if __name__ == "__main__":
    main()
