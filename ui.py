"""
Pakistan Legal AI - Modern Professional UI
Clean, modern interface for legal advice
"""

import streamlit as st
import requests
import json
import time
from datetime import datetime
import uuid

# Page configuration
st.set_page_config(
    page_title="Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern professional CSS
st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .main-header {
        text-align: center;
        color: #1a365d;
        font-weight: 700;
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .subtitle {
        text-align: center;
        color: #4a5568;
        font-weight: 400;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        opacity: 0.8;
    }
    
    /* Modern chat containers */
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
    }
    
    /* User message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.25rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.75rem 0;
        margin-left: 20%;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.25);
        font-weight: 400;
        line-height: 1.5;
    }
    
    /* AI response styling - Modern card design */
    .ai-message {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        margin: 1rem 0;
        margin-right: 10%;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        overflow: hidden;
    }
    
    .ai-header {
        background: linear-gradient(90deg, #f7fafc 0%, #edf2f7 100%);
        padding: 0.75rem 1.25rem;
        border-bottom: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
        font-weight: 500;
        color: #2d3748;
        font-size: 0.9rem;
    }
    
    .ai-content {
        padding: 1.5rem;
        line-height: 1.7;
        color: #2d3748;
        font-size: 0.95rem;
    }
    
    .ai-content h3 {
        color: #1a365d;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        font-size: 1rem;
        border-left: 3px solid #667eea;
        padding-left: 0.75rem;
    }
    
    .ai-content p {
        margin-bottom: 1rem;
        color: #4a5568;
    }
    
    .ai-content strong {
        color: #2d3748;
        font-weight: 600;
    }
    
    .ai-content.conversational {
        background: linear-gradient(135deg, #f0fff4 0%, #f7fafc 100%);
        border-radius: 12px;
        padding: 1.25rem;
        color: #2d3748;
        font-size: 0.95rem;
        line-height: 1.6;
        border: 1px solid #c6f6d5;
    }
    
    .ai-content.lawyer-directory {
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
        border-radius: 12px;
        padding: 1.25rem;
        color: #2d3748;
        font-size: 0.9rem;
        line-height: 1.6;
        border: 1px solid #fbbf24;
    }
    
    /* Timestamp styling */
    .timestamp {
        font-size: 0.75rem;
        color: #a0aec0;
        margin-left: 0.5rem;
    }
    
    /* Loading indicator */
    .loading-container {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        margin-right: 10%;
        text-align: center;
    }
    
    .loading-dots {
        color: #667eea;
        font-weight: 500;
    }
    
    /* Input area styling */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.025em !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Welcome message */
    .welcome-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "https://d238a068bfb4.ngrok-free.app"

class ChatManager:
    def __init__(self):
        if 'current_session_id' not in st.session_state:
            st.session_state.current_session_id = None
        if 'chat_sessions' not in st.session_state:
            st.session_state.chat_sessions = {}
        if 'current_messages' not in st.session_state:
            st.session_state.current_messages = []
    
    def create_new_session(self):
        """Create a new chat session"""
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        st.session_state.current_session_id = session_id
        st.session_state.current_messages = []
        st.session_state.chat_sessions[session_id] = {
            'title': 'New Consultation',
            'messages': [],
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        return session_id
    
    def load_session(self, session_id):
        """Load an existing chat session"""
        if session_id in st.session_state.chat_sessions:
            st.session_state.current_session_id = session_id
            st.session_state.current_messages = st.session_state.chat_sessions[session_id]['messages']
    
    def add_message(self, message, is_user=True):
        """Add a message to current session"""
        if not st.session_state.current_session_id:
            self.create_new_session()
        
        msg = {
            'message': message,
            'is_user': is_user,
            'timestamp': datetime.now().strftime("%H:%M")
        }
        
        st.session_state.current_messages.append(msg)
        st.session_state.chat_sessions[st.session_state.current_session_id]['messages'] = st.session_state.current_messages
        
        # Update session title with first user message
        if is_user and len(st.session_state.current_messages) == 1:
            title = message[:40] + "..." if len(message) > 40 else message
            st.session_state.chat_sessions[st.session_state.current_session_id]['title'] = title

def send_message_to_api(message, session_id=None):
    """Send message to FastAPI backend with retry mechanism"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            payload = {
                "query": message,
                "session_id": session_id
            }
            
            response = requests.post(f"{API_BASE_URL}/chat/message", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data['response'], data.get('session_id')
            else:
                return f"Sorry, I got an error response (Status: {response.status_code}). Please try again.", session_id
                
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return "⚠️ Cannot connect to the legal AI service. Please make sure the API server is running by executing: `python api.py`", session_id
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                continue
            return "⏰ Request timed out. Please try with a shorter question or check your connection.", session_id
            
        except Exception as e:
            if attempt < max_retries - 1:
                continue
            return f"An error occurred: {str(e)}. Please try again.", session_id
    
    return "Failed to get response after multiple attempts. Please check the API server.", session_id

def check_api_health():
    """Check if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def format_ai_response(message):
    """Format AI response for modern display"""
    # Check if this is a conversational/greeting response (English or Urdu)
    is_conversational = any(phrase in message.lower() for phrase in [
        "hello!", "i'm your legal assistant", "i'm doing great", "you're most welcome", 
        "i appreciate your question", "i specialize in pakistani law", "main bilkul theek hun",
        "main aap ka legal assistant hun", "koi baat nahi", "i don't have access to personal information",
        "main aap ki personal maloomat", "main yahan pakistani qanooni masail"
    ])
    
    if is_conversational:
        # For conversational responses, use a friendlier format
        return f'<div class="ai-content conversational">{message.replace(chr(10), "<br>")}</div>'
    
    # Split message into sections if it contains structured content
    sections = []
    current_section = ""
    
    lines = message.split('\n')
    
    for line in lines:
        line = line.strip()
        if line.startswith('**') and line.endswith(':**'):
            # This is a section header
            if current_section:
                sections.append(('content', current_section.strip()))
            sections.append(('header', line.replace('**', '').replace(':', '')))
            current_section = ""
        else:
            current_section += line + "\n"
    
    if current_section:
        sections.append(('content', current_section.strip()))
    
    # If no sections found, treat as single content
    if not sections or len(sections) == 1:
        return f'<div class="ai-content">{message.replace(chr(10), "<br>")}</div>'
    
    # Build formatted response
    formatted_html = '<div class="ai-content">'
    
    for section_type, content in sections:
        if section_type == 'header':
            formatted_html += f'<h3>{content}</h3>'
        else:
            formatted_html += f'<p>{content.replace(chr(10), "<br>")}</p>'
    
    formatted_html += '</div>'
    return formatted_html

def main():
    # Initialize chat manager
    chat_manager = ChatManager()
    
    # Header
    st.markdown('<h1 class="main-header">Legal Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Professional legal guidance for Pakistani law</p>', unsafe_allow_html=True)
    
    # Sidebar for chat history
    with st.sidebar:
        st.markdown("### 💼 Consultations")
        
        # New chat button
        if st.button("+ New Consultation", use_container_width=True, type="primary"):
            chat_manager.create_new_session()
            st.rerun()
        
        st.markdown("---")
        
        # Display chat sessions
        if st.session_state.chat_sessions:
            for session_id, session_data in reversed(list(st.session_state.chat_sessions.items())):
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        if st.button(
                            f"📋 {session_data['title']}", 
                            key=f"load_{session_id}",
                            use_container_width=True,
                            help=f"Created: {session_data['created_at']}"
                        ):
                            chat_manager.load_session(session_id)
                            st.rerun()
                    
                    with col2:
                        if st.button("🗑️", key=f"del_{session_id}", help="Delete"):
                            del st.session_state.chat_sessions[session_id]
                            if st.session_state.current_session_id == session_id:
                                st.session_state.current_session_id = None
                                st.session_state.current_messages = []
                            st.rerun()
        else:
            st.info("No previous consultations")
        
        st.markdown("---")
        
        # System status
        st.markdown("### ⚙️ System Status")
        if check_api_health():
            st.success("🟢 Service: Online")
        else:
            st.error("🔴 Service: Offline")
            st.info("Run: `python api.py`")
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat display area
        if st.session_state.current_messages:
            for msg in st.session_state.current_messages:
                if msg['is_user']:
                    st.markdown(f"""
                    <div class="user-message">
                        {msg['message']}
                        <span class="timestamp">{msg['timestamp']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Modern AI response card with dynamic header
                    formatted_content = format_ai_response(msg['message'])
                    
                    # Determine header based on response type
                    if any(phrase in msg['message'].lower() for phrase in [
                        "hello!", "salam!", "i'm your legal assistant", "i'm doing great", "you're most welcome", 
                        "i appreciate your question", "i specialize in pakistani law", "main bilkul theek hun",
                        "main aap ka legal assistant hun", "koi baat nahi", "i don't have access to personal information",
                        "main aap ki personal maloomat", "main yahan pakistani qanooni masail", "main pakistani qanoon mein mahir hun",
                        "salam! main aap ka legal assistant hun", "khushi hui ke madad kar saka"
                    ]):
                        header_text = "💬 Assistant"
                    elif any(phrase in msg['message'] for phrase in [
                        "Qualified Lawyers in", "Lawyers in", "Bar Council:", "Please specify which city",
                        "I have lawyer information for:"
                    ]):
                        header_text = "👩‍⚖️ Lawyer Directory"
                    else:
                        header_text = "⚖️ Legal Analysis"
                    
                    st.markdown(f"""
                    <div class="ai-message">
                        <div class="ai-header">
                            <span>{header_text}</span>
                            <span class="timestamp">{msg['timestamp']}</span>
                        </div>
                        {formatted_content}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Welcome message
            st.markdown("""
            <div class="welcome-card">
                <h3>👋 Welcome to Legal Assistant</h3>
                <p>I'm here to help you understand Pakistani law. Ask me any legal question and I'll provide professional guidance based on Pakistani legal documents.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Message input
        st.markdown("---")
        
        # Create form for message input
        with st.form("message_form", clear_on_submit=True):
            col_input, col_send = st.columns([4, 1])
            
            with col_input:
                user_input = st.text_area(
                    "Your legal question:",
                    placeholder="e.g., What are the penalties for tax evasion in Pakistan?",
                    height=80,
                    key="user_input"
                )
            
            with col_send:
                st.markdown("<br>", unsafe_allow_html=True)
                send_button = st.form_submit_button("Send", use_container_width=True, type="primary")
        
        # Process message when sent
        if send_button and user_input.strip():
            # Add user message to chat
            chat_manager.add_message(user_input, is_user=True)
            
            # Show loading indicator
            loading_placeholder = st.empty()
            loading_placeholder.markdown("""
            <div class="loading-container">
                <div class="loading-dots">🔍 Analyzing your legal question...</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Send to API
            response, session_id = send_message_to_api(user_input, st.session_state.current_session_id)
            
            # Update session ID if new
            if session_id and session_id != st.session_state.current_session_id:
                st.session_state.current_session_id = session_id
            
            loading_placeholder.empty()
            
            # Add AI response to chat
            chat_manager.add_message(response, is_user=False)
            
            # Rerun to update display
            st.rerun()
    
    with col2:
        # Quick actions panel
        st.markdown("### ⚡ Common Questions")
        
        common_questions = [
            "Property inheritance laws",
            "Divorce procedures", 
            "Criminal penalties",
            "Business registration",
            "Employment rights",
            "Contract disputes"
        ]
        
        for question in common_questions:
            if st.button(question, key=f"quick_{question}", use_container_width=True):
                # Create new session and add message
                if not st.session_state.current_session_id:
                    chat_manager.create_new_session()
                
                chat_manager.add_message(f"Tell me about {question} in Pakistan", is_user=True)
                
                # Get response
                with st.spinner("Getting response..."):
                    response, session_id = send_message_to_api(f"Tell me about {question} in Pakistan", st.session_state.current_session_id)
                    chat_manager.add_message(response, is_user=False)
                
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📚 Legal Areas")
        st.markdown("""
        • **Criminal Law** - Offenses & penalties
        • **Civil Law** - Contracts & disputes  
        • **Family Law** - Marriage & divorce
        • **Commercial Law** - Business matters
        • **Constitutional Law** - Rights & governance
        """)

if __name__ == "__main__":
    main()
