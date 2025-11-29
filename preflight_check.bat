@echo off
REM Drawing Studio - Pre-flight Check Script
REM Run this to verify your system is ready

echo.
echo ========================================
echo   Drawing Studio - Pre-flight Check
echo ========================================
echo.

REM Check Python
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found in PATH
    echo    Please install Python: https://www.python.org/
    echo    During installation, check "Add Python to PATH"
    pause
    exit /b 1
)
python --version
echo ✅ Python is installed
echo.

REM Check pip
echo [2/4] Checking pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip not found
    echo    Try: python -m pip install --upgrade pip
    pause
    exit /b 1
)
pip --version
echo ✅ pip is installed
echo.

REM Check if in correct directory
echo [3/4] Checking current directory...
if exist drawing_app.html (
    echo ✅ drawing_app.html found
) else (
    echo ⚠️  drawing_app.html not found
    echo    Make sure you're in the correct directory
)
if exist server.py (
    echo ✅ server.py found
) else (
    echo ⚠️  server.py not found
    echo    Make sure you're in the correct directory
)
echo.

REM Show next steps
echo [4/4] Next Steps:
echo.
echo 1. Install dependencies (first time only):
echo    pip install -r requirements.txt
echo.
echo 2. Start the server:
echo    python server.py
echo.
echo 3. Open drawing_app.html in your browser
echo.
echo ========================================
echo ✅ System is ready!
echo ========================================
echo.
pause
