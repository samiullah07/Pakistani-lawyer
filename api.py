"""
Pakistan Legal AI - FastAPI Backend (FIXED VERSION)
REST API endpoints for legal advice system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pakistan Legal AI API",
    description="AI-powered legal advice system for Pakistani law",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for services
legal_agent = None
retriever = None
classifier = None
agent_initialization_error = None

# Pydantic models
class LegalQuery(BaseModel):
    query: str
    session_id: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    message: str
    vector_store_status: str
    agent_status: str
    timestamp: str

# Chat storage
chat_sessions = {}

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global legal_agent, retriever, classifier, agent_initialization_error
    
    try:
        logger.info("🚀 Starting Pakistan Legal AI API...")
        
        # Try to initialize services
        try:
            from agent import create_legal_agent
            from retriever import LegalRetriever, QueryClassifier
            
            # Initialize agent (this might fail if vector store doesn't exist)
            try:
                legal_agent = create_legal_agent()
                logger.info("✅ Legal agent initialized")
            except Exception as agent_error:
                logger.warning(f"⚠️ Legal agent initialization failed: {str(agent_error)}")
                agent_initialization_error = str(agent_error)
                legal_agent = None
            
            # Initialize retriever and classifier separately
            try:
                retriever = LegalRetriever()
                classifier = QueryClassifier()
                logger.info("✅ Retriever and classifier initialized")
            except Exception as retriever_error:
                logger.warning(f"⚠️ Retriever initialization failed: {str(retriever_error)}")
                retriever = None
                classifier = None
            
        except ImportError as import_error:
            logger.error(f"❌ Failed to import modules: {str(import_error)}")
            agent_initialization_error = str(import_error)
        
        logger.info("✅ API startup complete (some services may be degraded)")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")
        agent_initialization_error = str(e)

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health"""
    vector_status = "Not Available"
    agent_status = "Not Available"
    
    if retriever:
        try:
            if retriever.vector_store and retriever.vector_store.vector_store:
                vector_status = "Available"
        except:
            vector_status = "Error"
    
    if legal_agent:
        agent_status = "Available"
    elif agent_initialization_error:
        agent_status = f"Error: {agent_initialization_error[:50]}"
    
    overall_status = "healthy" if (legal_agent or vector_status == "Available") else "degraded"
    
    return HealthResponse(
        status=overall_status,
        message="Pakistan Legal AI API is running",
        vector_store_status=vector_status,
        agent_status=agent_status,
        timestamp=datetime.now().isoformat()
    )

