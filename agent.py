"""
Pakistan Legal AI - Agent Module
Bilingual Legal Assistant with Agentic Behavior
"""

from typing import Dict, List, Any, TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
import json
import re
from langchain_groq import ChatGroq
from dotenv import load_dotenv


load_dotenv()

class LegalState(TypedDict):
    """State for legal advice workflow"""
    query: str
    language: str  # 'english' or 'urdu'
    intent: str  # 'casual_chat', 'legal_query', 'greeting'
    domain: str
    context: str
    sources: List[Dict]
    legal_analysis: str
    recommendations: str
    lawyer_type: str
    confidence: str
    final_response: str

class LegalAgent:
    def __init__(self, llm=None, vector_store_path: str = "legal_vector_store"):
        """Initialize bilingual legal agent with LLM and retriever"""
        # Import here to avoid circular imports
        from retriever import LegalRetriever, QueryClassifier
        
        self.retriever = LegalRetriever(vector_store_path)
        self.classifier = QueryClassifier()
        self.llm = llm
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow for legal advice"""
        
        workflow = StateGraph(LegalState)
        
        # Add nodes
        workflow.add_node("detect_language", self._detect_language)
        workflow.add_node("detect_intent", self._detect_intent)
        workflow.add_node("handle_casual", self._handle_casual_chat)
        workflow.add_node("classify_query", self._classify_query)
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("analyze_legal_issue", self._analyze_legal_issue)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("recommend_lawyer", self._recommend_lawyer)
        workflow.add_node("compile_response", self._compile_response)
        
        # Add conditional edges
        workflow.add_edge("detect_language", "detect_intent")
        workflow.add_conditional_edges(
            "detect_intent",
            self._route_by_intent,
            {
                "casual": "handle_casual",
                "legal": "classify_query"
            }
        )
        workflow.add_edge("handle_casual", END)
        workflow.add_edge("classify_query", "retrieve_context")
        workflow.add_edge("retrieve_context", "analyze_legal_issue")
        workflow.add_edge("analyze_legal_issue", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "recommend_lawyer")
        workflow.add_edge("recommend_lawyer", "compile_response")
        workflow.add_edge("compile_response", END)
        
        # Set entry point
        workflow.set_entry_point("detect_language")
        return workflow.compile()
    
    def _detect_language(self, state: LegalState) -> LegalState:
        """Detect if query is in English or Urdu"""
        query = state["query"].lower()
        
        # Check for Urdu script (Unicode range for Urdu)
        urdu_pattern = re.compile(r'[\u0600-\u06FF]')
        
        # Common Urdu words in Roman script
        urdu_roman_words = ['kya', 'hai', 'mein', 'ka', 'ki', 'ko', 'se', 'aap', 'main', 'hun', 
                           'thi', 'tha', 'hain', 'hoon', 'kaise', 'kyun', 'aur', 'ya']
        
        if urdu_pattern.search(state["query"]):
            state["language"] = "urdu"
        elif any(word in query.split() for word in urdu_roman_words):
            state["language"] = "urdu"
        else:
            state["language"] = "english"
        
        print(f"🌐 Detected language: {state['language']}")
        return state
    
    def _detect_intent(self, state: LegalState) -> LegalState:
        """Detect if this is casual chat or legal query"""
        query_lower = state["query"].lower()
        
        # Casual/greeting patterns in English
        casual_english = [
            'hi', 'hello', 'hey', 'how are you', 'whats up', 'good morning',
            'good evening', 'good afternoon', 'thanks', 'thank you', 'bye',
            'goodbye', 'who are you', 'what is your name', 'introduce yourself'
        ]
        
        # Casual/greeting patterns in Urdu (Roman)
        casual_urdu = [
            'salam', 'assalam', 'kaise ho', 'kya hal hai', 'kaisa hai',
            'theek ho', 'shukriya', 'mehrbani', 'allah hafiz', 'khuda hafiz',
            'tum kaun ho', 'aap ka naam kya hai'
        ]
        
        # Legal keywords
        legal_keywords = [
            'law', 'section', 'act', 'code', 'penal', 'court', 'judge', 'case',
            'lawyer', 'attorney', 'legal', 'rights', 'punishment', 'crime',
            'qanoon', 'dafa', 'kanoon', 'adalat', 'wakeel', 'saza', 'jurm'
        ]
        
        # Check for casual patterns
        is_casual = any(pattern in query_lower for pattern in casual_english + casual_urdu)
        has_legal_keywords = any(keyword in query_lower for keyword in legal_keywords)
        
        # If it's short and casual-looking without legal keywords, it's casual
        if is_casual and not has_legal_keywords and len(state["query"].split()) < 15:
            state["intent"] = "casual_chat"
        else:
            state["intent"] = "legal_query"
        
        print(f"🎯 Intent detected: {state['intent']}")
        return state
    
    def _route_by_intent(self, state: LegalState) -> str:
        """Route based on intent"""
        return "casual" if state["intent"] == "casual_chat" else "legal"
    
    def _handle_casual_chat(self, state: LegalState) -> LegalState:
        """Handle casual conversation in appropriate language"""
        query_lower = state["query"].lower()
        language = state["language"]
        
        # Greetings
        if any(word in query_lower for word in ['hi', 'hello', 'hey', 'salam', 'assalam']):
            if language == "urdu":
                response = "Salam! Main Sami Ullah AI hun, aap ka Pakistani Legal Assistant. Main aap ki kaise madad kar sakta hun?"
            else:
                response = "Hello! I'm Sami Ullah AI, your Pakistani Legal Assistant. How can I help you today?"
        
        # How are you
        elif any(phrase in query_lower for phrase in ['how are you', 'kaise ho', 'kya hal']):
            if language == "urdu":
                response = "Main bilkul theek hun, shukriya! Main aap ka legal assistant hun aur Pakistani qanoon mein mahir hun. Kya aap ka koi legal sawal hai?"
            else:
                response = "I'm doing great, thank you! I'm your legal assistant specialized in Pakistani Law. Do you have any legal questions?"
        
        # Thank you
        elif any(word in query_lower for word in ['thanks', 'thank you', 'shukriya', 'mehrbani']):
            if language == "urdu":
                response = "Aap ka swagat hai! Koi aur sawal ho to zaroor poochiye. Main yahan aap ki madad ke liye hun."
            else:
                response = "You're most welcome! Feel free to ask any legal questions. I'm here to help you understand Pakistani law."
        
        # Who are you
        elif any(phrase in query_lower for phrase in ['who are you', 'what is your name', 'kaun ho', 'naam kya hai']):
            if language == "urdu":
                response = "Main Sami Ullah AI hun, aap ka Pakistani Legal Assistant. Main Pakistani qanoon mein mahir hun aur aap ko legal mashware aur guidance dene ke liye yahan hun. Yaad rahen, main ek AI assistant hun, wakeel nahi, lekin main aap ko Pakistani qanoon samajhne mein madad kar sakta hun."
            else:
                response = "I'm Sami Ullah AI, your Pakistani Legal Assistant. I specialize in Pakistani Law and I'm here to provide legal guidance and information. Remember, I'm an AI assistant for legal research, not a lawyer, but I can help you understand Pakistani law better."
        
        # Goodbye
        elif any(word in query_lower for word in ['bye', 'goodbye', 'allah hafiz', 'khuda hafiz']):
            if language == "urdu":
                response = "Allah Hafiz! Aap ko phir kabhi legal masail mein madad ki zaroorat ho to zaroor aaiye."
            else:
                response = "Goodbye! Feel free to return anytime you need legal guidance. Take care!"
        
        # Default friendly response
        else:
            if language == "urdu":
                response = "Main yahan aap ki legal masail mein madad ke liye hun. Kya aap ka koi qanooni sawal hai jo main jawab de sakun?"
            else:
                response = "I'm here to help you with legal matters. Do you have any legal questions I can assist with?"
        
        state["final_response"] = response
        print("💬 Casual conversation handled")
        return state
    
    def _classify_query(self, state: LegalState) -> LegalState:
        """Classify the legal query into domain"""
        domain = self.classifier.classify_query(state["query"])
        print(f"🏷️ Classified as: {domain}")
        
        state["domain"] = domain
        return state
    
    def _retrieve_context(self, state: LegalState) -> LegalState:
        """Retrieve relevant legal context"""
        context_data = self.retriever.get_context_for_legal_advice(state["query"])
        
        state["context"] = context_data["context"]
        state["sources"] = context_data["sources"]
        state["confidence"] = context_data["confidence"]
        
        print(f"📚 Retrieved context with {context_data['total_docs_found']} documents")
        return state
    
    def _analyze_legal_issue(self, state: LegalState) -> LegalState:
        """Analyze the legal issue using LLM with bilingual support"""
        
        language = state["language"]
        
        if language == "urdu":
            analysis_prompt = f"""
            Aap ek Pakistani qanoon ke mahir hain. Is legal sawal ka jawab Pakistani qanoon ke mutabiq dein.
            
            Sawal: {state["query"]}
            Legal Domain: {state["domain"]}
            
            Mutalliqah Qanooni Maloomat:
            {state["context"]}
            
            Tafseel se jawab dein jismein shamil hon:
            1. **Qabil-e-Tatbeeq Qanoon aur Dafa'at (Applicable Law & Sections)**
            2. **Qanooni Matn (Legal Text - mختصر)**
            3. **Saza aur Category (Punishment & Category)**
            4. **Amali Nuktay (Practical Implications)**
            5. **Mashware (Suggestions)**
            
            Apna jawab factual aur Pakistani qanoon par mabni rakhein. Urdu mein jawab dein.
            """
        else:
            analysis_prompt = f"""
            You are a professional, intelligent Pakistani legal expert. Analyze this legal query based on Pakistani law.
            
            Query: {state["query"]}
            Legal Domain: {state["domain"]}
            
            Relevant Legal Context:
            {state["context"]}
            
            Provide a structured, clear analysis including:
            
            **Applicable Law & Section:**
            [Specify the exact law and section number]
            
            **Key Legal Text (simplified):**
            [Brief explanation of what the law says]
            
            **Punishment & Category:**
            [Punishment details, whether bailable/non-bailable, compoundable/non-compoundable, which court]
            
            **Practical Implications:**
            [What this means in practice for the user]
            
            **Suggestions:**
            [Next steps, whether to consult lawyer, file FIR, etc.]
            
            Keep your response professional, empathetic, and factual based on Pakistani law.
            """
        
        # If LLM is available, use it
        if self.llm:
            try:
                response = self.llm.invoke(analysis_prompt, config={'timeout': 30})
                analysis = response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                print(f"❌ LLM error: {e}, using template response")
                analysis = self._template_legal_analysis(state)
        else:
            analysis = self._template_legal_analysis(state)
        
        state["legal_analysis"] = analysis
        print("⚖️ Legal analysis completed")
        return state
    
    def _generate_recommendations(self, state: LegalState) -> LegalState:
        """Generate actionable recommendations in appropriate language"""
        
        language = state["language"]
        
        if language == "urdu":
            recommendations_prompt = f"""
            Is qanooni tajziye ke mutabiq, wazeh aur amal-qaabil mashware dein:
            
            Sawal: {state["query"]}
            Domain: {state["domain"]}
            Tajziya: {state["legal_analysis"]}
            
            Mashware dein:
            1. Fauran kya karna chahiye
            2. Kaunse kagzaat chahiye
            3. Qanooni rawaiye
            4. Ehtiyati tadabeer
            5. Waqt ka khayal
            
            Mashware practical aur Pakistani qanooni nizam ke mutabiq hon. Urdu mein jawab dein.
            """
        else:
            recommendations_prompt = f"""
            Based on this legal analysis, provide clear, actionable recommendations:
            
            Query: {state["query"]}
            Domain: {state["domain"]}
            Analysis: {state["legal_analysis"]}
            
            Provide step-by-step recommendations:
            1. Immediate actions to take
            2. Documentation needed
            3. Legal procedures to follow
            4. Precautions and warnings
            5. Timeline considerations
            
            Make recommendations practical, empathetic, and specific to Pakistani legal system.
            """
        
        if self.llm:
            try:
                response = self.llm.invoke(recommendations_prompt)
                recommendations = response.content if hasattr(response, 'content') else str(response)
            except Exception as e:
                print(f"❌ LLM error: {e}, using template recommendations")
                recommendations = self._template_recommendations(state)
        else:
            recommendations = self._template_recommendations(state)
        
        state["recommendations"] = recommendations
        print("💡 Recommendations generated")
        return state
    
    def _recommend_lawyer(self, state: LegalState) -> LegalState:
        """Recommend appropriate type of lawyer in appropriate language"""
        
        language = state["language"]
        
        lawyer_mapping = {
            "criminal": ("Criminal Defense Lawyer", "Criminal Defense Wakeel"),
            "civil": ("Civil Litigation Lawyer", "Civil Wakeel"), 
            "family": ("Family Law Lawyer", "Family Law Wakeel"),
            "commercial": ("Corporate/Commercial Lawyer", "Corporate/Commercial Wakeel"),
            "constitutional": ("Constitutional Lawyer", "Constitutional Wakeel"),
            "general": ("General Practice Lawyer", "General Practice Wakeel")
        }
        
        lawyer_type_en, lawyer_type_ur = lawyer_mapping.get(state["domain"], ("General Practice Lawyer", "General Practice Wakeel"))
        
        if language == "urdu":
            lawyer_guidance = f"""
            **Tavsiya Shuda Qanooni Numayandagi:** {lawyer_type_ur}
            
            **Is Maharat ki Wajah:**
            - {state["domain"]} qanoon mein maharat
            - Isi tarah ke cases mein tajruba
            - Mutalliqah rawaiye ka ilm
            
            **Kya Dhundna Chahiye:**
            - Bar Council ki registration
            - {state["domain"]} cases mein tajruba
            - Acha track record
            - Wazeh fee structure
            """
        else:
            lawyer_guidance = f"""
            **Recommended Legal Representation:** {lawyer_type_en}
            
            **Why this specialization:**
            - Specialized knowledge in {state["domain"]} law
            - Experience with similar cases
            - Understanding of relevant procedures
            
            **What to look for:**
            - Bar Council registration
            - Experience in {state["domain"]} cases
            - Good track record
            - Clear fee structure
            """
        
        state["lawyer_type"] = lawyer_guidance
        print(f"👩‍⚖️ Lawyer recommendation: {lawyer_type_en}")
        return state
    
    def _compile_response(self, state: LegalState) -> LegalState:
        """Compile final response in appropriate language"""
        
        language = state["language"]
        
        if language == "urdu":
            final_response = f"""
