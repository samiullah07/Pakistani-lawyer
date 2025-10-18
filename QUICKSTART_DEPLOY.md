# 🚀 QUICK DEPLOYMENT GUIDE

## ⚡ Deploy in 10 Minutes (FREE)

### **Step 1: Prepare Your Code (2 min)**

```bash
cd "C:\Users\BEST LAPTOP\Desktop\Pakistan Lawer"
python deploy_check.py
```

This checks if everything is ready. Fix any issues it finds.

---

### **Step 2: Push to GitHub (3 min)**

```bash
# Initialize git
git init
git add .
git commit -m "Pakistan Legal AI - Ready to deploy"

# Create repo on GitHub.com (name: pakistan-legal-ai)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/pakistan-legal-ai.git
git branch -M main
git push -u origin main
```

---

### **Step 3: Deploy Frontend on Streamlit Cloud (3 min)**

1. Go to https://share.streamlit.io
2. Click **"New app"**
3. Select your GitHub repo: `pakistan-legal-ai`
4. Settings:
   - **Main file:** `ui.py`
   - **Python version:** 3.11
5. **Advanced settings** → **Secrets**:
   ```toml
   API_URL = "http://localhost:8000"
   GROQ_API_KEY = os.getenv("GROQ_API_KEY")
   ```
6. Click **"Deploy"**

⏱️ Wait 5-7 minutes for build...

✅ **DONE!** Your UI is live at: `https://YOUR-APP.streamlit.app`

---

### **Step 4: Deploy Backend on Render (2 min)**

1. Go to https://render.com (sign up free)
2. Click **"New +" → "Web Service"**
3. Connect your GitHub repo
4. Settings:
   - **Name:** `pakistan-legal-api`
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables:**
   - `GROQ_API_KEY` = `os.getenv("GROQ_API_KEY")`
   - `PYTHON_VERSION` = `3.11.0`
6. Click **"Create Web Service"**

⏱️ Wait 10-15 minutes for build...

✅ **DONE!** Your API is live at: `https://pakistan-legal-api.onrender.com`

---

### **Step 5: Connect Frontend to Backend (1 min)**

Update Streamlit Cloud secrets:

1. Go to your Streamlit app dashboard
2. Settings → Secrets
3. Update:
   ```toml
   API_URL = "https://pakistan-legal-api.onrender.com"
   ```
4. Save & Reboot

---

## ✅ **YOU'RE LIVE!**

Share your chatbot:
- 🌐 **Live URL:** `https://your-app.streamlit.app`
- 🔗 **API:** `https://pakistan-legal-api.onrender.com`

---

## 🎯 **Testing Your Deployment:**

Visit your Streamlit URL and try:
- "Hello" → Should greet you
- "section 420 kya hai?" → Should provide legal analysis
- "I need a lawyer in Lahore" → Should show lawyers

---

## ⚠️ **Important Notes:**

### **Free Tier Limitations:**

**Streamlit Cloud:**
- ✅ Always active
- ✅ Unlimited usage
- ✅ 1GB RAM

**Render FREE:**
- ⚠️ Sleeps after 15min inactivity
- ⚠️ Takes 30-50s to wake up on first request
- ✅ Then works normally

### **Keep API Awake (Optional):**

Use a service like UptimeRobot to ping your API every 14 minutes:
1. Go to https://uptimerobot.com (free)
2. Add monitor: `https://pakistan-legal-api.onrender.com/health`
3. Check every 5 minutes

---

## 🐛 **Troubleshooting:**

### **Build Fails:**
- Check `requirements.txt` - all packages compatible?
- Check Python version matches `runtime.txt`

### **API Not Connecting:**
- Verify API_URL in Streamlit secrets
- Check API is running: visit `/health` endpoint

### **Slow First Response:**
- Normal! Render free tier wakes from sleep
- Takes 30-50s first time, then instant

### **Vector Store Error:**
- Make sure `legal_vector_store/` folder is in GitHub
- Or rebuild on first run (takes 2-3min)

---

## 💰 **Costs:**

- **Total:** $0.00 (100% FREE)
- **Streamlit Cloud:** Free forever
- **Render:** Free tier (with sleep)
- **No credit card needed!**

---

## 🚀 **Upgrade Options (Later):**

When ready for production:
- **Render Paid:** $7/month (no sleep, more resources)
- **Railway:** $5/month credit
- **Heroku:** $7/month

---

## 📞 **Need Help?**

- Check `DEPLOYMENT.md` for detailed guide
- Run `python deploy_check.py` to diagnose issues
- API docs: `https://your-api.onrender.com/docs`

---

**Ready? Start with Step 1! 🚀**
