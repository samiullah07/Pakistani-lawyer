# 🇵🇰 Pakistan Legal AI Assistant

An intelligent legal advice system powered by AI, specifically designed for Pakistani law. This system helps users get legal guidance, search through legal documents, and understand their rights under Pakistani law.

## 🚀 Features

- **💬 Chat Interface**: Natural language chat for legal queries
- **🔍 Document Search**: Search through Pakistani legal documents (Constitution, Penal Code, etc.)
- **⚖️ Legal Analysis**: AI-powered analysis of legal issues
- **👩‍⚖️ Lawyer Recommendations**: Suggests appropriate legal specialization
- **📚 Chat History**: Saves all conversations for future reference
- **🌐 Web Interface**: Easy-to-use web interface built with Streamlit

## 📁 Project Structure

```
Pakistan Lawer/
├── data_ingestion.py    # PDF processing and document loading
├── vector_store.py      # FAISS vector database management
├── retriever.py         # Document similarity search
├── agent.py            # LangGraph workflow for legal advice
├── api.py              # FastAPI backend endpoints
├── ui.py               # Streamlit frontend interface
├── main.py             # Command-line interface
├── start.py            # Startup script for both servers
├── requirements.txt    # Python dependencies
├── .env               # API keys (keep private)
├── Laws/              # PDF legal documents
└── legal_vector_store/ # Generated vector embeddings
```

## 🛠️ Installation & Setup

### 1. Clone or Download Project
```bash
cd "C:\Users\BEST LAPTOP\Desktop\Pakistan Lawer"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Add Legal Documents
- Your `Laws/` folder already contains Pakistani legal documents
- Add more PDFs as needed

### 4. Configure API Keys (Optional)
Edit `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_key_here
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

### Web Interface
1. Open http://localhost:8501
2. Type your legal question
3. Get AI-powered legal advice
4. View chat history in sidebar

### Example Questions
- "What is the punishment for theft in Pakistan?"
- "How do I file for divorce in Pakistan?"
- "What are property inheritance rights for daughters?"
- "Can I start a business as a student?"

### API Usage
```python
import requests

response = requests.post("http://localhost:8000/chat/message", 
                        json={"query": "What are my rights if arrested?"})
print(response.json())
```

## 🔧 Technical Details

### Core Components
- **LangChain**: Document processing and LLM integration
- **FAISS**: Vector similarity search
- **LangGraph**: Multi-agent workflow
- **FastAPI**: REST API backend
- **Streamlit**: Web interface
- **Groq**: Fast LLM inference (optional)

### Legal Documents Included
- Pakistan Penal Code (PPC 1860)
- Constitution of Pakistan (1973)
- Civil Procedure Code (CPC 1908)
- Criminal Procedure Code (CrPC 1898)
- Guardian and Wards Act (1890)
- Transfer of Property Act (TPA 1882)
- Specific Relief Act (1877)
- And more...

## 🛡️ Important Disclaimer

**This is an AI assistant providing general information about Pakistani law. It is NOT a substitute for professional legal advice. Always consult with a qualified Pakistani lawyer for specific legal matters.**

## 🔍 Troubleshooting

### Common Issues

1. **"Vector store not found"**
   - Run `python main.py` once to build the vector store

2. **"Cannot connect to API service"**
   - Make sure API server is running: `python api.py`

3. **"Missing package errors"**
   - Run: `pip install -r requirements.txt`

4. **LLM errors**
   - System works without LLM using template responses
   - Add GROQ_API_KEY to `.env` for better responses

## 📊 System Requirements

- Python 3.8+
- 4GB RAM minimum (8GB recommended)
- 2GB disk space for vector store
- Internet connection (for LLM API calls)

## 🔮 Future Enhancements

- [ ] Multi-language support (Urdu)
- [ ] Case law precedent search  
- [ ] Legal document generation
- [ ] Lawyer directory integration
- [ ] Mobile app version

## 🤝 Contributing

This is a learning project. Feel free to:
- Add more legal documents
- Improve the UI/UX
- Enhance the AI responses
- Fix bugs and issues

## 📜 License

Educational/Learning Project - Use responsibly

---

**Made with ❤️ for Pakistani legal education and accessibility**
