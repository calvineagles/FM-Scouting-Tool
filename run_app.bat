@echo off
echo Setting up FM Scouting Tool...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Run the Flask app
echo Starting Flask app...
echo.
echo The app will be available at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause 