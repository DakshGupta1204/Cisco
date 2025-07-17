#!/usr/bin/env python3
"""
Aegis of Alderaan Guardian Server - Startup Script
Quick start script for the Guardian server
"""

import sys
import os
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if requirements_file.exists():
        print("Installing Guardian server dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
    else:
        print("requirements.txt not found")

def check_database_connections():
    """Check if databases are available"""
    print("Checking database connections...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    import os
    
    # Debug: Show environment variables
    mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'password')
    
    print(f"🔧 MongoDB URI: {mongodb_uri[:50]}...")
    print(f"🔧 Neo4j URI: {neo4j_uri}")
    
    # Check MongoDB
    try:
        import pymongo
        client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        client.close()
    except ImportError:
        print("⚠️  PyMongo not installed - install with: pip install pymongo")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
    
    # Check Neo4j (optional)
    try:
        from neo4j import GraphDatabase
        # Configure driver based on URI scheme
        driver_config = {"auth": (neo4j_user, neo4j_password)}
        if neo4j_uri.startswith(('bolt://', 'neo4j://')):
            driver_config["encrypted"] = True
        
        driver = GraphDatabase.driver(neo4j_uri, **driver_config)
        with driver.session() as session:
            session.run("RETURN 1")
        print("✅ Neo4j connection successful")
        driver.close()
    except ImportError:
        print("⚠️  Neo4j driver not installed - install with: pip install neo4j")
    except Exception as e:
        print(f"⚠️  Neo4j connection failed: {e}")

def main():
    """Main startup function"""
    print("=" * 60)
    print("🛡️  Aegis of Alderaan - Guardian Server Startup")
    print("=" * 60)
    
    # Check if dependencies need to be installed
    try:
        import fastapi
        import uvicorn
        print("✅ Core dependencies available")
    except ImportError as e:
        print(f"Missing core dependency: {e}")
        print("Installing dependencies...")
        install_dependencies()
    
    # Check optional dependencies
    try:
        import motor
        print("✅ MongoDB driver available")
    except ImportError:
        print("⚠️  Motor (MongoDB driver) not available - install with: pip install motor")
    
    try:
        import neo4j
        print("✅ Neo4j driver available")
    except ImportError:
        print("⚠️  Neo4j driver not available - install with: pip install neo4j")
    
    try:
        import jwt
        print("✅ JWT library available")
    except ImportError:
        print("⚠️  PyJWT not available - install with: pip install PyJWT")
    
    # Check database connections
    check_database_connections()
    
    # Start the server
    try:
        print("🚀 Starting Guardian Server...")
        print("📊 Dashboard will be available at: http://localhost:3001")
        print("🔌 WebSocket endpoints:")
        print("   - Agents: ws://localhost:3001/ws/agent")
        print("   - Dashboard: ws://localhost:3001/ws/dashboard")
        print("📖 API Documentation: http://localhost:3001/docs")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 60)
        
        # Import and run the FastAPI app
        import uvicorn
        uvicorn.run(
            "app:app",
            host="0.0.0.0",
            port=3001,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Guardian Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting Guardian server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
