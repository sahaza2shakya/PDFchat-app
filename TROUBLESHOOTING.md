# Troubleshooting Guide

## Network Error: "Backend server is not running"

If you see this error when uploading a PDF, follow these steps:

### Step 1: Check if Backend is Running

**Option A: Use the check script**
```bash
cd backend
python3 check_server.py
```

**Option B: Manual check**
```bash
curl http://localhost:8000/health
```

If you get a connection error, the backend is not running.

### Step 2: Start the Backend Server

**Mac/Linux:**
```bash
cd backend
./start_server.sh
```

**Windows:**
```bash
cd backend
start_server.bat
```

**Manual start:**
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

### Step 3: Verify Backend is Running

You should see:
- Server running on `http://localhost:8000`
- API docs at `http://localhost:8000/docs`
- Health check at `http://localhost:8000/health`

### Step 4: Check Frontend Configuration

Ensure your frontend is configured to connect to the backend:
- Frontend should be on `http://localhost:3000` (Vite default)
- Backend should be on `http://localhost:8000`
- CORS is configured for these origins

### Common Issues

#### 1. Port 8000 Already in Use
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9  # Mac/Linux
# Or on Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### 2. Missing .env File
```bash
cd backend
cp env.example .env
# Edit .env with your API keys
```

#### 3. Virtual Environment Not Activated
```bash
cd backend
source venv/bin/activate  # Mac/Linux
# Or
venv\Scripts\activate  # Windows
```

#### 4. Dependencies Not Installed
```bash
cd backend
pip install -r requirements.txt
```

#### 5. MongoDB Connection Error
- Check your MongoDB URI in `.env`
- Ensure MongoDB Atlas allows connections from your IP
- Verify network access in MongoDB Atlas dashboard

#### 6. OpenAI API Key Error
- Verify your API key in `.env`
- Check if you have sufficient credits
- Ensure the key has proper permissions

### Quick Test

1. **Backend health check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test upload endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/upload-pdf \
     -F "file=@test.pdf"
   ```

3. **Check browser console:**
   - Open browser DevTools (F12)
   - Check Console tab for errors
   - Check Network tab for failed requests

### Still Having Issues?

1. Check backend logs for error messages
2. Check browser console for frontend errors
3. Verify all environment variables are set correctly
4. Ensure both frontend and backend are running
5. Check firewall/antivirus isn't blocking connections

