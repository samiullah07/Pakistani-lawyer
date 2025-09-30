"""
Pakistan Legal AI - Retriever Module
Handles similarity search and context retrieval
"""

from typing import List, Dict, Tuple
from langchain.schema import Document

class LegalRetriever:
    def __init__(self, vector_store_path: str = "legal_vector_store"):
        """Initialize retriever with vector store"""
        # Import here to avoid circular imports
        from vector_store import VectorStore
        self.vector_store = VectorStore()
        try:
            self.vector_store.load_vector_store(vector_store_path)
            print("✅ Vector store loaded for retrieval")
        except FileNotFoundError:
            print(f"❌ Vector store not found at {vector_store_path}")
            print("Please run vector_store.py first to create the index")
            self.vector_store.vector_store = None
    
    def retrieve_relevant_docs(self, query: str, k: int = 5, score_threshold: float = 0.0) -> List[Document]:
        """Retrieve relevant legal documents for a query"""
        if not self.vector_store.vector_store:
            return []
        
        # Get documents with scores (FAISS returns distances, lower is better)
        docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
        
        # Filter by score threshold if specified (convert distance to similarity)
        if score_threshold > 0:
            # Since FAISS returns distances, we want documents with distance <= threshold
            filtered_docs = [doc for doc, score in docs_with_scores if score <= score_threshold]
        else:
            filtered_docs = [doc for doc, score in docs_with_scores]
        
        print(f"🔍 Retrieved {len(filtered_docs)} relevant documents for query: {query[:50]}...")
        return filtered_docs
    
    def retrieve_by_legal_domain(self, query: str, domain: str = None, k: int = 5) -> List[Document]:
        """Retrieve documents with domain-specific enhancement"""
        
        # Enhance query based on legal domain
        enhanced_query = self.enhance_query_for_domain(query, domain)
        
        return self.retrieve_relevant_docs(enhanced_query, k=k)
    
    # In retriever.py - enhance query enhancement
    def enhance_query_for_domain(self, query: str, domain: str = None) -> str:
        """Enhance query based on legal domain"""
        domain_keywords = {
            "criminal": "criminal law penal code PPC 302 304 murder manslaughter",
            "police_misconduct": "police officer misconduct assault slap beat public humiliation Pakistan Penal Code PPC 355 356 357 Police Order 2002 human rights",
            "civil": "civil law contract property dispute",
            "family": "family law marriage divorce custody inheritance",
            "commercial": "commercial law business contract trade",
            "constitutional": "constitution fundamental rights"
        }
        
        if domain and domain.lower() in domain_keywords:
            enhanced = f"{query} {domain_keywords[domain.lower()]}"
            return enhanced
        
        return query
    
    def get_context_for_legal_advice(self, query: str, max_context_length: int = 3000) -> Dict[str, any]:
        """Get structured context for legal advice generation"""
        
        # Retrieve relevant documents
        relevant_docs = self.retrieve_relevant_docs(query, k=5)
        
        if not relevant_docs:
            return {
                "context": "No relevant legal documents found",
                "sources": [],
                "confidence": "low"
            }
        
        # Build context string
        context_parts = []
        sources = []
        current_length = 0
        
        for doc in relevant_docs:
            doc_text = doc.page_content.strip()
            
            # Check if adding this document would exceed max length
            if current_length + len(doc_text) > max_context_length:
                break
            
            context_parts.append(doc_text)
            sources.append({
                "source_file": doc.metadata.get("source_file", "Unknown"),
                "page": doc.metadata.get("page", "Unknown"),
                "content_preview": doc_text[:100] + "..." if len(doc_text) > 100 else doc_text
            })
            
            current_length += len(doc_text)
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Determine confidence based on number of relevant docs
        confidence = "high" if len(relevant_docs) >= 3 else "medium" if len(relevant_docs) >= 1 else "low"
        
        return {
            "context": context,
            "sources": sources,
            "confidence": confidence,
            "total_docs_found": len(relevant_docs)
        }
    
    def search_specific_law(self, law_name: str, section: str = None) -> List[Document]:
        """Search for specific law or section"""
        if section:
            query = f"{law_name} section {section}"
        else:
            query = law_name
        
        return self.retrieve_relevant_docs(query, k=3)
    
    def find_similar_cases(self, case_description: str, k: int = 5) -> List[Document]:
        """Find similar legal cases or precedents"""
        enhanced_query = f"case precedent similar {case_description}"
        return self.retrieve_relevant_docs(enhanced_query, k=k)

# In retriever.py - enhance the QueryClassifier
class QueryClassifier:
    """Classify legal queries into domains"""
    
    def __init__(self):
        self.domain_keywords = {
            "criminal": [
                "crime", "criminal", "theft", "murder", "assault", "fraud", 
                "punishment", "jail", "prison", "police", "arrest", "bail",
                "penal code", "offense", "robbery", "kidnapping", "shot", "shooting",
                "accidental", "underground", "surrender", "FIR", "investigation",
                "homicide", "manslaughter", "weapon", "firearm"
            ],
            "police_misconduct": [
                "police", "officer", "cop", "slap", "beat", "harass", "misconduct",
                "abuse", "brutality", "assault", "public", "humiliate", "rights",
                "complaint", "police station", "uniform", "authority"
            ],
            "civil": [
                "contract", "property", "land", "dispute", "damages", 
                "compensation", "breach", "agreement", "civil suit",
                "tort", "negligence", "liability"
            ],
            "family": [
                "marriage", "divorce", "custody", "inheritance", "family",
                "spouse", "children", "will", "property inheritance",
                "maintenance", "alimony", "nikah", "khula", "mahr",
                "second marriage", "multiple wives", "polygamy", "permission",
                "first wife", "husband", "wife", "marriage contract",
                "muslim family law", "family laws ordinance"
            ],
            "commercial": [
                "business", "trade", "commercial", "company", "corporate",
                "contract", "agreement", "partnership", "liability",
                "investment", "shares", "stock", "merger", "acquisition"
            ],
            "constitutional": [
                "constitution", "fundamental rights", "freedom", "equality",
                "discrimination", "citizen", "state", "government", "law",
                "judiciary", "parliament", "amendment"
            ],
            
        }
    
    def classify_query(self, query: str) -> str:
        """Classify query into legal domain"""
        query_lower = query.lower()
        
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            domain_scores[domain] = score
        
        if max(domain_scores.values()) > 0:
            return max(domain_scores, key=domain_scores.get)
        else:
            return "general"

if __name__ == "__main__":
    # Test the retriever
    retriever = LegalRetriever()
    classifier = QueryClassifier()
    
    # Test queries
    test_queries = [
        "What is the punishment for theft in Pakistan?",
        "How to file for divorce in Pakistan?",
        "What are the requirements for starting a business?",
        "Property inheritance laws in Pakistan"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        
        # Classify query
        domain = classifier.classify_query(query)
        print(f"📂 Domain: {domain}")
        
        # Get context
        context_data = retriever.get_context_for_legal_advice(query)
        print(f"📄 Found {context_data['total_docs_found']} relevant documents")
        print(f"🎯 Confidence: {context_data['confidence']}")
        
        if context_data['sources']:
            print("📚 Sources:")
            for source in context_data['sources'][:2]:  # Show first 2 sources
                print(f"  - {source['source_file']}: {source['content_preview']}")