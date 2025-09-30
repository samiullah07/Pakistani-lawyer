"""
Pakistan Legal AI - Agent Module
LangGraph workflow for legal advice generation
"""

from typing import Dict, List, Any, TypedDict
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
import json
from langchain_groq import ChatGroq
from dotenv import load_dotenv


load_dotenv()

class LegalState(TypedDict):
    """State for legal advice workflow"""
    query: str
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
        """Initialize legal agent with LLM and retriever"""
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
        workflow.add_node("classify_query", self._classify_query)
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("analyze_legal_issue", self._analyze_legal_issue)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("recommend_lawyer", self._recommend_lawyer)
        workflow.add_node("compile_response", self._compile_response)
        
        # Add edges
        workflow.add_edge("classify_query", "retrieve_context")
        workflow.add_edge("retrieve_context", "analyze_legal_issue")
        workflow.add_edge("analyze_legal_issue", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "recommend_lawyer")
        workflow.add_edge("recommend_lawyer", "compile_response")
        workflow.add_edge("compile_response", END)
        
        # Set entry point
        workflow.set_entry_point("classify_query")
        return workflow.compile()
    
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
        """Analyze the legal issue using LLM"""
        
        analysis_prompt = f"""
        You are a Pakistani legal expert. Analyze this legal query based on Pakistani law.
        
        Query: {state["query"]}
        Legal Domain: {state["domain"]}
        
        Relevant Legal Context:
        {state["context"]}
        
        Provide a detailed legal analysis including:
        1. Applicable laws and sections
        2. Legal implications
        3. Rights and obligations
        4. Potential legal consequences
        
        Keep your response factual and based on Pakistani law.
        """
        
        # If LLM is available, use it. Otherwise, provide template response
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
        """Generate actionable recommendations"""
        
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
        
        Make recommendations practical and specific to Pakistani legal system.
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
        """Recommend appropriate type of lawyer"""
        
        lawyer_mapping = {
            "criminal": "Criminal Defense Lawyer",
            "civil": "Civil Litigation Lawyer", 
            "family": "Family Law Lawyer",
            "commercial": "Corporate/Commercial Lawyer",
            "constitutional": "Constitutional Lawyer",
            "general": "General Practice Lawyer"
        }
        
        lawyer_type = lawyer_mapping.get(state["domain"], "General Practice Lawyer")
        
        # Add specific guidance
        lawyer_guidance = f"""
        Recommended Legal Representation: {lawyer_type}
        
        Why this specialization:
        - Specialized knowledge in {state["domain"]} law
        - Experience with similar cases
        - Understanding of relevant procedures
        
        What to look for:
        - Bar Council registration
        - Experience in {state["domain"]} cases
        - Good track record
        - Clear fee structure
        """
        
        state["lawyer_type"] = lawyer_guidance
        print(f"👩‍⚖️ Lawyer recommendation: {lawyer_type}")
        return state
    
    def _compile_response(self, state: LegalState) -> LegalState:
        """Compile final response"""
        
        final_response = f"""
        ## Legal Analysis & Advice

        **Query Domain:** {state["domain"].title()}
        **Confidence Level:** {state["confidence"].title()}

        ### Legal Analysis
        {state["legal_analysis"]}

        ### Recommendations
        {state["recommendations"]}

        ### Legal Representation
        {state["lawyer_type"]}

        ### Sources
        """
        
        if state["sources"]:
            final_response += "\nBased on the following legal documents:\n"
            for i, source in enumerate(state["sources"][:3], 1):
                final_response += f"{i}. {source['source_file']}\n"
        
        final_response += """
        
        ---
        **Disclaimer:** This is preliminary legal guidance based on available legal documents. 
        Always consult with a qualified Pakistani lawyer for specific legal advice.
        """
        
        state["final_response"] = final_response
        print("✅ Final response compiled")
        return state
 
    def _template_legal_analysis(self, state: LegalState) -> str:
        """Template analysis when LLM is not available"""
        if state["domain"] == "police_misconduct":
            return """
            Based on Pakistani law, police misconduct is addressed under multiple laws:

            **Pakistan Penal Code 1860:**
            - Section 355: Assault or criminal force otherwise than on grave provocation
            - Section 356: Assault or criminal force in attempt to commit theft of property carried by a person
            - Section 357: Assault or criminal force in attempt wrongfully to confine a person
            - Section 358: Assault or criminal force on grave provocation
            - Section 509: Word, gesture or act intended to insult the modesty of a woman

            **Police Order 2002:**
            - Provides mechanisms for complaints against police misconduct
            - Establishes accountability procedures

            **Constitutional Provisions:**
            - Article 4: Right to be treated in accordance with law
            - Article 9: Security of person
            - Article 14: Inviolability of dignity of man

            Police officers can be held accountable for excessive force or misconduct.
            """

        elif state["domain"] == "criminal":
            return """
            Based on Pakistani criminal law, accidental shooting cases are governed by the Pakistan Penal Code 1860.
            Key relevant sections:
            - Section 302: Punishment for intentional murder (Qatl-e-amd)
            - Section 304: Punishment for culpable homicide not amounting to murder (Qatl-e-khata)
            
            For accidental incidents, the court considers criminal intent and circumstances.
            """
        
        return f"""
        Based on the retrieved legal documents for your {state["domain"]} law query:
        Please consult the specific legal provisions and seek professional legal counsel.
        """

    def _template_recommendations(self, state: LegalState) -> str:
        """Template recommendations when LLM is not available"""
        if state["domain"] == "police_misconduct":
            return """
            IMMEDIATE ACTIONS FOR POLICE MISCONDUCT:

            1. **Preserve Evidence:**
            - Take photos of any injuries or marks
            - Save any video recordings from public or CCTV
            - Note the time, date, and location precisely

            2. **Document Details:**
            - Write down the officer's badge number, name, or physical description
            - Record names and contact information of witnesses
            - Document exactly what happened, word for word

            3. **File Official Complaints:**
            - Internal complaint with the police station's Senior Superintendent of Police (SSP)
            - Complaint with the District Police Complaints Authority
            - Application to the Human Rights Commission of Pakistan

            4. **Legal Actions:**
            - File FIR under relevant PPC sections (355, 357, etc.)
            - If police refuse FIR, approach the Judicial Magistrate
            - Consider filing a constitutional petition in High Court

            5. **Medical Documentation:**
            - Get medical examination from a government hospital
            - Obtain official medical report documenting injuries

            IMPORTANT: Do not confront the officer directly. Follow proper legal channels.
            """

        elif state["domain"] == "criminal":
            return """
            CRITICAL RECOMMENDATIONS FOR ACCIDENTAL SHOOTING:
            1. Do NOT go underground - surrender with a lawyer
            2. Preserve all evidence and document circumstances
            3. File FIR with factual details
            4. Apply for pre-arrest bail
            5. Contact criminal defense lawyer immediately
            """
        
        return f"""
        Recommended actions for your {state["domain"]} legal matter:
        1. Gather relevant documents and evidence
        2. Consult with a qualified {state["domain"]} lawyer
        3. Follow proper legal procedures
        """
        
    def process_legal_query(self, query: str) -> str:
            """Process a legal query through the workflow"""
            
            print(f"🚀 Processing legal query: {query[:50]}...")
            
            # Initialize state
            initial_state = LegalState(
                query=query,
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
                return f"Error processing your legal query: {str(e)}"

# Utility function to create agent
def create_legal_agent(llm:ChatGroq=ChatGroq(model="moonshotai/kimi-k2-instruct-0905", temperature=0,timeout=30), vector_store_path: str = "legal_vector_store") -> LegalAgent:
    """Create and return a legal agent instance"""
    return LegalAgent(llm=llm, vector_store_path=vector_store_path)

if __name__ == "__main__":
    # Test the agent
    agent = create_legal_agent()
    
    # Test queries
    test_queries = [
        "What is the punishment for theft in Pakistan under penal code?",
        "How can I file for divorce in Pakistan?",
        "What are property inheritance rights in Pakistan?"
    ]
    
    print("🧪 Testing Legal Agent...\n")
    
    for query in test_queries:
        print("=" * 60)
        response = agent.process_legal_query(query)
        print(response)
        print("\n")