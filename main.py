"""
Pakistan Legal AI - Main Application
Connects all modules and provides a unified interface
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PakistanLegalAI:
    def __init__(self, pdf_directory: str = "Laws", vector_store_path: str = "legal_vector_store"):
        self.pdf_directory = pdf_directory
        self.vector_store_path = vector_store_path
        self.vector_store_initialized = False
        self.agent = None
        
        print("🚀 Pakistan Legal AI System Initializing...")
        self._initialize_system()
    
    def _initialize_system(self):
        """Initialize all components of the legal AI system"""
        try:
            # Check if vector store exists, if not create it
            if not os.path.exists(self.vector_store_path):
                print("📚 Vector store not found. Building from PDFs...")
                self._build_vector_store()
            else:
                print("✅ Vector store found and ready!")
                self.vector_store_initialized = True
            
            # Initialize the agent
            self._initialize_agent()
            print("🎯 Legal Agent initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error initializing system: {str(e)}")
            sys.exit(1)
    
    def _build_vector_store(self):
        """Build vector store from PDF documents"""
        try:
            from data_ingestion import PDFProcessor
            from vector_store import build_legal_vector_store
            
            # Process PDFs
            processor = PDFProcessor()
            
            if not os.path.exists(self.pdf_directory):
                print(f"⚠️ PDF directory '{self.pdf_directory}' not found.")
                print("Please create the directory and add your PDF files.")
                return
            
            documents = processor.process_legal_documents(self.pdf_directory)
            
            if not documents:
                print("❌ No documents processed. Please check your PDF files.")
                return
            
            # Build vector store
            build_legal_vector_store(documents, self.vector_store_path)
            self.vector_store_initialized = True
            print("✅ Vector store built successfully!")
            
        except Exception as e:
            print(f"❌ Error building vector store: {str(e)}")
            raise
    
    def _initialize_agent(self):
        """Initialize the legal agent with optional LLM"""
        try:
            from agent import create_legal_agent
            
            # Try to initialize with Groq LLM if available
            llm = None
            groq_api_key = os.getenv("GROQ_API_KEY")
            
            if groq_api_key:
                try:
                    from langchain_groq import ChatGroq
                    llm = ChatGroq(
                        model="llama-3.1-8b-instant",  # Fixed model name
                        temperature=0,
                        api_key=groq_api_key,
                        max_tokens=1000
                    )
                    print("🤖 LLM connected successfully!")
                except ImportError:
                    print("⚠️ langchain_groq not available, using template responses")
                except Exception as e:
                    print(f"⚠️ LLM initialization failed: {e}, using template responses")
            else:
                print("ℹ️  GROQ_API_KEY not found, using template responses")
            
            self.agent = create_legal_agent(llm=llm, vector_store_path=self.vector_store_path)
            
        except Exception as e:
            print(f"❌ Error initializing agent: {str(e)}")
            raise
    
    def ask_legal_question(self, question: str) -> str:
        """Ask a legal question and get a response"""
        if not self.agent:
            return "❌ Agent not initialized. Please check system setup."
        
        if not self.vector_store_initialized:
            return "❌ Vector store not available. Please build it first."
        
        try:
            return self.agent.process_legal_query(question)
        except Exception as e:
            return f"❌ Error processing question: {str(e)}"
    
    def search_laws(self, law_name: str, section: str = None) -> str:
        """Search for specific laws or sections"""
        try:
            from retriever import LegalRetriever
            
            retriever = LegalRetriever(self.vector_store_path)
            documents = retriever.search_specific_law(law_name, section)
            
            if not documents:
                return f"❌ No documents found for '{law_name}'"
            
            result = f"🔍 Found {len(documents)} documents for '{law_name}'"
            if section:
                result += f" section {section}"
            result += "\n\n"
            
            for i, doc in enumerate(documents, 1):
                result += f"--- Document {i} ---\n"
                result += f"Source: {doc.metadata.get('source_file', 'Unknown')}\n"
                result += f"Content: {doc.page_content[:300]}...\n\n"
            
            return result
            
        except Exception as e:
            return f"❌ Error searching laws: {str(e)}"
    
    def rebuild_vector_store(self):
        """Rebuild the vector store from PDFs"""
        print("🔄 Rebuilding vector store...")
        self._build_vector_store()
        self._initialize_agent()
        print("✅ Vector store rebuilt successfully!")

def main():
    """Main interactive interface"""
    legal_ai = PakistanLegalAI()
    
    print("\n" + "="*60)
    print("🇵🇰 Pakistan Legal AI System Ready!")
    print("="*60)
    print("Commands:")
    print("  - Ask any legal question")
    print("  - 'search law [law_name]' - Search specific law")
    print("  - 'search section [law_name] [section]' - Search law section")
    print("  - 'rebuild' - Rebuild vector store")
    print("  - 'quit' or 'exit' - Exit the system")
    print("="*60)
    
    while True:
        try:
            user_input = input("\n💬 Your legal question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Thank you for using Pakistan Legal AI!")
                break
            
            elif user_input.lower() == 'rebuild':
                legal_ai.rebuild_vector_store()
                continue
            
            elif user_input.lower().startswith('search law '):
                law_name = user_input[11:].strip()
                if law_name:
                    response = legal_ai.search_laws(law_name)
                    print(f"\n{response}")
                else:
                    print("❌ Please provide a law name")
                continue
            
            elif user_input.lower().startswith('search section '):
                parts = user_input[15:].strip().split()
                if len(parts) >= 2:
                    law_name = parts[0]
                    section = parts[1]
                    response = legal_ai.search_laws(law_name, section)
                    print(f"\n{response}")
                else:
                    print("❌ Please provide law name and section (e.g., 'search section PenalCode 302')")
                continue
            
            elif user_input:
                print("\n" + "🧠 Thinking..." + "\n")
                response = legal_ai.ask_legal_question(user_input)
                print(response)
            
            else:
                print("❌ Please enter a question or command")
                
        except KeyboardInterrupt:
            print("\n👋 Thank you for using Pakistan Legal AI!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()