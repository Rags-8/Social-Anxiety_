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
echo.
echo [INFO] Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

echo.
echo [INFO] Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo [INFO] Launching Streamlit...
:: Use 127.0.0.1 explicitly to avoid IPv6 issues
start http://127.0.0.1:8501
set API_URL=http://127.0.0.1:8000
python -m streamlit run streamlit_app.py --server.port 8501 --server.address 127.0.0.1