**Qanooni Tajziya aur Mashwara**

**Sawal ka Domain:** {state["domain"].title()}
**Yaqeen ka Daraja:** {state["confidence"].title()}

{state["legal_analysis"]}

{state["recommendations"]}

{state["lawyer_type"]}

**Mazeed Maloomat:**
"""
            if state["sources"]:
                final_response += "\nYeh maloomat in qanooni dastavezat par mabni hai:\n"
                for i, source in enumerate(state["sources"][:3], 1):
                    final_response += f"{i}. {source['source_file']}\n"
            
            final_response += """

---
**Disclaimer:** Yeh abtedai qanooni rahnumai hai jo mojuda qanooni dastavezat par mabni hai. 
Kisi bhi makhsoos qanooni masle ke liye hamesha kisi qualified Pakistani wakeel se mashwara karen.

**Yaad Rahen:** Main ek AI assistant hun, wakeel nahi. Professional legal advice ke liye hamesha kisi qualified wakeel se raabta karen.
"""
        else:
            final_response = f"""
**Legal Analysis & Advice**

**Query Domain:** {state["domain"].title()}
**Confidence Level:** {state["confidence"].title()}

{state["legal_analysis"]}

{state["recommendations"]}

{state["lawyer_type"]}

**Sources:**
"""
            if state["sources"]:
                final_response += "\nBased on the following legal documents:\n"
                for i, source in enumerate(state["sources"][:3], 1):
                    final_response += f"{i}. {source['source_file']}\n"
            
            final_response += """

