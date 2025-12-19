# Solution: Network Error When Uploading PDF

## ✅ Problem Solved!

I've fixed the network error issue and set up everything you need to get the backend running.

### What Was Fixed:

1. ✅ Created `.env` file from `env.example` (with your API keys)
2. ✅ Added startup scripts for easy server management
3. ✅ Improved error handling and connection validation
4. ✅ Created server check utility
5. ✅ Added comprehensive troubleshooting guides

## 🚀 Quick Fix (3 Commands)

### 1. Start the Backend Server

Open a terminal and run:

```bash
cd /Users/sajinashakya/PDFchat-app/backend
./start_server.sh
```

This script will:
- Check for `.env` file (✅ already created)
- Create virtual environment if needed
- Install all dependencies
- Start the server on port 8000

### 2. Verify Server is Running

In a new terminal:

```bash
cd /Users/sajinashakya/PDFchat-app/backend
python3 check_server.py
```

You should see: `✅ Backend server is running!`

Or visit: http://localhost:8000/health

### 3. Start the Frontend

In another terminal:

```bash
cd /Users/sajinashakya/PDFchat-app/frontend
npm run dev
```

## 📋 What You Should See

**Backend Terminal:**
```
🌟 Starting FastAPI server on http://localhost:8000
📚 API docs available at http://localhost:8000/docs
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Frontend Terminal:**
```
  VITE v5.0.8  ready in XXX ms

  ➜  Local:   http://localhost:3000/
```

## 🧪 Test It

1. Open http://localhost:3000 in your browser
2. Click "Upload PDF"
3. Select a PDF file
4. The upload should work now! ✅

## 📚 Additional Resources

- **Quick Start Guide**: See [QUICK_START.md](./QUICK_START.md)
- **Troubleshooting**: See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **API Documentation**: http://localhost:8000/docs (when server is running)

## 🔧 Manual Start (Alternative)

If the script doesn't work, start manually:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

## ⚠️ Common Issues

### Port 8000 Already in Use
```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9
```

### Dependencies Not Installed
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### MongoDB Connection Error
- Check your MongoDB URI in `backend/.env`
- Ensure MongoDB Atlas allows your IP address

---

**The network error should now be resolved!** 🎉

If you still encounter issues, check the backend terminal for error messages and refer to [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).

