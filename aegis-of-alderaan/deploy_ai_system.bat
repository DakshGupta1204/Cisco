@echo off
REM Aegis AI-Powered Self-Healing System Deployment Script (Windows)
REM Sets up environment variables and deploys the enhanced system

echo.
echo 🚀 Deploying Aegis AI-Powered Self-Healing System
echo =================================================
echo.

REM Create .env file
echo 📝 Setting up environment variables...
echo.

echo 🧠 Gemini AI Configuration
echo -------------------------
echo To get your Gemini API key:
echo 1. Go to https://makersuite.google.com/app/apikey
echo 2. Create a new API key
echo 3. Copy the key here
echo.

set /p GEMINI_API_KEY="Enter Gemini AI API Key: "

echo.
echo 🕸️ Neo4j Database Configuration
echo ------------------------------
echo For Neo4j Aura (recommended):
echo 1. Go to https://console.neo4j.io/
echo 2. Create a new AuraDB instance
echo 3. Copy the connection details
echo.

set /p NEO4J_URI="Enter Neo4j URI [neo4j+s://your-database.databases.neo4j.io]: "
if "%NEO4J_URI%"=="" set NEO4J_URI=neo4j+s://your-database.databases.neo4j.io

set /p NEO4J_USER="Enter Neo4j Username [neo4j]: "
if "%NEO4J_USER%"=="" set NEO4J_USER=neo4j

set /p NEO4J_PASSWORD="Enter Neo4j Password: "

echo.
echo 🍃 MongoDB Configuration
echo ----------------------
echo You can use MongoDB Atlas (cloud) or local MongoDB
echo.

set /p MONGODB_URI="Enter MongoDB URI [mongodb://localhost:27017]: "
if "%MONGODB_URI%"=="" set MONGODB_URI=mongodb://localhost:27017

set /p MONGODB_DATABASE="Enter MongoDB Database Name [aegis_db]: "
if "%MONGODB_DATABASE%"=="" set MONGODB_DATABASE=aegis_db

echo.
echo 🔐 Security Configuration
echo ------------------------

set /p JWT_SECRET="Enter JWT Secret Key [your-super-secret-jwt-key-change-in-production]: "
if "%JWT_SECRET%"=="" set JWT_SECRET=your-super-secret-jwt-key-change-in-production

set /p JWT_ALGORITHM="Enter JWT Algorithm [HS256]: "
if "%JWT_ALGORITHM%"=="" set JWT_ALGORITHM=HS256

set /p JWT_EXPIRE_HOURS="Enter JWT Expiration Hours [24]: "
if "%JWT_EXPIRE_HOURS%"=="" set JWT_EXPIRE_HOURS=24

echo.
echo ⚙️ Server Configuration
echo ---------------------

set /p SERVER_HOST="Enter Server Host [0.0.0.0]: "
if "%SERVER_HOST%"=="" set SERVER_HOST=0.0.0.0

set /p SERVER_PORT="Enter Server Port [3001]: "
if "%SERVER_PORT%"=="" set SERVER_PORT=3001

set /p LOG_LEVEL="Enter Log Level [INFO]: "
if "%LOG_LEVEL%"=="" set LOG_LEVEL=INFO

REM Write .env file
echo Writing configuration to guardian-server\.env...

(
echo # Aegis AI-Powered Self-Healing System Configuration
echo # Generated on %date% %time%
echo.
echo # === AI CONFIGURATION ===
echo GEMINI_API_KEY=%GEMINI_API_KEY%
echo.
echo # === DATABASE CONFIGURATION ===
echo # Neo4j Graph Database
echo NEO4J_URI=%NEO4J_URI%
echo NEO4J_USER=%NEO4J_USER%
echo NEO4J_PASSWORD=%NEO4J_PASSWORD%
echo.
echo # MongoDB
echo MONGODB_URI=%MONGODB_URI%
echo MONGODB_DATABASE=%MONGODB_DATABASE%
echo.
echo # === SECURITY CONFIGURATION ===
echo JWT_SECRET=%JWT_SECRET%
echo JWT_ALGORITHM=%JWT_ALGORITHM%
echo JWT_EXPIRE_HOURS=%JWT_EXPIRE_HOURS%
echo.
echo # === SERVER CONFIGURATION ===
echo SERVER_HOST=%SERVER_HOST%
echo SERVER_PORT=%SERVER_PORT%
echo LOG_LEVEL=%LOG_LEVEL%
echo.
echo # === CORS CONFIGURATION ===
echo CORS_ORIGINS=*
echo CORS_CREDENTIALS=true
echo.
echo # === AI CONFIGURATION OPTIONS ===
echo AI_CONFIDENCE_THRESHOLD=0.7
echo AI_MAX_RETRIES=3
echo AI_TIMEOUT_SECONDS=30
echo.
echo # === MONITORING CONFIGURATION ===
echo HEALTH_CHECK_INTERVAL=30
echo MIRROR_CHECK_INTERVAL=60
echo HEALING_TIMEOUT_MINUTES=30
) > guardian-server\.env

echo ✅ Environment configuration saved to guardian-server\.env
echo.

REM Install dependencies
echo 📦 Installing dependencies...
cd guardian-server

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Dependencies installed successfully
echo.

REM Test AI system
echo 🧪 Testing AI System...
cd ..
python test_ai_system.py

if %errorlevel% equ 0 (
    echo ✅ AI system tests passed!
) else (
    echo ⚠️ Some AI system tests failed. Check the logs for details.
)

echo.
set /p docker_deploy="Do you want to deploy with Docker? (y/N): "

if /i "%docker_deploy%"=="y" (
    echo 🐳 Building Docker image...
    docker build -t aegis-guardian:latest .
    
    echo 🚀 Starting Docker container...
    docker run -d --name aegis-guardian --env-file guardian-server\.env -p 3001:3001 aegis-guardian:latest
    
    echo ✅ Docker deployment completed!
    echo Guardian Server is running at http://localhost:3001
) else (
    echo 🏃 Starting development server...
    cd guardian-server
    start /b python -m uvicorn app:app --host %SERVER_HOST% --port %SERVER_PORT% --reload
    
    echo ✅ Development server started!
    echo Guardian Server is running at http://%SERVER_HOST%:%SERVER_PORT%
    echo API Documentation: http://%SERVER_HOST%:%SERVER_PORT%/docs
)

REM Display next steps
echo.
echo 🎯 Next Steps:
echo ==============
echo 1. Access the API documentation at http://localhost:3001/docs
echo 2. Test the AI endpoints:
echo    - POST /ai/analyze/health/{agent_id}
echo    - POST /ai/mirror/recommend/{agent_id}
echo    - POST /ai/healing/strategy/{agent_id}
echo 3. Monitor the system logs for AI activity
echo 4. Set up your frontend to use the new AI endpoints
echo.
echo 📚 Documentation:
echo - AI Self-Healing Guide: AI_SELF_HEALING_GUIDE.md
echo - Attack Simulation API: ATTACK_SIMULATION_API.md
echo - Deployment Guide: DEPLOYMENT_GUIDE.md
echo.
echo 🛡️ Aegis AI-Powered Self-Healing System is now active!
echo    Intelligent node analysis ✅
echo    Smart mirror management ✅
echo    Autonomous healing strategies ✅
echo    Predictive failure detection ✅
echo    Graph database mirroring ✅
echo.
echo Happy monitoring! 🚀
echo.
pause