# Chat endpoint - FIXED VERSION
@app.post("/chat/message")
async def send_chat_message(query: LegalQuery):
    """Send a chat message and get response - works even without vector store"""
    try:
        # Generate session ID if not provided
        session_id = query.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"📥 Received query: {query.query[:50]}...")
        
        # STEP 1: Check for special queries (greetings, identity questions, etc.)
        # These should ALWAYS work, even without vector store or agent
        special_response = handle_special_queries(query.query)
        
        if special_response:
            logger.info("✅ Handled as special query (greeting/identity)")
            store_chat_message(session_id, query.query, special_response)
            return {
                "response": special_response,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        
        # STEP 2: Check for lawyer directory queries
        try:
            from lawyer_directory import handle_lawyer_search_query
            lawyer_response = handle_lawyer_search_query(query.query)
            if lawyer_response:
                logger.info("✅ Handled as lawyer directory query")
                store_chat_message(session_id, query.query, lawyer_response)
                return {
                    "response": lawyer_response,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as lawyer_error:
            logger.warning(f"⚠️ Lawyer directory error: {lawyer_error}")
        
        # STEP 3: Process as legal query (requires agent)
        if not legal_agent:
            # Agent not available - provide helpful error message
            error_response = get_agent_unavailable_response()
            logger.warning("❌ Legal agent not available")
            store_chat_message(session_id, query.query, error_response)
            return {
                "response": error_response,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        
        # Process legal query with agent
        try:
            logger.info("🔄 Processing with legal agent...")
            response = legal_agent.process_legal_query(query.query)
            clean_response = clean_ai_response(response)
            
            logger.info("✅ Legal query processed successfully")
            store_chat_message(session_id, query.query, clean_response)
            
            return {
                "response": clean_response,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as agent_error:
            logger.error(f"❌ Agent processing error: {str(agent_error)}")
            error_response = f"I encountered an error processing your legal question: {str(agent_error)}\\n\\nPlease try rephrasing your question or contact support if the issue persists."
            store_chat_message(session_id, query.query, error_response)
            return {
                "response": error_response,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            }
        
    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Utility functions
def detect_language(query: str) -> str:
    """Detect if query is in Urdu or English"""
    urdu_words = [
        'kya', 'hai', 'ho', 'hain', 'ka', 'ki', 'ke', 'mein', 'se', 'ko', 'ne', 'par', 'tak',
        'apko', 'aap', 'ap', 'tum', 'tumhe', 'main', 'hum', 'woh', 'yeh', 'is', 'us',
        'naam', 'kaun', 'kaise', 'kaisy', 'kahan', 'kab', 'kyun', 'kyu', 'pta', 'pata',
        'maloom', 'batao', 'bataiye', 'samjhao', 'madad', 'shukria', 'dhanyawad'
    ]
    
    query_words = query.lower().split()
    urdu_word_count = sum(1 for word in query_words if word in urdu_words)
    
    if len(query_words) > 0 and (urdu_word_count / len(query_words)) > 0.3:
        return 'urdu'
    else:
        return 'english'

def handle_special_queries(query: str) -> Optional[str]:
    """Handle greetings, identity questions - ALWAYS works"""
    query_lower = query.lower().strip()
    detected_lang = detect_language(query)
    
    # Greetings
    greetings = [
        'hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening', 
        'assalam alaikum', 'salam', 'adab', 'namaste', 'hi!', 'hello!', 'hey!'
    ]
    if any(greeting == query_lower or greeting in query_lower.split() for greeting in greetings) and len(query_lower) < 25:
        if detected_lang == 'urdu':
            return "Salam! Main aap ka Legal Assistant hun aur Pakistani qanoon mein mahir hun. Main aap ko qanooni masail, aap ke haqooq, aur qanooni procedures ke baare mein madad kar sakta hun. Kya koi qanooni sawal hai?"
        else:
            return "Hello! I'm your Legal Assistant, specialized in Pakistani law. I'm here to help you understand legal matters, your rights, and provide guidance on various legal issues in Pakistan. What legal question can I assist you with today?"
    
    # How are you
    how_are_you_phrases = [
        'how are you', 'how r u', 'how do you do', 'whats up',
        'ap kaisy ho', 'ap kaise ho', 'ap kaise hain', 'kaisy ho', 'kaise ho', 
        'kya hal hai', 'sab theek', 'ap ka kya haal hai', 'kia haal hai'
    ]
    if any(phrase in query_lower for phrase in how_are_you_phrases):
        if detected_lang == 'urdu':
            return "Main bilkul theek hun, puchne ke liye shukria! Main Pakistani qanoon ke baare mein aap ke sawalon ka jawab dene ke liye tayyar hun. Criminal law, civil law, family law, ya business regulations - kisi bhi qanooni masle mein madad kar sakta hun. Kya janna chahte hain?"
        else:
            return "I'm doing great, thank you for asking! I'm ready to help you with any questions about Pakistani law. Whether it's criminal law, civil matters, family law, or business regulations, I'm here to provide you with accurate legal guidance. What would you like to know?"
    
    # Identity questions
    identity_questions = [
        'who are you', 'what are you', 'who r u', 'what is your name', 'introduce yourself',
        'ap kaun ho', 'ap kya ho', 'ap kaun hain', 'tumhara naam kya hai',
        'tum kaun ho', 'aap kaun hain'
    ]
    if any(question in query_lower for question in identity_questions):
        if detected_lang == 'urdu':
            return "Main aap ka Legal Assistant hun - Pakistani qanoon mein mahir ek AI system. Mere paas Pakistani legal documents ki mukammal maloomat hai jisme Constitution, Penal Code, Civil Procedure Code, aur doosre qanooni acts shamil hain. Main aap ko qanooni procedures, aap ke haqooq, crimes ki saza, aur qanooni masail mein rehnamai provide kar sakta hun."
        else:
            return "I'm your Legal Assistant - an AI-powered legal guidance system specialized in Pakistani law. I have comprehensive knowledge of Pakistani legal documents including the Constitution, Penal Code, Civil Procedure Code, and various other legal acts. I can help you understand legal procedures, your rights, penalties for various offenses, and guide you on what steps to take in legal matters."
    
    # Thanks
    thanks_phrases = [
        'thank you', 'thanks', 'thank u', 'thx', 'shukria', 'dhanyawad', 
        'bohot shukria', 'bahut dhanyawad', 'shukar hai', 'thankyou', 'thnx'
    ]
    if any(phrase in query_lower for phrase in thanks_phrases) and len(query_lower) < 30:
        if detected_lang == 'urdu':
            return "Koi baat nahi! Khushi hui ke madad kar saka. Agar koi aur qanooni sawal hai to beshak puchiye. Main hamesha aap ki qanooni rehnamai ke liye hazir hun."
        else:
            return "You're most welcome! I'm glad I could help. If you have any other legal questions or need clarification on anything, please don't hesitate to ask. I'm here whenever you need legal guidance."
    
    # Goodbye
    goodbye_phrases = ['bye', 'goodbye', 'see you', 'allah hafiz', 'khuda hafiz', 'bye bye']
    if any(phrase in query_lower for phrase in goodbye_phrases):
        if detected_lang == 'urdu':
            return "Allah Hafiz! Aap ko phir kabhi qanooni madad ki zaroorat ho to zaroor aaiye. Khuda Hafiz!"
        else:
            return "Goodbye! Feel free to return anytime you need legal guidance. Take care!"
    
    return None

def get_agent_unavailable_response() -> str:
    """Response when agent is not available"""
    if agent_initialization_error and "vector" in agent_initialization_error.lower():
        return """⚠️ **Legal Database Not Ready**

The legal document database hasn't been built yet. To use the full legal assistance features, please:

1. **Build the database** by running: `python main.py`
2. **Wait** for it to process all PDF legal documents
3. **Restart** the API server

**What I can still help with:**
• General legal information
• Answering questions about Pakistani law system
• Finding lawyers in your city
• Understanding legal procedures

Please build the database for detailed legal analysis of specific sections and cases."""
    
    return """⚠️ **System Initializing**

The legal assistance system is still starting up. Please:

1. Wait a moment and try again
2. Check that all dependencies are installed
3. Ensure the vector store is built (run `python main.py`)

If the issue persists, please contact support."""

def store_chat_message(session_id: str, user_message: str, ai_response: str):
    """Store chat messages in session"""
    if session_id not in chat_sessions:
        title = user_message[:50] + "..." if len(user_message) > 50 else user_message
        chat_sessions[session_id] = {
            "session_id": session_id,
            "title": title,
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
    
    timestamp = datetime.now().isoformat()
    chat_sessions[session_id]["messages"].extend([
        {"message": user_message, "is_user": True, "timestamp": timestamp},
        {"message": ai_response, "is_user": False, "timestamp": timestamp}
    ])

def clean_ai_response(response: str) -> str:
    """Clean AI response"""
    if "Sources" in response:
        response = response.split("Sources")[0]
    if "Disclaimer:" in response:
        response = response.split("Disclaimer:")[0]
    
    response = response.replace("###", "").replace("##", "")
    return response.strip()

# Chat session endpoints
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

# Run the server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "api_backup:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
