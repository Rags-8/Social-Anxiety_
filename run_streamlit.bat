@echo off
echo Starting Streamlit App for Social Anxiety Detection...
echo.

rem Check if virtual environment exists and activate it if so
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating .venv
    call ".venv\Scripts\activate.bat"
)

echo [INFO] Installing/Updating dependencies...
pip install -r requirements.txt

echo.
echo [INFO] Starting Backend Server...
start "Backend Server" cmd /k "python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"

timeout /t 5 /nobreak >nul

echo.
echo [INFO] Launching Streamlit...
start http://localhost:8501
set API_URL=http://127.0.0.1:8000
python -m streamlit run streamlit_app.py --server.headless true
pause
