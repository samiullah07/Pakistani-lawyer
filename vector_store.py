"""
Pakistan Legal AI - Vector Store Module
Handles FAISS vector database and embeddings
"""

import os
import pickle
from pathlib import Path
from typing import List, Optional
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

class VectorStore:
    def __init__(self, embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        """Initialize with multilingual embedding model for Urdu/English support"""
        self.embedding_model = embedding_model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},  # Change to 'cuda' if you have GPU
            encode_kwargs={'normalize_embeddings': True}
        )
        self.vector_store = None
        self.store_path = "legal_vector_store"  # Fixed path consistency
    
    def create_vector_store(self, documents: List[Document]) -> FAISS:
        """Create FAISS vector store from documents"""
        if not documents:
            raise ValueError("No documents provided for vector store creation")
        
        print(f"🔄 Creating embeddings for {len(documents)} documents...")
        
        # Create FAISS vector store
        self.vector_store = FAISS.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        print("✅ Vector store created successfully!")
        return self.vector_store
    
    def save_vector_store(self, path: str = None):
        """Save vector store to disk"""
        if not self.vector_store:
            raise ValueError("No vector store to save. Create one first.")
        
        save_path = path or self.store_path
        os.makedirs(save_path, exist_ok=True)
        
        # Save FAISS index
        self.vector_store.save_local(save_path)
        
        print(f"💾 Vector store saved to {save_path}")
    
    def load_vector_store(self, path: str = None) -> FAISS:
        """Load vector store from disk"""
        load_path = path or self.store_path
        
        if not os.path.exists(load_path):
            raise FileNotFoundError(f"Vector store not found at {load_path}")
        
        # Load FAISS index
        self.vector_store = FAISS.load_local(
            load_path,
            embeddings=self.embeddings,
            allow_dangerous_deserialization=True  # Only for local files you trust
        )
        
        print(f"📂 Vector store loaded from {load_path}")
        return self.vector_store
    
    def add_documents(self, documents: List[Document]):
        """Add new documents to existing vector store"""
        if not self.vector_store:
            raise ValueError("No vector store loaded. Create or load one first.")
        
        print(f"➕ Adding {len(documents)} new documents...")
        self.vector_store.add_documents(documents)
        print("✅ Documents added successfully!")
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """Search for similar documents"""
        if not self.vector_store:
            raise ValueError("No vector store loaded. Create or load one first.")
        
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def similarity_search_with_score(self, query: str, k: int = 5) -> List[tuple]:
        """Search with similarity scores"""
        if not self.vector_store:
            raise ValueError("No vector store loaded. Create or load one first.")
        
        results = self.vector_store.similarity_search_with_score(query, k=k)
        return results
    
    def get_store_info(self) -> dict:
        """Get information about the vector store"""
        if not self.vector_store:
            return {"status": "No vector store loaded"}
        
        return {
            "status": "Loaded",
            "total_vectors": self.vector_store.index.ntotal,
            "embedding_dimension": self.vector_store.index.d,
            "embedding_model": self.embedding_model
        }

def build_legal_vector_store(documents: List[Document], save_path: str = "legal_vector_store"):
    """Utility function to build and save legal vector store"""
    print("🏗️ Building legal document vector store...")
    
    # Initialize vector store
    vs = VectorStore()
    
    # Create vector store
    vector_store = vs.create_vector_store(documents)
    
    # Save to disk
    vs.save_vector_store(save_path)
    
    # Print info
    info = vs.get_store_info()
    print(f"📊 Vector Store Info: {info}")
    
    return vs

if __name__ == "__main__":
    # Example usage - import inside main to avoid circular imports
    from data_ingestion import PDFProcessor
    
    # Process PDFs first
    processor = PDFProcessor()
    pdf_dir = "Laws"
    
    if os.path.exists(pdf_dir):
        documents = processor.process_legal_documents(pdf_dir)
        
        if documents:
            # Build vector store
            vs = build_legal_vector_store(documents)
            
            # Test search
            test_query = "criminal law penalties"
            results = vs.similarity_search(test_query, k=3)
            
            print(f"\n🔍 Test search for '{test_query}':")
            for i, doc in enumerate(results, 1):
                print(f"{i}. {doc.page_content[:200]}...")
        else:
            print("No documents to process")
    else:
        print(f"Directory {pdf_dir} not found")