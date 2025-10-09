"""
Modern Streamlit UI with Streaming & Memory
ChatGPT-like interface for Pakistani Legal Assistant
"""

import streamlit as st
import requests
import json
from datetime import datetime
import time
import uuid

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Legal Assistant - Pakistani Law",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS - Modern Professional Design
# ============================================================================

st.markdown("""
<style>
    /* Import modern fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global styling */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem 1rem;
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #1a1a1a;
        font-weight: 600;
    }
    
    /* Chat message containers */
    .stChatMessage {
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    
    /* Input box */
    .stChatInputContainer {
        border-top: 1px solid #e2e8f0;
        padding-top: 1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* History items in sidebar */
    .history-item {
        background: white;
        padding: 0.75rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 3px solid #667eea;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    /* Metrics */
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 600;
        color: #667eea;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Success/Info/Warning boxes */
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

API_BASE_URL = "http://localhost:8000"

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'session_id' not in st.session_state:
    st.session_state.session_id = f"session_{uuid.uuid4().hex[:12]}"

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'conversation_count' not in st.session_state:
    st.session_state.conversation_count = 0

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_api_health():
    """Check if API is running and healthy"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None

def stream_response(query: str, session_id: str):
    """
    Stream response from API word by word.
    Yields chunks as they arrive from the server.
    """
    try:
        with requests.post(
            f"{API_BASE_URL}/chat/stream",
            json={"query": query, "session_id": session_id, "stream": True},
            stream=True,
            timeout=30
        ) as response:
            
            if response.status_code != 200:
                yield f"Error: {response.status_code}"
                return
            
            # Process Server-Sent Events
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    
                    # Skip empty lines and non-data lines
                    if not line.startswith('data: '):
                        continue
                    
                    # Parse JSON data
                    try:
                        data = json.loads(line[6:])  # Skip 'data: ' prefix
                        
                        # Check if done
                        if data.get('done'):
                            break
                        
                        # Yield chunk
                        if 'chunk' in data:
                            yield data['chunk']
                    
                    except json.JSONDecodeError:
                        continue
    
    except requests.exceptions.Timeout:
        yield "⏰ Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        yield "⚠️ Cannot connect to API. Please ensure the server is running."
    except Exception as e:
        yield f"❌ Error: {str(e)}"

def send_message_regular(query: str, session_id: str):
    """
    Send message without streaming (fallback).
    Returns complete response at once.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/message",
            json={"query": query, "session_id": session_id},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data['response']
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Error: {str(e)}"

def get_conversation_history(session_id: str):
    """Fetch conversation history from API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/memory/history/{session_id}",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('history', [])
        return []
    
    except:
        return []

def clear_conversation():
    """Clear current conversation"""
    try:
        requests.delete(f"{API_BASE_URL}/memory/clear/{st.session_state.session_id}")
    except:
        pass
    
    # Reset session state
    st.session_state.messages = []
    st.session_state.session_id = f"session_{uuid.uuid4().hex[:12]}"
    st.session_state.conversation_count = 0

# ============================================================================
# SIDEBAR - Conversation History & Context
# ============================================================================

with st.sidebar:
    st.title("💬 Legal Assistant")
    st.markdown("---")
    
    # API Status
    is_healthy, health_data = check_api_health()
    
    if is_healthy:
        st.success("🟢 API Connected")
        
        if health_data:
            with st.expander("📊 System Status"):
                st.metric("Status", health_data.get('status', 'unknown').title())
                st.metric("Vector Store", health_data.get('vector_store_status', 'unknown'))
                st.metric("Active Sessions", health_data.get('memory_sessions', 0))
    else:
        st.error("🔴 API Offline")
        st.info("Start API: `python api_with_memory.py`")
    
    st.markdown("---")
    
    # Conversation Controls
    st.subheader("🎛️ Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 New Chat", use_container_width=True):
            clear_conversation()
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            clear_conversation()
            st.rerun()
    
    st.markdown("---")
    
    # Conversation Summary
    st.subheader("📝 Current Session")
    st.metric("Messages", len(st.session_state.messages))
    st.metric("Session ID", st.session_state.session_id[:8] + "...")
    
    # Conversation History Display
    if st.session_state.messages:
        st.markdown("---")
        st.subheader("💭 Conversation Context")
        
        with st.container(height=400):
            # Show last 10 exchanges
            recent_messages = st.session_state.messages[-20:]  # Last 10 exchanges
            
            for i, msg in enumerate(recent_messages):
                role = "You" if msg["role"] == "user" else "Assistant"
                content = msg["content"]
                
                # Truncate long messages for sidebar
                if len(content) > 100:
                    content = content[:100] + "..."
                
                # Create styled history item
                st.markdown(
                    f'<div class="history-item">'
                    f'<strong>{role}:</strong><br>'
                    f'{content}'
                    f'</div>',
                    unsafe_allow_html=True
                )
    
    st.markdown("---")
    
    # Quick Actions
    st.subheader("⚡ Quick Queries")
    
    quick_queries = [
        "What is Section 420 PPC?",
        "How to file an FIR?",
        "Property inheritance laws",
        "Divorce procedures",
        "Find lawyer in Lahore"
    ]
    
    for query in quick_queries:
        if st.button(query, key=f"quick_{query}", use_container_width=True):
            # Add to messages and process
            st.session_state.messages.append({"role": "user", "content": query})
            st.rerun()
    
    st.markdown("---")
    
    # Footer
    st.caption("💡 **Tip:** Ask me \"What was my last question?\" to test memory!")
    st.caption("🔒 Your conversations are private and secure")

# ============================================================================
# MAIN CHAT INTERFACE
# ============================================================================

# Header
st.title("⚖️ Pakistani Legal Assistant")
st.markdown("**Professional legal guidance powered by AI** • Bilingual (English/Urdu) • Conversational Memory")
st.markdown("---")

# Welcome message if no conversation yet
if not st.session_state.messages:
    st.info("""
    👋 **Welcome!** I'm your AI Legal Assistant for Pakistani law.
    
    **I can help you with:**
    - Understanding Pakistani laws and sections
    - Legal procedures and your rights
    - Finding qualified lawyers
    - Answering questions in English or Urdu
    
    **Memory Feature:** I remember our conversation! Try asking "What was my last question?" later.
    
    💬 Start by asking a question below...
    """)

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask anything about Pakistani law... (e.g., 'What is Section 420?')"):
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_count += 1
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response with streaming
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Show typing indicator
        with st.spinner("🤔 Thinking..."):
            time.sleep(0.3)  # Brief pause for natural feel
        
        # Stream the response
        try:
            for chunk in stream_response(prompt, st.session_state.session_id):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")  # Blinking cursor effect
                time.sleep(0.01)  # Small delay for smooth animation
            
            # Final response without cursor
            message_placeholder.markdown(full_response)
        
        except Exception as e:
            # Fallback to non-streaming if streaming fails
            st.warning("Streaming unavailable, loading complete response...")
            full_response = send_message_regular(prompt, st.session_state.session_id)
            message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# ============================================================================
# TESTING FEATURES SECTION
# ============================================================================

# Show testing panel in expander
with st.expander("🧪 Test Memory Features", expanded=False):
    st.markdown("### Test Conversational Memory")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Try these memory test questions:**")
        st.code("What was my last message?")
        st.code("What did I ask before?")
        st.code("Show our conversation history")
    
    with col2:
        st.markdown("**Current Session Info:**")
        st.write(f"Session ID: `{st.session_state.session_id}`")
        st.write(f"Total Messages: `{len(st.session_state.messages)}`")
        st.write(f"Exchanges: `{st.session_state.conversation_count}`")
    
    # Fetch and display memory from API
    if st.button("🔍 Fetch Memory from API"):
        with st.spinner("Fetching conversation history..."):
            history = get_conversation_history(st.session_state.session_id)
            
            if history:
                st.success(f"Found {len(history)} messages in memory")
                
                with st.container(height=300):
                    for i, msg in enumerate(history, 1):
                        role = "👤 You" if msg['role'] == 'user' else "🤖 Assistant"
                        st.markdown(f"**{i}. {role}:**")
                        st.text(msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content'])
                        st.markdown("---")
            else:
                st.info("No messages in memory yet. Start chatting!")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p><strong>⚖️ Pakistani Legal Assistant</strong> • AI-Powered Legal Guidance</p>
        <p style='font-size: 0.85rem;'>
            <em>Disclaimer: This is an AI assistant providing legal information, not legal advice. 
            Always consult a qualified lawyer for specific legal matters.</em>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