---
**Disclaimer:** This is preliminary legal guidance based on available legal documents. 
Always consult with a qualified Pakistani lawyer for specific legal advice.

**Remember:** I am an AI assistant for legal research and guidance, not a lawyer. For serious legal matters, always seek professional legal counsel.
"""
        
        state["final_response"] = final_response
        print("✅ Final response compiled")
        return state
 
    def _template_legal_analysis(self, state: LegalState) -> str:
        """Template analysis when LLM is not available"""
        language = state["language"]
        
        if language == "urdu":
            return f"""
**Qabil-e-Tatbeeq Qanoon aur Dafa'at:**
Aap ke sawal {state["domain"]} qanoon se mutalliq hai.

**Qanooni Matn:**
Mutalliqah qanooni dastavezat ki bunyad par.

**Mashwara:**
Mehrbani karke kisi Pakistani wakeel se raabta karen jo is masle mein aap ki tafseel se madad kar sake.
"""
        
        if state["domain"] == "criminal":
            return """
**Applicable Law & Section:**
Pakistan Penal Code 1860 - Various sections depending on the specific offense

**Key Legal Text:**
The Pakistan Penal Code defines various criminal offenses and their punishments.

**Punishment & Category:**
Varies based on specific section. Categories include:
- Bailable/Non-bailable
- Compoundable/Non-compoundable
- Cognizable/Non-cognizable

