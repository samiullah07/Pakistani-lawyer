"""
Pakistan Legal AI - FastAPI Backend
REST API endpoints for legal advice system
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime
import logging
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pakistan Legal AI API",
    description="AI-powered legal advice system for Pakistani law",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for services
legal_agent = None
retriever = None
classifier = None

# Pydantic models
class LegalQuery(BaseModel):
    query: str
    session_id: Optional[str] = None

class LegalResponse(BaseModel):
    query: str
    domain: str
    analysis: str
    recommendations: str
    lawyer_type: str
    confidence: str
    sources: List[Dict]
    timestamp: str
    session_id: Optional[str] = None

class ChatMessage(BaseModel):
    message: str
    is_user: bool
    timestamp: str

class ChatSession(BaseModel):
    session_id: str
    title: str
    messages: List[ChatMessage]
    created_at: str

class HealthResponse(BaseModel):
    status: str
    message: str
    vector_store_status: str
    timestamp: str

# Chat storage (in production, use a database)
chat_sessions = {}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global legal_agent, retriever, classifier
    
    try:
        logger.info("🚀 Starting Pakistan Legal AI API...")
        
        # Initialize services
        from agent import create_legal_agent
        from retriever import LegalRetriever, QueryClassifier
        
        legal_agent = create_legal_agent()
        retriever = LegalRetriever()
        classifier = QueryClassifier()
        
        logger.info("✅ Services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {str(e)}")

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health"""
    vector_status = "Available" if retriever and retriever.vector_store.vector_store else "Not Available"
    
    return HealthResponse(
        status="healthy" if legal_agent else "degraded",
        message="Pakistan Legal AI API is running",
        vector_store_status=vector_status,
        timestamp=datetime.now().isoformat()
    )

