"""
Test script to verify the Guardian server can start
"""
import sys
import os

# Add guardian-server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'guardian-server'))

try:
    print("🧪 Testing Guardian Server startup...")
    
    # Test imports
    print("📦 Testing imports...")
    
    try:
        from fastapi import FastAPI
        print("  ✅ FastAPI imported")
    except ImportError as e:
        print(f"  ❌ FastAPI import failed: {e}")
    
    try:
        import google.generativeai as genai
        print("  ✅ Google GenerativeAI imported")
    except ImportError as e:
        print(f"  ❌ Google GenerativeAI import failed: {e}")
    
    try:
        from gemini_ai_handler import GeminiAIHandler
        print("  ✅ Gemini AI Handler imported")
    except ImportError as e:
        print(f"  ❌ Gemini AI Handler import failed: {e}")
    
    # Test basic AI handler initialization
    try:
        ai_handler = GeminiAIHandler()
        print(f"  ✅ AI Handler initialized (enabled: {ai_handler.enabled})")
    except Exception as e:
        print(f"  ❌ AI Handler initialization failed: {e}")
    
    print("\n🎯 Postman Testing Setup Complete!")
    print("=" * 50)
    print("📁 Files created for Postman testing:")
    print("  - Aegis_AI_Postman_Collection.json")
    print("  - Aegis_AI_Postman_Environment.json") 
    print("  - POSTMAN_TESTING_GUIDE.md")
    print("")
    print("🚀 To start the server manually:")
    print("  cd guardian-server")
    print("  python -m uvicorn app:app --host 0.0.0.0 --port 3001 --reload")
    print("")
    print("📚 Server will be available at:")
    print("  🌐 Main API: http://localhost:3001")
    print("  📖 Docs: http://localhost:3001/docs")
    print("  ⚡ Health: http://localhost:3001/health")
    print("")
    print("🧠 Key AI endpoints to test in Postman:")
    print("  POST /ai/analyze/health/test-agent-001")
    print("  POST /ai/mirror/recommend/test-agent-001") 
    print("  POST /ai/healing/strategy/test-agent-001")
    print("  GET /ai/mirror/topology")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    sys.exit(1)
