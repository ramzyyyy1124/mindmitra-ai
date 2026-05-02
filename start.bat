@echo off
echo Starting MindMitra AI...

echo Starting FastAPI Backend...
start cmd /k "uvicorn main:app --reload"

echo Starting React Frontend...
cd frontend
start cmd /k "npm run dev"

echo Both servers started!
echo Backend is running at: http://localhost:8000
echo Frontend is running at: http://localhost:5173
pause
