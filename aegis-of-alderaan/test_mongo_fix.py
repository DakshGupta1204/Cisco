#!/usr/bin/env python3
"""
Test MongoDB connection fix
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guardian-server'))

from db.mongo_handler import MongoHandler

async def test_mongo_connection():
    print("Testing MongoDB connection...")
    
    # Test with environment variables
    mongo_handler = MongoHandler()
    
    try:
        await mongo_handler.connect()
        print("✅ MongoDB connection successful")
        
        # Test the fixed method
        offline_agents = await mongo_handler.get_offline_agents()
        print(f"✅ get_offline_agents() successful: {len(offline_agents)} offline agents")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
    
    finally:
        await mongo_handler.disconnect()

if __name__ == "__main__":
    asyncio.run(test_mongo_connection())
