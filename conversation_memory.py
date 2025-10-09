"""
Conversation Memory Manager for Legal Assistant
Handles context, memory, and sidebar summaries
"""

from typing import List, Dict, Optional
from datetime import datetime
import json


class ConversationMemory:
    """Manages conversation history and context"""
    
    def __init__(self):
        self.sessions = {}  # session_id -> conversation data
    
    def create_session(self, session_id: str) -> Dict:
        """Create a new conversation session"""
        self.sessions[session_id] = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "messages": [],
            "context_summary": [],
            "topics_discussed": [],
            "language": "english"
        }
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the conversation"""
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        message = {
            "role": role,  # 'user' or 'assistant'
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.sessions[session_id]["messages"].append(message)
        
        # Update context summary if it's a legal query
        if metadata and metadata.get("intent") == "legal_query":
            self._update_context_summary(session_id, content, metadata)
    
    def _update_context_summary(self, session_id: str, content: str, metadata: Dict):
        """Update sidebar context summary"""
        session = self.sessions[session_id]
        
        # Extract key information
        domain = metadata.get("domain", "")
        section = self._extract_section(content)
        
        # Create summary entry
        summary = ""
        if section:
            summary = f"Discussed {section}"
        elif domain:
            summary = f"Query about {domain} law"
        else:
            summary = content[:50] + "..." if len(content) > 50 else content
        
        # Add topic to discussed topics
        if domain and domain not in session["topics_discussed"]:
            session["topics_discussed"].append(domain)
        
        # Add to context summary (keep last 5)
        session["context_summary"].append(summary)
        if len(session["context_summary"]) > 5:
            session["context_summary"] = session["context_summary"][-5:]
    
    def _extract_section(self, text: str) -> Optional[str]:
        """Extract section number from text"""
        import re
        # Match patterns like "Section 420", "Dafa 302", etc.
        patterns = [
            r'[Ss]ection\s+(\d+)',
            r'[Dd]afa\s+(\d+)',
            r'[Aa]rticle\s+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"Section {match.group(1)}"
        return None
    
    def get_context(self, session_id: str) -> str:
        """Get conversation context for LLM"""
        if session_id not in self.sessions:
            return ""
        
        session = self.sessions[session_id]
        messages = session["messages"]
        
        if not messages:
            return ""
        
        # Build context from recent messages (last 5 exchanges)
        context_parts = []
        recent_messages = messages[-10:]  # Last 5 user-assistant pairs
        
        for msg in recent_messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            content = msg["content"][:200]  # Truncate long messages
            context_parts.append(f"{role}: {content}")
        
        return "\n".join(context_parts)
    
    def get_sidebar_summary(self, session_id: str) -> Dict:
        """Get sidebar summary for display"""
        if session_id not in self.sessions:
            return {"context_summary": [], "topics_discussed": [], "message_count": 0}
        
        session = self.sessions[session_id]
        
        return {
            "context_summary": session["context_summary"],
            "topics_discussed": session["topics_discussed"],
            "message_count": len(session["messages"]) // 2,  # Number of exchanges
            "language": session["language"]
        }
    
    def update_language(self, session_id: str, language: str):
        """Update session language"""
        if session_id in self.sessions:
            self.sessions[session_id]["language"] = language
    
    def clear_session(self, session_id: str):
        """Clear a conversation session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_recent_topics(self, session_id: str) -> List[str]:
        """Get recently discussed topics"""
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id]["topics_discussed"]


class StreamingResponseBuilder:
    """Builds streaming-style responses in chunks"""
    
    @staticmethod
    def build_legal_response(
        domain: str,
        law_section: str,
        explanation: str,
        punishment: str,
        practical_notes: str,
        suggestions: str,
        language: str = "english"
    ) -> List[str]:
        """Build response in progressive chunks"""
        
        chunks = []
        
        if language == "urdu":
            # Chunk 1: Acknowledgment
            chunks.append("👩‍⚖️ Aap ka sawal check kar raha hun...")
            
            # Chunk 2: Law & Section
            if law_section:
                chunks.append(f"📖 **Qabil-e-Tatbeeq Qanoon:** {law_section}")
            
            # Chunk 3: Explanation
            if explanation:
                chunks.append(f"**Tashreeh:** {explanation}")
            
            # Chunk 4: Punishment
            if punishment:
                chunks.append(f"⚖️ **Saza:** {punishment}")
            
            # Chunk 5: Practical Notes
            if practical_notes:
                chunks.append(f"💡 **Amali Nuktay:** {practical_notes}")
            
            # Chunk 6: Suggestions
            if suggestions:
                chunks.append(f"**Mashware:** {suggestions}")
        
        else:
            # Chunk 1: Acknowledgment
            chunks.append("👩‍⚖️ Let me check that for you...")
            
            # Chunk 2: Law & Section
            if law_section:
                chunks.append(f"📖 **Applicable Law:** {law_section}")
            
            # Chunk 3: Explanation
            if explanation:
                chunks.append(f"**Explanation:** {explanation}")
            
            # Chunk 4: Punishment
            if punishment:
                chunks.append(f"⚖️ **Punishment:** {punishment}")
            
            # Chunk 5: Practical Notes
            if practical_notes:
                chunks.append(f"💡 **Practical Note:** {practical_notes}")
            
            # Chunk 6: Suggestions
            if suggestions:
                chunks.append(f"**Suggestions:** {suggestions}")
        
        return chunks
    
    @staticmethod
    def format_response_from_chunks(chunks: List[str]) -> str:
        """Format chunks into final response"""
        return "\n\n".join(chunks)


# Global memory instance
conversation_memory = ConversationMemory()


def get_memory() -> ConversationMemory:
    """Get the global conversation memory instance"""
    return conversation_memory
