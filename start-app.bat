@echo off
echo ====================================================
echo Starting AI Resume Analyzer (Backend + Frontend)
echo ====================================================

echo Starting FastAPI Backend on http://localhost:8000 ...
start "FastAPI Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --port 8000"

ping -n 3 127.0.0.1 >nul 2>&1

echo Starting Vite Frontend on http://localhost:5173 ...
start "Vite Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both services launched!
echo Open your browser at: http://localhost:5173
echo ====================================================
