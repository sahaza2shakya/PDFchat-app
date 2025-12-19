# Quick Start Guide

## Fix "Network Error" When Uploading PDF

### The Problem
You're seeing: `Error: Network error - please check if the backend server is running on http://localhost:8000`

This means the backend server is not running or not accessible.

### The Solution (3 Steps)

#### Step 1: Start the Backend Server

Open a terminal and run:

**Mac/Linux:**
```bash
cd /Users/sajinashakya/PDFchat-app/backend
./start_server.sh
```

**Windows:**
```bash
cd PDFchat-app\backend
start_server.bat
```

You should see:
```
🌟 Starting FastAPI server on http://localhost:8000
📚 API docs available at http://localhost:8000/docs
```

#### Step 2: Verify Backend is Running

Open a new terminal and run:
```bash
cd /Users/sajinashakya/PDFchat-app/backend
python3 check_server.py
```

Or visit in your browser:
- http://localhost:8000/health
- http://localhost:8000/docs

#### Step 3: Start the Frontend

Open another terminal and run:
```bash
cd /Users/sajinashakya/PDFchat-app/frontend
npm run dev
```

The frontend should start on http://localhost:3000

### Now Try Uploading a PDF

1. Go to http://localhost:3000
2. Click "Upload PDF"
3. Select a PDF file
4. Wait for processing

### If It Still Doesn't Work

1. **Check if port 8000 is in use:**
   ```bash
   lsof -i :8000  # Mac/Linux
   netstat -ano | findstr :8000  # Windows
   ```

2. **Kill any process using port 8000:**
   ```bash
   lsof -ti:8000 | xargs kill -9  # Mac/Linux
   ```

3. **Check backend logs** for error messages

4. **Verify .env file exists:**
   ```bash
   ls backend/.env  # Should show the file
   ```

5. **Check MongoDB connection:**
   - Verify MongoDB URI in `backend/.env`
   - Ensure MongoDB Atlas allows your IP address

### Need More Help?

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed solutions.

