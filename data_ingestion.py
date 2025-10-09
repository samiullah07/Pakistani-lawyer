"""
Pakistan Legal AI - Data Ingestion Module
Handles PDF parsing and document preprocessing
"""

import os
from pathlib import Path
from typing import List, Dict
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

class PDFProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )
    
    def load_pdf(self, pdf_path: str) -> List[Document]:
        """Load and extract text from a single PDF file"""
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            print(f"✅ Loaded {len(documents)} pages from {pdf_path}")
            return documents
        except Exception as e:
            print(f"❌ Error loading {pdf_path}: {str(e)}")
            return []
    
    def process_directory(self, pdf_directory: str) -> List[Document]:
        """Process all PDFs in a directory"""
        all_documents = []
        pdf_files = list(Path(pdf_directory).glob("*.pdf"))
        
        print(f"🔍 Found {len(pdf_files)} PDF files")
        
        for pdf_path in pdf_files:
            documents = self.load_pdf(str(pdf_path))
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    'source_file': pdf_path.name,
                    'document_type': 'legal_document'
                })
            all_documents.extend(documents)
        
        return all_documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into smaller chunks for better retrieval"""
        chunked_docs = self.text_splitter.split_documents(documents)
        print(f"📄 Created {len(chunked_docs)} chunks from {len(documents)} documents")
        return chunked_docs
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for better embedding"""
        # Remove excessive whitespace
        text = ' '.join(text.split())
        # Add any other preprocessing steps here
        return text
    
    def process_legal_documents(self, pdf_directory: str) -> List[Document]:
        """Main method to process all legal PDFs"""
        print("🚀 Starting PDF processing...")
        
        # Load all PDFs
        documents = self.process_directory(pdf_directory)
        
        if not documents:
            print("⚠️ No documents loaded!")
            return []
        
        # Clean text
        for doc in documents:
            doc.page_content = self.preprocess_text(doc.page_content)
        
        # Create chunks
        chunked_documents = self.chunk_documents(documents)
        
        print(f"✅ Processing complete! {len(chunked_documents)} chunks ready")
        return chunked_documents

if __name__ == "__main__":
    # Example usage
    processor = PDFProcessor()
    
    # Point this to your PDF directory
    pdf_dir = "Laws"  # Change this path
    
    if os.path.exists(pdf_dir):
        documents = processor.process_legal_documents(pdf_dir)
        print(f"Processed {len(documents)} document chunks")
    else:
        print(f"Directory {pdf_dir} not found. Please create it and add your PDF files.")