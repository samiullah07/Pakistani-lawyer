# 🇵🇰 Pakistan Legal AI Assistant - Sami Ullah AI

An intelligent, bilingual (English/Urdu) legal assistant powered by AI, specifically designed for Pakistani law. This system helps users get professional legal guidance, search through legal documents, and understand their rights under Pakistani law with a friendly, agentic approach.

## 🚀 Key Features

- **🌐 Bilingual Support**: Automatically switches between English and Urdu based on your input
- **🤖 Agentic Behavior**: Intelligent conversation that asks clarifying questions and reasons step-by-step
- **💬 Dual Mode**:
  - **Casual Chat**: Friendly, warm responses for greetings and general conversation
  - **Legal Queries**: Professional, structured legal analysis with practical advice
- **⚖️ Comprehensive Legal Analysis**:
  - Applicable laws and sections
  - Key legal text (simplified)
  - Punishment & category details
  - Practical implications
  - Actionable suggestions
- **👩‍⚖️ Smart Lawyer Recommendations**: Suggests appropriate legal specialization
- **📚 Chat History**: Saves all conversations for future reference
- **🌐 Modern Web Interface**: Clean, professional UI built with Streamlit

## 🎯 Core Behavior

### Professional & Friendly
- Professional, clear, empathetic, and concise legal guidance
- Friendly & casual for general conversation
- Automatic language switching (English ↔ Urdu)

### Conversation Modes

**1. General Chat**
```
User: "Hi, how are you?"
Bot: "I'm doing well, thanks! I'm Sami Ullah AI, your Pakistani Legal Assistant. 
      How are you today?"
```

**2. Legal Query**
```
User: "What is section 420 in Pakistan?"
Bot: 
Applicable Law & Section: Pakistan Penal Code (PPC) Section 420 – Cheating
Text: Whoever cheats and dishonestly induces someone to deliver property...
Punishment: Up to 7 years imprisonment + fine
Category: Cognizable, non-bailable, non-compoundable
Practical Note: This applies to fraud cases. Victims may lodge an FIR.
```

**3. Bilingual Support**
```
User: "Salam, section 302 kya hai?"
Bot: [Responds in Urdu with full legal analysis]
```

### Agentic Intelligence
- Asks clarifying questions when queries are vague
- Provides step-by-step reasoning
- Suggests next actions (FIR, lawyer consultation, bail info)
- Understands context and intent

## 📁 Project Structure

```
Law2.0/
├── data_ingestion.py          # PDF processing and document loading
├── vector_store.py            # FAISS vector database management
├── retriever.py               # Document similarity search
├── agent.py                   # Bilingual LangGraph workflow (NEW!)
├── api.py                     # FastAPI backend endpoints
├── ui.py                      # Modern Streamlit UI
├── main.py                    # Command-line interface
├── start.py                   # Startup script for both servers
├── lawyer_directory.py        # Lawyer directory integration
├── requirements.txt           # Python dependencies
├── .env                       # API keys (keep private)
├── Laws/                      # PDF legal documents
└── legal_vector_store/        # Generated vector embeddings
```

## 🛠️ Installation & Setup

### 1. Navigate to Project
```bash
cd "C:\Users\BEST LAPTOP\Desktop\Law2.0"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Legal Documents
- Your `Laws/` folder contains Pakistani legal documents
- Add more PDFs as needed

### 4. Configure API Keys
Edit `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
```

## 🚀 How to Run

### Option 1: Quick Start (Recommended)
```bash
python start.py
```
This starts both API server and web interface automatically.

### Option 2: Manual Start
```bash
# Terminal 1 - Start API
python api.py

# Terminal 2 - Start Web Interface  
streamlit run ui.py
```

### Option 3: Command Line Interface
```bash
python main.py
```

## 🌐 Access Points

- **Web Interface**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 💡 Usage Examples

### English Queries
```
"What is the punishment for theft in Pakistan?"
"How do I file for divorce in Pakistan?"
"What are property inheritance rights for daughters?"
"Section 420 PPC"
"Can police arrest without warrant?"
```

### Urdu Queries (Roman Script)
```
"Section 302 kya hai?"
"Talaq ka qanoon kya hai Pakistan mein?"
"Chori ki saza kya hai?"
"Police ke ikhtiyarat kya hain?"
```

### Casual Conversation
```
English: "Hi, how are you?" / "Thank you" / "Who are you?"
Urdu: "Salam" / "Kaise ho?" / "Shukriya" / "Aap kaun hain?"
```

### API Usage
```python
import requests

# English query
response = requests.post("http://localhost:8000/chat/message", 
                        json={"query": "What is section 420?"})

# Urdu query
response = requests.post("http://localhost:8000/chat/message", 
                        json={"query": "Section 302 kya hai?"})

