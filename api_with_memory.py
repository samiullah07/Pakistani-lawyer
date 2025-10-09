"""
Enhanced API with Conversational Memory and Streaming Support
Production-ready FastAPI backend for Pakistani Legal Assistant
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, AsyncGenerator
import uvicorn
from datetime import datetime
import logging
import os
import json
import asyncio

# LangChain imports for memory
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Pakistan Legal AI API with Memory",
    description="AI-powered legal advice system with conversational memory",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
legal_agent = None
retriever = None
classifier = None
agent_initialization_error = None

# Session-based memory storage
# In production, use Redis or a proper database
session_memories: Dict[str, ConversationBufferMemory] = {}

# Pydantic models
class ChatRequest(BaseModel):
    query: str
    session_id: str
    stream: bool = True  # Enable streaming by default

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str
    conversation_history: List[Dict]

class MemoryQuery(BaseModel):
    session_id: str

class HealthResponse(BaseModel):
    status: str
    message: str
    vector_store_status: str
    agent_status: str
    memory_sessions: int
    timestamp: str

# ============================================================================
# MEMORY MANAGEMENT
# ============================================================================

def get_or_create_memory(session_id: str) -> ConversationBufferMemory:
    """
    Get existing memory for session or create new one.
    Uses ConversationBufferMemory to store full conversation history.
    """
    if session_id not in session_memories:
        logger.info(f"Creating new memory for session: {session_id}")
        session_memories[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
    return session_memories[session_id]

def add_to_memory(session_id: str, user_message: str, ai_response: str):
    """Add conversation exchange to memory"""
    memory = get_or_create_memory(session_id)
    memory.chat_memory.add_user_message(user_message)
    memory.chat_memory.add_ai_message(ai_response)
    logger.info(f"Added to memory - Session: {session_id}")

def get_conversation_history(session_id: str) -> List[Dict]:
    """Get formatted conversation history for display"""
    if session_id not in session_memories:
        return []
    
    memory = session_memories[session_id]
    messages = memory.chat_memory.messages
    
    history = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            history.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            history.append({"role": "assistant", "content": msg.content})
    
    return history

def get_memory_context(session_id: str) -> str:
    """Get conversation context as string for LLM"""
    if session_id not in session_memories:
        return ""
    
    memory = session_memories[session_id]
    messages = memory.chat_memory.messages
    
    # Format last 10 messages for context
    context_messages = messages[-10:] if len(messages) > 10 else messages
    
    context_parts = []
    for msg in context_messages:
        if isinstance(msg, HumanMessage):
            context_parts.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            context_parts.append(f"Assistant: {msg.content}")
    
    return "\n".join(context_parts)

def clear_memory(session_id: str):
    """Clear memory for a session"""
    if session_id in session_memories:
        del session_memories[session_id]
        logger.info(f"Cleared memory for session: {session_id}")

# ============================================================================
# STARTUP & INITIALIZATION
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global legal_agent, retriever, classifier, agent_initialization_error
    
    try:
        logger.info("🚀 Starting Pakistan Legal AI API with Memory...")
        
        try:
            from agent import create_legal_agent
            from retriever import LegalRetriever, QueryClassifier
            
            # Initialize agent
            try:
                legal_agent = create_legal_agent()
                logger.info("✅ Legal agent initialized")
            except Exception as agent_error:
                logger.warning(f"⚠️ Legal agent initialization failed: {str(agent_error)}")
                agent_initialization_error = str(agent_error)
                legal_agent = None
            
            # Initialize retriever and classifier
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
        
        logger.info("✅ API startup complete with memory support")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {str(e)}")
        agent_initialization_error = str(e)

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check system health including memory status"""
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
        message="Pakistan Legal AI API is running with memory",
        vector_store_status=vector_status,
        agent_status=agent_status,
        memory_sessions=len(session_memories),
        timestamp=datetime.now().isoformat()
    )

# ============================================================================
# QUERY PROCESSING WITH MEMORY
# ============================================================================

