@echo off
REM Drawing Studio - Windows Startup Script

echo.
echo ========================================
echo    Drawing Studio - Setup & Launch
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo [✓] Python found
echo.

REM Install dependencies if needed
echo Installing/Updating dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [WARNING] Some packages may not have installed. Continuing anyway...
)

echo [✓] Dependencies installed
echo.

REM Launch server
echo ========================================
echo    Starting Flask Server...
echo ========================================
echo.
echo Server will start on: http://localhost:5000
echo Drawing App: Open drawing_app.html in your browser
echo.
echo Press Ctrl+C to stop the server
echo.
pause

python server.py
