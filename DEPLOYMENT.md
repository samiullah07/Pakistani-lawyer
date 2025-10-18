# 🚀 Deployment Guide - Pakistan Legal AI Chatbot

## FREE Hosting Options for Testing

### ✅ **OPTION 1: Streamlit Cloud (Recommended - Easiest)**

**Best for:** Quick testing with UI
**Cost:** FREE forever
**Steps:**

1. **Prepare Your Code:**
   - Your code is ready! ✅

2. **Create GitHub Repository:**
   ```bash
   cd "C:\Users\BEST LAPTOP\Desktop\Pakistan Lawer"
   git init
   git add .
   git commit -m "Initial commit - Pakistan Legal AI"
   ```

3. **Push to GitHub:**
   - Create a new repository on https://github.com
   - Name it: `pakistan-legal-ai`
   - Run:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/pakistan-legal-ai.git
   git branch -M main
   git push -u origin main
   ```

4. **Deploy on Streamlit Cloud:**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Connect your GitHub repo
   - Set:
     - Main file: `ui.py`
     - Python version: 3.11
     - Advanced: Add API URL in secrets

5. **Add Secrets (API Keys):**
   - In Streamlit Cloud dashboard → Settings → Secrets
   - Add:
   ```toml
   GROQ_API_KEY = "your_groq_key_here"
   OPENAI_API_KEY = "your_openai_key_here"
   ```

6. **Deploy!** 🎉
   - Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

**⚠️ LIMITATION:** Streamlit Cloud runs only the UI. For full functionality, you need backend deployment.

---

### ✅ **OPTION 2: Full Stack Deployment (UI + Backend)**

#### **Backend on Render (FREE):**

1. **Go to https://render.com** and sign up

2. **Create New Web Service:**
   - Connect your GitHub repo
   - Name: `pakistan-legal-api`
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables:**
   - `GROQ_API_KEY`: your key
   - `OPENAI_API_KEY`: your key
   - `PYTHON_VERSION`: 3.11.0

4. **Deploy Backend** - You'll get a URL like:
   `https://pakistan-legal-api.onrender.com`

#### **Frontend on Streamlit Cloud:**

1. **Update `ui.py` to use deployed API:**
   - Change `API_BASE_URL`:
   ```python
   API_BASE_URL = "https://pakistan-legal-api.onrender.com"
   ```

2. **Deploy UI on Streamlit Cloud** (follow steps from Option 1)

---

### ✅ **OPTION 3: Railway (Alternative - Simpler)**

1. **Go to https://railway.app** and sign up

2. **Deploy Backend:**
   - New Project → Deploy from GitHub
   - Select your repo
   - Railway auto-detects FastAPI
   - Add environment variables

3. **Deploy Frontend:**
   - Use Streamlit Cloud as above
   - OR deploy on Railway too (separate service)

---

## 📋 **Pre-Deployment Checklist:**

### **1. Update API URL in ui.py:**

For deployment, change this line in `ui.py`:
```python
# Change from:
API_BASE_URL = "http://localhost:8000"

# To your deployed API URL:
API_BASE_URL = "https://your-api-url.onrender.com"
```

### **2. Verify Files:**

Make sure you have:
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - For Render/Railway
- ✅ `runtime.txt` - Python version
- ✅ `.streamlit/config.toml` - Streamlit config
- ✅ All Python files
- ✅ Laws folder with PDFs

### **3. Environment Variables Needed:**

```
GROQ_API_KEY= = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

```

---

## 🎯 **Recommended Approach for Quick Testing:**

**EASIEST PATH (UI Only):**

1. Deploy just the UI on Streamlit Cloud
2. Keep API running locally OR use a simple backend service
3. Test with users

**COMPLETE PATH (Full Stack):**

1. Backend on Render (FREE tier - sleeps after 15min inactivity)
2. Frontend on Streamlit Cloud (FREE forever)
3. Both connected via API URL

---

## ⚠️ **Important Notes:**

### **Free Tier Limitations:**

**Render FREE:**
- ✅ Unlimited hours
- ❌ Sleeps after 15min inactivity (wakes on request - 30s delay)
- ✅ 512MB RAM
- ✅ 0.1 CPU

**Streamlit Cloud FREE:**
- ✅ Unlimited public apps
- ✅ Always active
- ✅ 1GB RAM
- ✅ 1 CPU core

**Railway FREE:**
- ✅ $5 free credit/month
- ✅ Good for testing
- ❌ Requires credit card

### **Handling Vector Store:**

For deployment, you have 2 options:

**Option A (Recommended):** Pre-build vector store
- Build locally: `python vector_store.py`
- Include `legal_vector_store/` folder in GitHub
- Faster startup on deployment

**Option B:** Build on first run
- Takes 2-3 minutes on first request
- Uses more resources

---

## 🚀 **Quick Start Commands:**

### **1. Prepare for GitHub:**
```bash
cd "C:\Users\BEST LAPTOP\Desktop\Pakistan Lawer"
git init
git add .
git commit -m "Pakistan Legal AI - Ready for deployment"
```

### **2. Create .gitignore:**
```bash
echo "__pycache__/
*.pyc
.env
.venv/
*.log" > .gitignore
```

### **3. Push to GitHub:**
```bash
# Create repo on GitHub first, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### **4. Deploy on Streamlit Cloud:**
- Visit: https://share.streamlit.io
- Connect GitHub
- Deploy `ui.py`
- ✅ DONE!

---

## 🎉 **After Deployment:**

Your chatbot will be live at URLs like:
- **UI:** `https://pakistan-legal-ai.streamlit.app`
- **API:** `https://pakistan-legal-api.onrender.com`

Share these links for testing!

---

## 🆘 **Need Help?**

Common issues:

1. **Build fails:** Check `requirements.txt` versions
2. **API not connecting:** Update `API_BASE_URL` in `ui.py`
3. **Slow response:** Free tier wakes from sleep (30s first request)
4. **Vector store missing:** Include folder in GitHub OR rebuild on startup

---

## 💡 **Pro Tips:**

1. **Keep vector store in repo** - Faster deployment
2. **Use Render for API** - Most reliable free tier
3. **Monitor usage** - Stay within free limits
4. **Add health check** - Prevent API from sleeping (Render)
5. **Test locally first** - Ensure everything works

---

Ready to deploy? Follow Option 1 for quickest results! 🚀