async def process_query_with_memory(query: str, session_id: str) -> str:
    """
    Process query with conversational memory.
    Checks for meta-questions about conversation history.
    """
    query_lower = query.lower().strip()
    
    # Check for meta-questions about conversation
    meta_questions = [
        'what was my last message', 'what did i ask', 'what was my previous question',
        'what did i say before', 'my last query', 'my previous message',
        'what was our conversation', 'conversation history', 'chat history'
    ]
    
    if any(meta in query_lower for meta in meta_questions):
        history = get_conversation_history(session_id)
        
        if not history or len(history) < 2:
            return "We just started our conversation! You haven't asked anything yet. How can I help you with Pakistani law?"
        
        # Find last user message (excluding current)
        user_messages = [h for h in history if h['role'] == 'user']
        
        if 'last message' in query_lower or 'previous' in query_lower:
            if len(user_messages) >= 2:
                last_msg = user_messages[-2]['content']  # -2 because current is -1
                return f"Your last message was: \"{last_msg}\"\n\nWould you like me to provide more details about that topic?"
            else:
                return "This is your first question in our conversation!"
        
        # Full conversation history request
        if 'conversation' in query_lower or 'history' in query_lower:
            if len(history) <= 2:
                return "We just started chatting! Ask me anything about Pakistani law."
            
            summary = "Here's our conversation so far:\n\n"
            for i, msg in enumerate(history[:-1], 1):  # Exclude current message
                role = "You" if msg['role'] == 'user' else "Me"
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                summary += f"{i}. {role}: {content}\n"
            
            return summary + "\nWhat else would you like to know?"
    
    # Get conversation context for better responses
    context = get_memory_context(session_id)
    
    # Check for special queries (greetings, identity, etc.)
    special_response = handle_special_queries(query, context)
    if special_response:
        return special_response
    
    # Check for lawyer directory queries
    try:
        from lawyer_directory import handle_lawyer_search_query
        lawyer_response = handle_lawyer_search_query(query)
        if lawyer_response:
            return lawyer_response
    except Exception as lawyer_error:
        logger.warning(f"⚠️ Lawyer directory error: {lawyer_error}")
    
    # Process legal query with agent (if available)
    if not legal_agent:
        return get_agent_unavailable_response()
    
    try:
        # Pass context to agent if it supports it
        response = legal_agent.process_legal_query(query)
        return clean_ai_response(response)
    except Exception as e:
        logger.error(f"❌ Agent error: {str(e)}")
        return f"I encountered an error processing your legal question. Please try rephrasing or contact support."

# ============================================================================
# STREAMING ENDPOINT
# ============================================================================

