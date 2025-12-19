@echo off
REM PDF Chat Backend Startup Script for Windows

echo 🚀 Starting PDF Chat Backend Server...

REM Check if .env file exists
if not exist .env (
    echo ❌ Error: .env file not found!
    echo 📝 Creating .env from env.example...
    if exist env.example (
        copy env.example .env
        echo ✅ Created .env file. Please edit it with your API keys before running again.
        echo    Edit: backend\.env
        pause
        exit /b 1
    ) else (
        echo ❌ env.example file also not found!
        pause
        exit /b 1
    )
)

REM Check if virtual environment exists
if not exist venv (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Start the server
echo 🌟 Starting FastAPI server on http://localhost:8000
echo 📚 API docs available at http://localhost:8000/docs
echo.
uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause

