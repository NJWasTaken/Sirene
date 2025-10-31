@echo off
echo =========================================
echo      Sirene Flask Application Starter    
echo =========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -q -r requirements.txt
echo Requirements installed.
echo.

echo =========================================
echo Starting Flask application...
echo =========================================
echo.
echo Access the application at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Start Flask app
python app.py

pause