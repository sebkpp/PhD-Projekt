@echo off
echo ============================================
echo  VR Study Management - Starting App
echo ============================================
echo.

if not exist "Backend\.env" (
    echo [ERROR] Backend\.env not found. Run setup_windows.bat first.
    pause
    exit /b 1
)

echo Starting backend on http://localhost:5000 ...
start "Backend" cmd /k "uv run fastapi dev Backend/app.py"

echo Starting frontend on http://localhost:5173 ...
start "Frontend" cmd /k "npm run dev"

echo.
echo Both services are starting in separate windows.
echo Open http://localhost:5173 in your browser once both are ready.
echo.
pause
