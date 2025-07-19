#!/usr/bin/env python3
"""
Test script to verify environment variable loading
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== Environment Variable Test ===")
print(f"NEO4J_URI: {os.getenv('NEO4J_URI', 'NOT_FOUND')}")
print(f"NEO4J_USER: {os.getenv('NEO4J_USER', 'NOT_FOUND')}")
print(f"NEO4J_PASSWORD: {os.getenv('NEO4J_PASSWORD', 'NOT_FOUND')[:10]}...")
print(f"MONGODB_URI: {os.getenv('MONGODB_URI', 'NOT_FOUND')[:50]}...")

# Test Neo4j connection
try:
    from neo4j import GraphDatabase
    uri = os.getenv('NEO4J_URI')
    user = os.getenv('NEO4J_USER')
    password = os.getenv('NEO4J_PASSWORD')
    
    print(f"\n=== Testing Neo4j Connection ===")
    print(f"Connecting to: {uri}")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        result = session.run("RETURN 'Hello Neo4j!' as message")
        record = result.single()
        print(f"✅ Neo4j connection successful: {record['message']}")
    driver.close()
    
except Exception as e:
    print(f"❌ Neo4j connection failed: {e}")

# Test MongoDB connection
try:
    from pymongo import MongoClient
    uri = os.getenv('MONGODB_URI')
    
    print(f"\n=== Testing MongoDB Connection ===")
    print(f"Connecting to: {uri[:50]}...")
    
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    # Test the connection
    client.admin.command('ping')
    print("✅ MongoDB connection successful")
    client.close()
    
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")

print("\n=== Test Complete ===")
