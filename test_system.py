"""
Test script for Pakistan Legal AI
Verifies all components are working correctly
"""

import os
import sys
from pathlib import Path
import time

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import langchain
        import langchain_community
        import langchain_groq  
        import langchain_huggingface
        import faiss
        import streamlit
        import fastapi
        import uvicorn
        import requests
        from dotenv import load_dotenv
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_files_exist():
    """Test if all required files exist"""
    print("📁 Testing file structure...")
    
    required_files = [
        'data_ingestion.py',
        'vector_store.py', 
        'retriever.py',
        'agent.py',
        'api.py',
        'ui.py',
        'main.py',
        'requirements.txt',
        '.env'
    ]
    
    required_dirs = [
        'Laws',
        'legal_vector_store'
    ]
    
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    for dir in required_dirs:
        if not Path(dir).exists():
            missing_files.append(dir)
    
    if missing_files:
        print(f"❌ Missing files/directories: {missing_files}")
        return False
    else:
        print("✅ All required files and directories exist")
        return True

def test_pdf_documents():
    """Test if PDF documents exist"""
    print("📚 Testing PDF documents...")
    
    laws_dir = Path("Laws")
    pdf_files = list(laws_dir.glob("*.pdf"))
    
    if pdf_files:
        print(f"✅ Found {len(pdf_files)} PDF documents")
        for pdf in pdf_files[:5]:  # Show first 5
            print(f"  - {pdf.name}")
        if len(pdf_files) > 5:
            print(f"  - ... and {len(pdf_files) - 5} more")
        return True
    else:
        print("❌ No PDF documents found in Laws directory")
        return False

def test_vector_store():
    """Test if vector store is built"""
    print("🗂️ Testing vector store...")
    
    vector_dir = Path("legal_vector_store")
    if vector_dir.exists():
        faiss_file = vector_dir / "index.faiss"
        pkl_file = vector_dir / "index.pkl"
        
        if faiss_file.exists() and pkl_file.exists():
            print("✅ Vector store files exist")
            return True
        else:
            print("❌ Vector store files incomplete")
            return False
    else:
        print("❌ Vector store directory not found")
        return False

def test_api_keys():
    """Test if API keys are configured"""
    print("🔑 Testing API keys...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    groq_key = os.getenv('GROQ_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if groq_key:
        print("✅ GROQ API key found")
    else:
        print("⚠️ GROQ API key not found (system will use template responses)")
    
    if openai_key:
        print("✅ OpenAI API key found")
    else:
        print("⚠️ OpenAI API key not found")
    
    return True

def test_basic_functionality():
    """Test basic system functionality"""
    print("⚙️ Testing basic functionality...")
    
    try:
        # Test data ingestion
        from data_ingestion import PDFProcessor
        processor = PDFProcessor()
        print("✅ PDF processor initialized")
        
        # Test vector store
        from vector_store import VectorStore
        vs = VectorStore()
        print("✅ Vector store class initialized")
        
        # Test retriever
        from retriever import LegalRetriever, QueryClassifier
        classifier = QueryClassifier()
        print("✅ Query classifier initialized")
        
        # Test query classification
        test_query = "What is theft in Pakistan?"
        domain = classifier.classify_query(test_query)
        print(f"✅ Query classification works: '{test_query}' -> {domain}")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🇵🇰 Pakistan Legal AI - System Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("File Structure Test", test_files_exist), 
        ("PDF Documents Test", test_pdf_documents),
        ("Vector Store Test", test_vector_store),
        ("API Keys Test", test_api_keys),
        ("Basic Functionality Test", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if test_func():
            passed += 1
        
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is ready to use.")
        print("\n🚀 To start the system run:")
        print("   python start.py")
    else:
        print("⚠️ Some tests failed. Please fix the issues above.")
        
        if passed >= 4:  # Most critical tests passed
            print("\n💡 You can still try running the system:")
            print("   python start.py")

if __name__ == "__main__":
    main()