# Casual chat
response = requests.post("http://localhost:8000/chat/message", 
                        json={"query": "Hi, how are you?"})

print(response.json())
```

## 🔧 Technical Details

### Core Components
- **LangChain**: Document processing and LLM integration
- **FAISS**: Vector similarity search
- **LangGraph**: Multi-agent workflow with bilingual support
- **FastAPI**: REST API backend
- **Streamlit**: Modern web interface
- **Groq**: Fast LLM inference (Llama 3.3 70B)

### Legal Documents Included
- Pakistan Penal Code (PPC 1860)
- Constitution of Pakistan (1973)
- Civil Procedure Code (CPC 1908)
- Criminal Procedure Code (CrPC 1898)
- Guardian and Wards Act (1890)
- Transfer of Property Act (TPA 1882)
- Specific Relief Act (1877)
- And more...

## 🎭 How It Works

### 1. Language Detection
- Automatically detects English or Urdu (including Roman Urdu)
- Maintains consistent language throughout the conversation

### 2. Intent Recognition
- Distinguishes between casual chat and legal queries
- Routes to appropriate conversation handler

### 3. Legal Query Processing
- Classifies query into legal domain (criminal, civil, family, etc.)
- Retrieves relevant legal context from vector store
- Analyzes using LLM with structured prompts
- Generates practical recommendations
- Suggests appropriate lawyer type

### 4. Response Structure
For legal queries, always provides:
- **Applicable Law & Section**: Exact law and section numbers
- **Legal Text**: Simplified explanation
- **Punishment & Category**: Bailable/non-bailable, etc.
- **Practical Implications**: Real-world meaning
- **Suggestions**: Next steps and actions

## 🛡️ Important Disclaimer

**This is an AI assistant providing general information about Pakistani law. It is NOT a substitute for professional legal advice. Always consult with a qualified Pakistani lawyer for specific legal matters.**

**Sami Ullah AI is an AI assistant for legal research, not a lawyer.**

## 🔍 Troubleshooting

### Common Issues

1. **"Vector store not found"**
   - Run `python main.py` once to build the vector store from PDFs

2. **"Cannot connect to API service"**
   - Make sure API server is running: `python api.py`
   - Or use: `python start.py` to start both services

3. **"Missing package errors"**
   - Run: `pip install -r requirements.txt`

4. **LLM errors**
   - System works without LLM using template responses
   - Add GROQ_API_KEY to `.env` for AI-powered responses
   - Get free API key from: https://console.groq.com

5. **Bilingual responses not working**
   - Make sure you're using the updated `agent.py`
   - Check that language detection is working (logs show detected language)

## 📊 System Requirements

- Python 3.8+
- 4GB RAM minimum (8GB recommended)
- 2GB disk space for vector store
- Internet connection (for LLM API calls)

## 🆕 What's New

### Version 2.0 - Bilingual Agentic Assistant
- ✅ Full English/Urdu bilingual support
- ✅ Agentic conversation behavior
- ✅ Casual chat vs legal query detection
- ✅ Structured legal analysis format
- ✅ Step-by-step reasoning
- ✅ Clarifying questions for vague queries
- ✅ Professional, empathetic tone
- ✅ Improved LLM prompting (Llama 3.3 70B)

## 🔮 Future Enhancements

- [ ] Full Urdu script support (currently Roman Urdu)
- [ ] Case law precedent search  
- [ ] Legal document generation
- [ ] Voice input/output in both languages
- [ ] Mobile app version
- [ ] Multi-turn conversation memory
- [ ] Lawyer directory with real contacts

## 🤝 Contributing

This is a learning project. Feel free to:
- Add more legal documents
- Improve language detection
- Enhance the UI/UX
- Add more languages
- Improve AI responses
- Fix bugs and issues

## 👨‍💻 Developer Notes

### Testing the Agent
```bash
python agent.py
```
This runs built-in tests for both English and Urdu queries.

### Customizing Responses
Edit `agent.py`:
- Modify `_handle_casual_chat()` for casual responses
- Update `_analyze_legal_issue()` prompts for legal analysis
- Adjust `_template_legal_analysis()` for fallback responses

### Adding New Languages
1. Update `_detect_language()` in `agent.py`
2. Add language-specific prompts in analysis functions
3. Update casual chat responses
4. Test thoroughly

## 📜 License

Educational/Learning Project - Use responsibly

---

**Made with ❤️ by Sami Ullah for Pakistani legal education and accessibility**

**Disclaimer**: I am Sami Ullah AI, an AI assistant specialized in Pakistani law. I provide legal information and guidance, but I am not a lawyer. For specific legal advice, please consult a qualified Pakistani legal professional.
