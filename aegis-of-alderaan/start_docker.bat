@echo off
echo 🚀 Starting Docker Desktop...
echo.

REM Try to start Docker Desktop
echo Starting Docker Desktop application...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

echo.
echo ⏳ Waiting for Docker Desktop to start...
echo This may take 30-60 seconds...
echo.

REM Wait for Docker to be available
:wait_loop
timeout /t 5 /nobreak >nul
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo Still waiting for Docker...
    goto wait_loop
)

echo.
echo ✅ Docker Desktop is now running!
echo.
echo 🛡️ Ready to deploy Aegis of Alderaan!
echo.
echo Run this command to deploy:
echo   python deploy_complete.py
echo.
pause
