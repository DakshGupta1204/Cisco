# Aegis of Alderaan Guardian Server Configuration
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Server Configuration
SERVER_HOST = os.getenv("GUARDIAN_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("GUARDIAN_PORT", "8000"))

# Database Configuration - Cloud Ready
MONGODB_URL = os.getenv("MONGODB_URI", "mongodb+srv://your-username:your-password@your-cluster.xxxxx.mongodb.net/aegis-guardian?retryWrites=true&w=majority")
NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://your-database-id.databases.neo4j.io")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your-password")

# Security Configuration
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "aegis-guardian-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRY = int(os.getenv("JWT_EXPIRATION_HOURS", "24")) * 3600

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "guardian.log")

# Monitoring Configuration
HEALTH_CHECK_INTERVAL = 60
CLEANUP_INTERVAL = 86400  # 24 hours
OLD_DATA_RETENTION_DAYS = 30

# Debug Configuration
DEBUG = os.getenv("GUARDIAN_DEBUG", "false").lower() == "true"
