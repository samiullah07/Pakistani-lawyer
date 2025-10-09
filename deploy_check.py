"""
Deployment preparation script
Run this before deploying to ensure everything is ready
"""

import os
import sys
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    print("🔍 Checking required files...")
    
    required_files = [
        "api.py",
        "ui.py",
        "requirements.txt",
        "Procfile",
        "runtime.txt",
        ".gitignore",
        "DEPLOYMENT.md",
        "data_ingestion.py",
        "vector_store.py",
        "retriever.py",
        "agent.py",
        "lawyer_directory.py"
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
            print(f"  ❌ Missing: {file}")
        else:
            print(f"  ✅ Found: {file}")
    
    if missing:
        print(f"\n⚠️ Missing {len(missing)} required files!")
        return False
    
    print("\n✅ All required files present!")
    return True

def check_vector_store():
    """Check if vector store exists"""
    print("\n🗂️ Checking vector store...")
    
    vector_store_path = Path("legal_vector_store")
    
    if vector_store_path.exists():
        files = list(vector_store_path.glob("*"))
        if files:
            print(f"  ✅ Vector store found with {len(files)} files")
            return True
        else:
            print("  ❌ Vector store folder empty")
            return False
    else:
        print("  ❌ Vector store not found")
        print("  💡 Run: python vector_store.py to build it")
        return False

def check_laws_folder():
    """Check if Laws folder has PDFs"""
    print("\n📚 Checking Laws folder...")
    
    laws_path = Path("Laws")
    
    if laws_path.exists():
        pdfs = list(laws_path.glob("*.pdf"))
        if pdfs:
            print(f"  ✅ Found {len(pdfs)} PDF files")
            for pdf in pdfs[:5]:  # Show first 5
                print(f"    - {pdf.name}")
            if len(pdfs) > 5:
                print(f"    - ... and {len(pdfs) - 5} more")
            return True
        else:
            print("  ❌ No PDF files found in Laws folder")
            return False
    else:
        print("  ❌ Laws folder not found")
        return False

def check_env_file():
    """Check .env file for API keys"""
    print("\n🔑 Checking environment variables...")
    
    env_path = Path(".env")
    
    if env_path.exists():
        print("  ✅ .env file found")
        
        with open(env_path, 'r') as f:
            content = f.read()
            
        has_groq = "GROQ_API_KEY" in content
        has_openai = "OPENAI_API_KEY" in content
        
        if has_groq:
            print("  ✅ GROQ_API_KEY configured")
        else:
            print("  ⚠️ GROQ_API_KEY not found")
            
        if has_openai:
            print("  ✅ OPENAI_API_KEY configured")
        else:
            print("  ⚠️ OPENAI_API_KEY not found")
            
        return has_groq or has_openai
    else:
        print("  ⚠️ .env file not found")
        print("  💡 API keys should be added in deployment platform")
        return True  # OK for deployment

def generate_deployment_checklist():
    """Generate checklist for deployment"""
    print("\n" + "="*60)
    print("📋 DEPLOYMENT CHECKLIST")
    print("="*60)
    
    checklist = [
        ("✅" if check_files() else "❌", "All required files present"),
        ("✅" if check_vector_store() else "❌", "Vector store built"),
        ("✅" if check_laws_folder() else "❌", "PDF files available"),
        ("✅" if check_env_file() else "⚠️", "Environment variables configured"),
    ]
    
    print("\n📝 Summary:")
    for status, item in checklist:
        print(f"  {status} {item}")
    
    all_ready = all(status == "✅" for status, _ in checklist)
    
    if all_ready:
        print("\n🎉 ALL CHECKS PASSED! Ready for deployment!")
        print("\n🚀 Next Steps:")
        print("  1. Create GitHub repository")
        print("  2. Push code: git init && git add . && git commit -m 'Initial commit'")
        print("  3. Deploy on Streamlit Cloud: https://share.streamlit.io")
        print("  4. Deploy API on Render: https://render.com")
        print("\n📖 See DEPLOYMENT.md for detailed instructions")
    else:
        print("\n⚠️ Some issues found. Please fix them before deploying.")
        print("📖 See DEPLOYMENT.md for help")

if __name__ == "__main__":
    print("🇵🇰 Pakistan Legal AI - Deployment Preparation")
    print("="*60)
    
    generate_deployment_checklist()