**Practical Implications:**
Criminal matters require immediate legal attention. Documentation and evidence preservation are crucial.

**Suggestions:**
1. Consult a criminal defense lawyer immediately
2. Do not make any statements without legal counsel
3. Preserve all evidence
4. Understand your rights under the law
"""
        
        return f"""
**Applicable Law & Section:**
Based on Pakistani {state["domain"]} law

**Key Legal Text:**
Please refer to the specific legal provisions retrieved from the documents.

**Practical Implications:**
This requires professional legal evaluation.

**Suggestions:**
Consult with a qualified Pakistani lawyer specializing in {state["domain"]} law for specific guidance on your situation.
"""

    def _template_recommendations(self, state: LegalState) -> str:
        """Template recommendations when LLM is not available"""
        language = state["language"]
        
        if language == "urdu":
            return f"""
**Amal-qaabil Mashware:**

1. **Fauran:** Tamam zaruri kagzaat jama karen
2. **Wakeel:** Kisi qualified {state["domain"]} wakeel se raabta karen
3. **Rawaiye:** Qanooni rawaiye ka sahi tareeqe se itteba karen
4. **Ehtiyat:** Apne huqooq aur zimmedariyan samjhen
"""
        
        return f"""
**Actionable Recommendations:**

1. **Immediate:** Gather all relevant documents and evidence
2. **Legal Counsel:** Consult with a qualified {state["domain"]} lawyer
3. **Procedures:** Follow proper legal procedures as per Pakistani law
4. **Precautions:** Understand your rights and obligations
5. **Documentation:** Keep detailed records of all interactions and documents
"""
        
    def process_legal_query(self, query: str) -> str:
        """Process a legal query through the workflow"""
        
        print(f"🚀 Processing query: {query[:50]}...")
        
        # Initialize state
        initial_state = LegalState(
            query=query,
            language="",
            intent="",
            domain="",
            context="",
            sources=[],
            legal_analysis="",
            recommendations="",
            lawyer_type="",
            confidence="",
            final_response=""
        )
        
        # Run workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            return final_state["final_response"]
        except Exception as e:
            print(f"❌ Error processing query: {str(e)}")
            # Return error in detected language if possible
            if "language" in initial_state and initial_state["language"] == "urdu":
                return f"Khata: Aap ke sawal ko process karne mein masla: {str(e)}"
            return f"Error processing your query: {str(e)}"

# Utility function to create agent
def create_legal_agent(llm:ChatGroq=ChatGroq(model="llama-3.3-70b-versatile", temperature=0,timeout=30), vector_store_path: str = "legal_vector_store") -> LegalAgent:
    """Create and return a bilingual legal agent instance"""
    return LegalAgent(llm=llm, vector_store_path=vector_store_path)

if __name__ == "__main__":
    # Test the agent
    agent = create_legal_agent()
    
    # Test queries
    test_queries = [
        "Hi, how are you?",
        "What is section 420 in Pakistan?",
        "Salam, kaise hain aap?",
        "Section 302 kya hai?"
    ]
    
    print("🧪 Testing Bilingual Legal Agent...\n")
    
    for query in test_queries:
        print("=" * 60)
        response = agent.process_legal_query(query)
        print(response)
        print("\n")