async def generate_stream(text: str) -> AsyncGenerator[str, None]:
    """
    Generate streaming response word by word.
    Simulates real-time typing like ChatGPT.
    """
    words = text.split()
    
    for i, word in enumerate(words):
        # Send word with space
        chunk = word + " " if i < len(words) - 1 else word
        
        # Format as Server-Sent Events
        yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        
        # Small delay for streaming effect (adjust as needed)
        await asyncio.sleep(0.03)  # 30ms between words
    
    # Send completion signal
    yield f"data: {json.dumps({'done': True})}\n\n"

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming endpoint for real-time responses.
    Returns Server-Sent Events (SSE) for word-by-word streaming.
    """
    try:
        logger.info(f"📥 Streaming query: {request.query[:50]}... Session: {request.session_id}")
        
        # Process query with memory
        response = await process_query_with_memory(request.query, request.session_id)
        
        # Add to memory
        add_to_memory(request.session_id, request.query, response)
        
        # Return streaming response
        return StreamingResponse(
            generate_stream(response),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Streaming error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# REGULAR CHAT ENDPOINT (Non-streaming fallback)
# ============================================================================

@app.post("/chat/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """
    Regular chat endpoint (non-streaming).
    Use this if streaming is not supported by client.
    """
    try:
        logger.info(f"📥 Query: {request.query[:50]}... Session: {request.session_id}")
        
        # Process query with memory
        response = await process_query_with_memory(request.query, request.session_id)
        
        # Add to memory
        add_to_memory(request.session_id, request.query, response)
        
        # Get conversation history
        history = get_conversation_history(request.session_id)
        
        return ChatResponse(
            response=response,
            session_id=request.session_id,
            timestamp=datetime.now().isoformat(),
            conversation_history=history
        )
        
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MEMORY MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/memory/history/{session_id}")
async def get_memory_history(session_id: str):
    """Get conversation history for a session"""
    history = get_conversation_history(session_id)
    return {
        "session_id": session_id,
        "message_count": len(history),
        "history": history
    }

@app.delete("/memory/clear/{session_id}")
async def clear_session_memory(session_id: str):
    """Clear memory for a session"""
    clear_memory(session_id)
    return {"message": f"Memory cleared for session {session_id}"}

@app.get("/memory/sessions")
async def list_memory_sessions():
    """List all active memory sessions"""
    sessions = []
    for session_id, memory in session_memories.items():
        msg_count = len(memory.chat_memory.messages)
        sessions.append({
            "session_id": session_id,
            "message_count": msg_count
        })
    return {"sessions": sessions, "total": len(sessions)}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def detect_language(query: str) -> str:
    """Detect if query is in Urdu or English"""
    urdu_words = [
        'kya', 'hai', 'ho', 'hain', 'ka', 'ki', 'ke', 'mein', 'se', 'ko',
        'aap', 'main', 'hum', 'kaun', 'kaise', 'kahan', 'kab', 'kyun',
        'shukria', 'dhanyawad', 'salam'
    ]
    
    query_words = query.lower().split()
    urdu_word_count = sum(1 for word in query_words if word in urdu_words)
    
    return 'urdu' if (len(query_words) > 0 and urdu_word_count / len(query_words) > 0.3) else 'english'

def handle_special_queries(query: str, context: str = "") -> Optional[str]:
    """
    Handle greetings, identity questions, casual chat.
    Now context-aware using conversation history.
    """
    query_lower = query.lower().strip()
    detected_lang = detect_language(query)
    
    # Greetings
    greetings = ['hi', 'hello', 'hey', 'salam', 'assalam', 'good morning', 'good evening']
    if any(g == query_lower or g in query_lower.split() for g in greetings) and len(query_lower) < 25:
        if detected_lang == 'urdu':
            return "Salam! Main aap ka Legal Assistant hun. Kya koi qanooni sawal hai?"
        else:
            return "Hello! I'm your Legal Assistant for Pakistani law. What can I help you with today?"
    
    # How are you
    how_are_you = ['how are you', 'kaise ho', 'kya hal']
    if any(phrase in query_lower for phrase in how_are_you):
        if detected_lang == 'urdu':
            return "Main bilkul theek hun, shukria! Main Pakistani qanoon mein aap ki madad ke liye tayyar hun. Kya puchna chahte hain?"
        else:
            return "I'm doing great, thank you! I'm ready to help you with Pakistani law. What would you like to know?"
    
    # Identity
    identity = ['who are you', 'what are you', 'kaun ho']
    if any(phrase in query_lower for phrase in identity):
        if detected_lang == 'urdu':
            return "Main aap ka AI Legal Assistant hun - Pakistani qanoon mein mahir. Main Constitution, Penal Code, aur doosre legal acts ke baare mein aap ki madad kar sakta hun."
        else:
            return "I'm your AI Legal Assistant specialized in Pakistani law. I can help you understand the Constitution, Penal Code, and various legal matters in Pakistan."
    
    # Thanks
    thanks = ['thank you', 'thanks', 'shukria']
    if any(t in query_lower for t in thanks) and len(query_lower) < 30:
        if detected_lang == 'urdu':
            return "Koi baat nahi! Agar koi aur sawal ho to zaroor puchiye."
        else:
            return "You're welcome! Feel free to ask if you have any other questions."
    
    return None

def get_agent_unavailable_response() -> str:
    """Response when agent is not available"""
    return """⚠️ **Legal Database Not Ready**

The legal document database hasn't been built yet. To enable full legal assistance:

1. Run: `python main.py` to build the database
2. Wait for it to process all PDF documents
3. Restart the API server

**I can still help with:**
• General legal information
• Finding lawyers in your city
• Understanding legal procedures"""

def clean_ai_response(response: str) -> str:
    """Clean and format AI response"""
    # Remove metadata sections
    if "Sources" in response:
        response = response.split("Sources")[0]
    if "Disclaimer:" in response:
        response = response.split("Disclaimer:")[0]
    
    # Clean markdown
    response = response.replace("###", "").replace("##", "")
    
    return response.strip()

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
