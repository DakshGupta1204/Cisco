#!/bin/bash

# Aegis AI-Powered Self-Healing System Deployment Script
# Sets up environment variables and deploys the enhanced system

echo "🚀 Deploying Aegis AI-Powered Self-Healing System"
echo "================================================="

# Function to prompt for environment variables
prompt_for_env() {
    local var_name=$1
    local description=$2
    local default_value=$3
    
    if [ -n "$default_value" ]; then
        read -p "Enter $description ($var_name) [default: $default_value]: " input
        echo "${input:-$default_value}"
    else
        read -p "Enter $description ($var_name): " input
        echo "$input"
    fi
}

# Create .env file
echo "📝 Setting up environment variables..."

# Gemini AI Configuration
echo ""
echo "🧠 Gemini AI Configuration"
echo "-------------------------"
echo "To get your Gemini API key:"
echo "1. Go to https://makersuite.google.com/app/apikey"
echo "2. Create a new API key"
echo "3. Copy the key here"
echo ""

GEMINI_API_KEY=$(prompt_for_env "GEMINI_API_KEY" "Gemini AI API Key" "")

# Neo4j Configuration
echo ""
echo "🕸️ Neo4j Database Configuration"
echo "------------------------------"
echo "For Neo4j Aura (recommended):"
echo "1. Go to https://console.neo4j.io/"
echo "2. Create a new AuraDB instance"
echo "3. Copy the connection details"
echo ""

NEO4J_URI=$(prompt_for_env "NEO4J_URI" "Neo4j URI" "neo4j+s://your-database.databases.neo4j.io")
NEO4J_USER=$(prompt_for_env "NEO4J_USER" "Neo4j Username" "neo4j")
NEO4J_PASSWORD=$(prompt_for_env "NEO4J_PASSWORD" "Neo4j Password" "")

# MongoDB Configuration
echo ""
echo "🍃 MongoDB Configuration"
echo "----------------------"
echo "You can use MongoDB Atlas (cloud) or local MongoDB"
echo ""

MONGODB_URI=$(prompt_for_env "MONGODB_URI" "MongoDB URI" "mongodb://localhost:27017")
MONGODB_DATABASE=$(prompt_for_env "MONGODB_DATABASE" "MongoDB Database Name" "aegis_db")

# JWT Configuration
echo ""
echo "🔐 Security Configuration"
echo "------------------------"

JWT_SECRET=$(prompt_for_env "JWT_SECRET" "JWT Secret Key" "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM=$(prompt_for_env "JWT_ALGORITHM" "JWT Algorithm" "HS256")
JWT_EXPIRE_HOURS=$(prompt_for_env "JWT_EXPIRE_HOURS" "JWT Expiration Hours" "24")

# Server Configuration
echo ""
echo "⚙️ Server Configuration"
echo "---------------------"

SERVER_HOST=$(prompt_for_env "SERVER_HOST" "Server Host" "0.0.0.0")
SERVER_PORT=$(prompt_for_env "SERVER_PORT" "Server Port" "3001")
LOG_LEVEL=$(prompt_for_env "LOG_LEVEL" "Log Level" "INFO")

# Write .env file
cat > guardian-server/.env << EOF
# Aegis AI-Powered Self-Healing System Configuration
# Generated on $(date)

# === AI CONFIGURATION ===
GEMINI_API_KEY=$GEMINI_API_KEY

# === DATABASE CONFIGURATION ===
# Neo4j Graph Database
NEO4J_URI=$NEO4J_URI
NEO4J_USER=$NEO4J_USER
NEO4J_PASSWORD=$NEO4J_PASSWORD

# MongoDB
MONGODB_URI=$MONGODB_URI
MONGODB_DATABASE=$MONGODB_DATABASE

# === SECURITY CONFIGURATION ===
JWT_SECRET=$JWT_SECRET
JWT_ALGORITHM=$JWT_ALGORITHM
JWT_EXPIRE_HOURS=$JWT_EXPIRE_HOURS

# === SERVER CONFIGURATION ===
SERVER_HOST=$SERVER_HOST
SERVER_PORT=$SERVER_PORT
LOG_LEVEL=$LOG_LEVEL

# === CORS CONFIGURATION ===
CORS_ORIGINS=*
CORS_CREDENTIALS=true

# === AI CONFIGURATION OPTIONS ===
AI_CONFIDENCE_THRESHOLD=0.7
AI_MAX_RETRIES=3
AI_TIMEOUT_SECONDS=30

# === MONITORING CONFIGURATION ===
HEALTH_CHECK_INTERVAL=30
MIRROR_CHECK_INTERVAL=60
HEALING_TIMEOUT_MINUTES=30
EOF

echo "✅ Environment configuration saved to guardian-server/.env"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
cd guardian-server

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Install requirements
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Dependencies installed successfully"

# Test AI system
echo ""
echo "🧪 Testing AI System..."
cd ..
python test_ai_system.py

if [ $? -eq 0 ]; then
    echo "✅ AI system tests passed!"
else
    echo "⚠️ Some AI system tests failed. Check the logs for details."
fi

# Deploy with Docker (optional)
echo ""
read -p "Do you want to deploy with Docker? (y/N): " docker_deploy

if [[ $docker_deploy =~ ^[Yy]$ ]]; then
    echo "🐳 Building Docker image..."
    docker build -t aegis-guardian:latest .
    
    echo "🚀 Starting Docker container..."
    docker run -d \
        --name aegis-guardian \
        --env-file guardian-server/.env \
        -p 3001:3001 \
        aegis-guardian:latest
    
    echo "✅ Docker deployment completed!"
    echo "Guardian Server is running at http://localhost:3001"
else
    echo "🏃 Starting development server..."
    cd guardian-server
    python -m uvicorn app:app --host $SERVER_HOST --port $SERVER_PORT --reload &
    
    echo "✅ Development server started!"
    echo "Guardian Server is running at http://$SERVER_HOST:$SERVER_PORT"
    echo "API Documentation: http://$SERVER_HOST:$SERVER_PORT/docs"
fi

# Display next steps
echo ""
echo "🎯 Next Steps:"
echo "=============="
echo "1. Access the API documentation at http://localhost:3001/docs"
echo "2. Test the AI endpoints:"
echo "   - POST /ai/analyze/health/{agent_id}"
echo "   - POST /ai/mirror/recommend/{agent_id}"
echo "   - POST /ai/healing/strategy/{agent_id}"
echo "3. Monitor the system logs for AI activity"
echo "4. Set up your frontend to use the new AI endpoints"
echo ""
echo "📚 Documentation:"
echo "- AI Self-Healing Guide: AI_SELF_HEALING_GUIDE.md"
echo "- Attack Simulation API: ATTACK_SIMULATION_API.md"
echo "- Deployment Guide: DEPLOYMENT_GUIDE.md"
echo ""
echo "🛡️ Aegis AI-Powered Self-Healing System is now active!"
echo "   Intelligent node analysis ✅"
echo "   Smart mirror management ✅"
echo "   Autonomous healing strategies ✅"
echo "   Predictive failure detection ✅"
echo "   Graph database mirroring ✅"
echo ""
echo "Happy monitoring! 🚀"
