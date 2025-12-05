@echo off
echo ============================================================
echo           JUAN365 DATA REFRESH (Facebook API)
echo ============================================================
echo.
echo Fetching latest data from Facebook Graph API...
echo.
cd /d "%~dp0"

REM Run both fetchers
python api_fetcher.py
python refresh_api_cache.py

echo.
echo ============================================================
echo DATA REFRESH COMPLETE!
echo ============================================================
echo.
echo To update Streamlit Cloud, run:
echo   git add api_cache/ data/
echo   git commit -m "Update API data"
echo   git push
echo.
echo Refresh your browser at http://localhost:8501
echo.
pause
