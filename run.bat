@echo off
echo Installing requirements... If it fails due to network, it will automatically retry.

:retry_install
.venv\Scripts\python -m pip install --default-timeout=100 -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo Network error detected. Retrying installation...
    timeout /t 3
    goto retry_install
)

echo Installation successful! Starting the application...
.venv\Scripts\python -m streamlit run app.py