# Main legal query endpoint
@app.post("/legal-advice")
async def get_legal_advice(query: LegalQuery):
    """Process legal query and return advice"""
    if not legal_agent:
        raise HTTPException(status_code=503, detail="Legal agent not available")
    
    try:
        logger.info(f"Processing query: {query.query[:50]}...")
        
        # Process the query
        response = legal_agent.process_legal_query(query.query)
        
        # Extract components from response
        domain = classifier.classify_query(query.query) if classifier else "general"
        
        # Parse response sections
        analysis = ""
        recommendations = ""
        lawyer_type = ""
        
        if "### Legal Analysis" in response:
            sections = response.split("###")
            for section in sections:
                if section.strip().startswith("Legal Analysis"):
                    analysis = section.replace("Legal Analysis", "").strip()
                elif section.strip().startswith("Recommendations"):
                    recommendations = section.replace("Recommendations", "").strip()
                elif section.strip().startswith("Legal Representation"):
                    lawyer_type = section.replace("Legal Representation", "").strip()
        
        if not analysis:
            analysis = response
        
        # Get sources
        sources = []
        if retriever:
            context_data = retriever.get_context_for_legal_advice(query.query)
            sources = context_data.get("sources", [])
            confidence = context_data.get("confidence", "medium")
        else:
            confidence = "medium"
        
        # Store in chat session if session_id provided
        if query.session_id:
            store_chat_message(query.session_id, query.query, response)
        
        return {
            "query": query.query,
            "domain": domain,
            "analysis": analysis,
            "recommendations": recommendations,
            "lawyer_type": lawyer_type,
            "confidence": confidence,
            "sources": sources,
            "timestamp": datetime.now().isoformat(),
            "session_id": query.session_id
        }
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoints
@app.post("/chat/message")
async def send_chat_message(query: LegalQuery):
    """Send a chat message and get response"""
    if not legal_agent:
        raise HTTPException(status_code=503, detail="Legal agent not available")
    
    try:
        # Generate session ID if not provided
        session_id = query.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Check if this is a greeting, identity question, lawyer search, or out-of-domain query
        special_response = handle_special_queries(query.query)
        
        # If not a special query, check if it's a lawyer search
        if not special_response:
            from lawyer_directory import handle_lawyer_search_query
            special_response = handle_lawyer_search_query(query.query)
        
        if special_response:
            # Store messages for special responses
            store_chat_message(session_id, query.query, special_response)
            
            return {
                "response": special_response,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        
        # Process legal query normally
        response = legal_agent.process_legal_query(query.query)
        
        # Clean response to make it natural and professional
        clean_response = clean_ai_response(response)
        
        # Check if the response seems to be about a non-legal topic
        if is_non_legal_response(clean_response, query.query):
            clean_response = get_out_of_domain_response(query.query)
        
        # Store messages
        store_chat_message(session_id, query.query, clean_response)
        
        return {
            "response": clean_response,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/sessions")
async def get_chat_sessions():
    """Get all chat sessions"""
    sessions = []
    for session_id, session_data in chat_sessions.items():
        sessions.append({
            "session_id": session_id,
            "title": session_data.get("title", "Legal Query"),
            "created_at": session_data.get("created_at", datetime.now().isoformat()),
            "message_count": len(session_data.get("messages", []))
        })
    
    return {"sessions": sessions}

@app.get("/chat/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """Get specific chat session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return chat_sessions[session_id]

@app.delete("/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    del chat_sessions[session_id]
    return {"message": "Session deleted successfully"}

# Search endpoint
@app.post("/search")
async def search_documents(query: dict):
    """Search legal documents"""
    if not retriever:
        raise HTTPException(status_code=503, detail="Document retriever not available")
    
    try:
        search_query = query.get("query", "")
        max_results = query.get("max_results", 5)
        
        docs = retriever.retrieve_relevant_docs(search_query, k=max_results)
        
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content,
                "source": doc.metadata.get("source_file", "Unknown"),
                "page": doc.metadata.get("page", "Unknown")
            })
        
        return {"results": results, "total_found": len(docs)}
        
    except Exception as e:
        logger.error(f"Error in search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility functions
def detect_language(query: str) -> str:
    """Detect if query is in Urdu or English"""
    urdu_words = [
        'kya', 'hai', 'ho', 'hain', 'ka', 'ki', 'ke', 'mein', 'se', 'ko', 'ne', 'par', 'tak',
        'apko', 'aap', 'ap', 'tum', 'tumhe', 'main', 'hum', 'woh', 'yeh', 'is', 'us',
        'naam', 'kaun', 'kaise', 'kaisy', 'kahan', 'kab', 'kyun', 'kyu', 'pta', 'pata',
        'maloom', 'batao', 'bataiye', 'samjhao', 'madad', 'help', 'shukria', 'dhanyawad'
    ]
    
    query_words = query.lower().split()
    urdu_word_count = sum(1 for word in query_words if word in urdu_words)
    
    # If more than 30% words are Urdu, consider it Urdu
    if len(query_words) > 0 and (urdu_word_count / len(query_words)) > 0.3:
        return 'urdu'
    else:
        return 'english'

def handle_special_queries(query: str) -> str:
    """Handle greetings, identity questions, and special queries in detected language"""
    query_lower = query.lower().strip()
    detected_lang = detect_language(query)
    
    # Greetings (English and Urdu)
    greetings = [
        'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 
        'assalam alaikum', 'salam', 'adab', 'namaste'
    ]
    if any(greeting in query_lower for greeting in greetings) and len(query_lower) < 20:
        if detected_lang == 'urdu':
            return "Salam! Main aap ka Legal Assistant hun aur Pakistani qanoon mein mahir hun. Main aap ko qanooni masail, aap ke haqooq, aur qanooni procedures ke baare mein madad kar sakta hun. Kya koi qanooni sawal hai?"
        else:
            return "Hello! I'm your Legal Assistant, specialized in Pakistani law. I'm here to help you understand legal matters, your rights, and provide guidance on various legal issues in Pakistan. What legal question can I assist you with today?"
    
    # How are you questions (English and Urdu)
    how_are_you_phrases = [
        'how are you', 'how r u', 'how do you do', 'what\'s up',
        'ap kaisy ho', 'ap kaise ho', 'ap kaise hain', 'kaisy ho', 'kaise ho', 
        'kya hal hai', 'sab theek', 'ap ka kya haal hai', 'kia haal hai'
    ]
    if any(phrase in query_lower for phrase in how_are_you_phrases):
        if detected_lang == 'urdu':
            return "Main bilkul theek hun, puchne ke liye shukria! Main Pakistani qanoon ke baare mein aap ke sawalon ka jawab dene ke liye tayyar hun. Criminal law, civil law, family law, ya business regulations - kisi bhi qanooni masle mein madad kar sakta hun. Kya janna chahte hain?"
        else:
            return "I'm doing great, thank you for asking! I'm ready to help you with any questions about Pakistani law. Whether it's criminal law, civil matters, family law, or business regulations, I'm here to provide you with accurate legal guidance. What would you like to know?"
    
    # Identity questions (English and Urdu)
    identity_questions = [
        'who are you', 'what are you', 'who r u', 'what is your name', 'introduce yourself',
        'ap kaun ho', 'ap kya ho', 'ap kaun hain', 'tumhara naam kya hai', 'apna taraf karo',
        'tum kaun ho', 'aap kaun hain', 'apna parichay do'
    ]
    if any(question in query_lower for question in identity_questions):
        if detected_lang == 'urdu':
            return "Main aap ka Legal Assistant hun - Pakistani qanoon mein mahir ek AI system. Mere paas Pakistani legal documents ki mukammal maloomat hai jisme Constitution, Penal Code, Civil Procedure Code, aur doosre qanooni acts shamil hain. Main aap ko qanooni procedures, aap ke haqooq, crimes ki saza, aur qanooni masail mein rehnamai provide kar sakta hun."
        else:
            return "I'm your Legal Assistant - an AI-powered legal guidance system specialized in Pakistani law. I have comprehensive knowledge of Pakistani legal documents including the Constitution, Penal Code, Civil Procedure Code, and various other legal acts. I can help you understand legal procedures, your rights, penalties for various offenses, and guide you on what steps to take in legal matters."
    
    # Name questions (English and Urdu)
    name_questions = [
        'do you know my name', 'what is my name', 'whats my name', 'tell me my name',
        'apko mera naam pta hai', 'apko mera naam pata hai', 'mera naam kya hai', 
        'ap mera naam jantay ho', 'kya ap mera naam jante hain', 'tumhe mera naam pta hai',
        'apko mera naam maloom hai', 'mera naam bataiye'
    ]
    if any(question in query_lower for question in name_questions):
        if detected_lang == 'urdu':
            return "Main aap ki personal maloomat, jaise naam waghaira, access nahi kar sakta privacy aur security ke liye. Main sirf qanooni masail mein madad ke liye bana hun. Kya koi qanooni sawal hai jismein main aap ki madad kar sakun?"
        else:
            return "I don't have access to personal information about you, including your name, for privacy and security reasons. I'm designed to help with legal questions while keeping our conversations confidential. Is there a legal matter I can assist you with instead?"
    
    # Capability questions (English and Urdu)
    capability_questions = [
        'what can you do', 'what do you know', 'how can you help', 'what are your capabilities',
        'ap kya kar sakty ho', 'ap kya jantay ho', 'ap kaise madad kar sakty ho', 
        'aap ki kya salahiyat hain', 'kya kya kar sakte ho'
    ]
    if any(question in query_lower for question in capability_questions):
        if detected_lang == 'urdu':
            return "Main Pakistani qanoon mein mahir hun aur is mein aap ki madad kar sakta hun:\n\n• **Criminal Law** - Jurm, saza, aur qanooni procedures\n• **Civil Law** - Contract ke jhagde, property ke masail\n• **Family Law** - Shadi, talaq, custody, aur miraas ke haqooq\n• **Commercial Law** - Business registration aur commercial disputes\n• **Constitutional Law** - Bunyadi haqooq aur constitutional masail\n\nMain qanooni concepts samjha sakta hun, procedures mein rehnamai kar sakta hun, aur bataa sakta hun ke aap ko kis qism ke lawyer ki zarurat hai."
        else:
            return "I specialize in Pakistani law and can help you with:\n\n• **Criminal Law** - Understanding offenses, penalties, and legal procedures\n• **Civil Law** - Contract disputes, property matters, and civil procedures\n• **Family Law** - Marriage, divorce, custody, and inheritance rights\n• **Commercial Law** - Business registration, commercial disputes, and regulations\n• **Constitutional Law** - Fundamental rights and constitutional matters\n\nI can explain legal concepts, guide you through procedures, help you understand your rights, and recommend the type of legal representation you might need."
    
    # Thanks (English and Urdu)
    thanks_phrases = [
        'thank you', 'thanks', 'thank u', 'thx', 'shukria', 'dhanyawad', 
        'bohot shukria', 'bahut dhanyawad', 'shukar hai'
    ]
    if any(phrase in query_lower for phrase in thanks_phrases):
        if detected_lang == 'urdu':
            return "Koi baat nahi! Khushi hui ke madad kar saka. Agar koi aur qanooni sawal hai to beshak puchiye. Main hamesha aap ki qanooni rehnamai ke liye hazir hun."
        else:
            return "You're most welcome! I'm glad I could help. If you have any other legal questions or need clarification on anything, please don't hesitate to ask. I'm here whenever you need legal guidance."
    
    # General conversational questions (English and Urdu)
    general_conversation = [
        'kya kar rahe ho', 'kya kar rahi ho', 'what are you doing', 'kya haal hai',
        'kaise ho bhai', 'kya chal raha hai', 'whats going on', 'whats happening'
    ]
    if any(phrase in query_lower for phrase in general_conversation):
        if detected_lang == 'urdu':
            return "Main yahan Pakistani qanooni masail mein aap ki madad ke liye tayyar hun! Criminal law, civil disputes, family law, ya constitutional rights - kisi bhi qanooni masle mein rehnamai kar sakta hun. Kya koi legal sawal hai?"
        else:
            return "I'm here ready to help you with Pakistani legal matters! Whether you need guidance on criminal law, civil disputes, family law issues, or understanding your legal rights, I'm at your service. What legal question can I help you with?"
    
    return None

def is_non_legal_response(response: str, query: str) -> bool:
    """Check if the response indicates a non-legal topic"""
    query_lower = query.lower()
    response_lower = response.lower()
    
    # Check for non-legal topics in the query
    non_legal_topics = [
        'recipe', 'cooking', 'food', 'weather', 'sports', 'music', 'movie', 'entertainment',
        'technology', 'computer', 'programming', 'software', 'game', 'health', 'medicine',
        'doctor', 'travel', 'holiday', 'vacation', 'shopping', 'fashion', 'beauty',
        'fitness', 'exercise', 'diet', 'mathematics', 'science', 'physics', 'chemistry',
        'biology', 'history', 'geography', 'literature', 'art', 'painting', 'drawing'
    ]
    
    # If query contains non-legal topics and response seems generic
    if any(topic in query_lower for topic in non_legal_topics):
        return True
    
    # If response is very short and doesn't contain legal terms
    legal_indicators = ['law', 'legal', 'court', 'judge', 'penalty', 'offense', 'rights', 'act', 'section', 'constitution']
    if len(response) < 200 and not any(indicator in response_lower for indicator in legal_indicators):
        return True
    
    return False

def get_out_of_domain_response(query: str) -> str:
    """Return appropriate response for non-legal queries"""
    return f"I appreciate your question, but I'm specifically trained as a Legal Assistant for Pakistani law matters. I specialize in legal regulations, procedures, and rights under Pakistani law.\n\nI don't have specific information about '{query.strip()}' as it falls outside my legal expertise. However, I'd be happy to help you with any questions related to:\n\n• Criminal law and penalties\n• Civil disputes and procedures\n• Family law matters\n• Business and commercial law\n• Constitutional rights\n• Legal procedures and documentation\n\nIs there a legal matter I can assist you with instead?"

def store_chat_message(session_id: str, user_message: str, ai_response: str):
    """Store chat messages in session"""
    if session_id not in chat_sessions:
        # Create new session with title from first message
        title = user_message[:50] + "..." if len(user_message) > 50 else user_message
        chat_sessions[session_id] = {
            "session_id": session_id,
            "title": title,
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
    
    # Add messages
    timestamp = datetime.now().isoformat()
    chat_sessions[session_id]["messages"].extend([
        {
            "message": user_message,
            "is_user": True,
            "timestamp": timestamp
        },
        {
            "message": ai_response,
            "is_user": False,
            "timestamp": timestamp
        }
    ])

def clean_ai_response(response: str) -> str:
    """Clean AI response while preserving ALL legal content"""
    # Preserve the original response completely
    original_response = response
    
    # Only remove obvious AI preambles, keep ALL legal analysis
    ai_preambles_to_remove = [
        "Based on Pakistani law, here's what I found:\n\n",
        "According to Pakistani law,\n",
        "Based on the legal documents,\n"
    ]
    
    for preamble in ai_preambles_to_remove:
        response = response.replace(preamble, "")
    
    # Only remove sources section at the very end, keep all analysis
    if "Sources" in response:
        response = response.split("Sources")[0]
    
    if "Disclaimer:" in response:
        response = response.split("Disclaimer:")[0]
    
    # Clean up markdown but preserve ALL content
    response = response.replace("###", "")
    response = response.replace("##", "")
    
    # If response has structured sections, preserve them with better formatting
    if "Legal Analysis" in response:
        # Just clean up the formatting but keep ALL content
        sections = []
        current_content = ""
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                current_content += "\n"
                continue
                
            # Check if this is a section header
            if any(header in line for header in ["Legal Analysis", "Recommendations", "Legal Representation"]):
                # Save previous section with ALL its content
                if current_section and current_content.strip():
                    sections.append((current_section, current_content.strip()))
                
                # Start new section
                if "Legal Analysis" in line:
                    current_section = "Legal Analysis"
                elif "Recommendations" in line:
                    current_section = "Next Steps"
                elif "Legal Representation" in line:
                    current_section = "Legal Assistance"
                    
                current_content = ""
            else:
                current_content += line + "\n"
        
        # Add last section with ALL content
        if current_section and current_content.strip():
            sections.append((current_section, current_content.strip()))
        
        # Rebuild response with ALL content preserved
        if sections:
            final_response = ""
            for section_name, content in sections:
                if content.strip():
                    final_response += f"**{section_name}:**\n{content}\n\n"
            return final_response.strip()
    
    # If no structured sections found, return cleaned response with ALL content
    response = response.strip()
    
    # Only remove obvious PDF references at the end, keep all legal content
    lines = response.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Only skip obvious source reference lines at the very end
        if line and not (line.startswith('1.') and '.pdf' in line and len(line) < 100):
            cleaned_lines.append(line)
    
    final_clean = '\n'.join(cleaned_lines)
    
    # IMPORTANT: If cleaned version is significantly shorter, return original
    if len(final_clean.strip()) < len(original_response.strip()) * 0.7:
        return original_response
    
    return final_clean if final_clean.strip() else original_response

# Run the server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )