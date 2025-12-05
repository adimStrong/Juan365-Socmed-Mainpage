@echo off
echo ============================================================
echo           JUAN365 DATA REFRESH (Facebook API)
echo ============================================================
echo.
echo Fetching latest data from Facebook Graph API...
echo This may take 2-3 minutes...
echo.
cd /d "%~dp0"
python api_fetcher.py
echo.
echo ============================================================
echo DATA REFRESH COMPLETE!
echo ============================================================
echo.
echo Refresh your browser at http://localhost:8501
echo Or run START_STREAMLIT.bat to start the dashboard
echo.
pause
