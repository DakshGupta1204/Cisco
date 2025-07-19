#!/usr/bin/env python3
"""
Database Cleanup Script - Remove malformed agents from MongoDB
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import sys

class DatabaseCleaner:
    def __init__(self):
        # Load MongoDB URI from environment
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb+srv://mohantyswastik7008:xONvt5tI8BKZbOhz@cluster0.c5oyate.mongodb.net/aegis_guardian?retryWrites=true&w=majority&appName=Cluster0')
        self.client = AsyncIOMotorClient(mongodb_uri)
        self.db = self.client.aegis_guardian
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            await self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    async def list_all_agents(self):
        """List all agents in the database"""
        try:
            agents_collection = self.db.agents
            agents = await agents_collection.find({}).to_list(length=None)
            
            print(f"\n📊 Found {len(agents)} agents in database:")
            print("-" * 60)
            
            valid_agents = []
            malformed_agents = []
            
            for i, agent in enumerate(agents, 1):
                agent_id = agent.get('agent_id', 'UNKNOWN')
                hostname = agent.get('hostname', 'UNKNOWN')
                status = agent.get('status', 'UNKNOWN')
                last_heartbeat = agent.get('last_heartbeat', 'UNKNOWN')
                
                print(f"{i}. Agent ID: '{agent_id}'")
                print(f"   Hostname: '{hostname}'")
                print(f"   Status: {status}")
                print(f"   Last Heartbeat: {last_heartbeat}")
                
                # Check if malformed
                is_malformed = (
                    '}' in agent_id or 
                    'UNKNOWN' in agent_id or 
                    '${HOSTNAME}' in hostname or
                    len(agent_id) > 15 or
                    agent_id.endswith('-agent}')
                )
                
                if is_malformed:
                    print(f"   🚨 MALFORMED - Will be deleted")
                    malformed_agents.append(agent)
                else:
                    print(f"   ✅ VALID - Will be kept")
                    valid_agents.append(agent)
                print()
            
            return valid_agents, malformed_agents
            
        except Exception as e:
            print(f"❌ Error listing agents: {e}")
            return [], []
    
    async def clean_malformed_agents(self, malformed_agents):
        """Remove malformed agents from database"""
        if not malformed_agents:
            print("✅ No malformed agents to clean")
            return
        
        print(f"🧹 Cleaning {len(malformed_agents)} malformed agents...")
        
        try:
            agents_collection = self.db.agents
            metrics_collection = self.db.metrics
            anomalies_collection = self.db.anomalies
            
            for agent in malformed_agents:
                agent_id = agent.get('agent_id')
                print(f"   🗑️ Deleting agent: '{agent_id}'")
                
                # Delete from agents collection
                await agents_collection.delete_one({'agent_id': agent_id})
                
                # Delete associated metrics
                metrics_result = await metrics_collection.delete_many({'agent_id': agent_id})
                print(f"      📊 Deleted {metrics_result.deleted_count} metrics records")
                
                # Delete associated anomalies
                anomalies_result = await anomalies_collection.delete_many({'agent_id': agent_id})
                print(f"      🚨 Deleted {anomalies_result.deleted_count} anomaly records")
            
            print("✅ Cleanup completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
    
    async def verify_cleanup(self):
        """Verify that only valid agents remain"""
        print("\n🔍 Verifying cleanup...")
        
        try:
            agents_collection = self.db.agents
            remaining_agents = await agents_collection.find({}).to_list(length=None)
            
            print(f"📊 Remaining agents: {len(remaining_agents)}")
            
            for agent in remaining_agents:
                agent_id = agent.get('agent_id')
                hostname = agent.get('hostname') 
                status = agent.get('status')
                print(f"   ✅ {agent_id} ({hostname}) - {status}")
            
            if len(remaining_agents) == 1 and remaining_agents[0].get('agent_id') == 'agent-001':
                print("🎯 Perfect! Only the valid agent remains.")
            elif len(remaining_agents) == 0:
                print("⚠️ No agents remaining. Start your agent to register it.")
            else:
                print("⚠️ Unexpected agents still present.")
                
        except Exception as e:
            print(f"❌ Error verifying cleanup: {e}")
    
    async def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()

async def main():
    print("🧹 Aegis Database Cleanup Tool")
    print("="*50)
    print("This will remove malformed agents from MongoDB")
    print("="*50)
    
    cleaner = DatabaseCleaner()
    
    # Connect to database
    if not await cleaner.connect():
        return
    
    try:
        # List all agents
        valid_agents, malformed_agents = await cleaner.list_all_agents()
        
        if malformed_agents:
            print(f"\n⚠️ Found {len(malformed_agents)} malformed agents to clean")
            print("🎯 These agents have malformed IDs or hostnames and should be removed")
            
            # Ask for confirmation
            response = input("\n❓ Do you want to delete the malformed agents? (y/N): ").strip().lower()
            
            if response in ['y', 'yes']:
                await cleaner.clean_malformed_agents(malformed_agents)
                await cleaner.verify_cleanup()
                
                print("\n🚀 NEXT STEPS:")
                print("1. Restart your response monitor")
                print("2. You should now see only 1 agent: 'agent-001'")
                print("3. Metrics should display correctly (not 0%)")
                print("4. Test with: python attack_simulator.py")
            else:
                print("❌ Cleanup cancelled")
        else:
            print("✅ No cleanup needed - no malformed agents found")
            await cleaner.verify_cleanup()
    
    finally:
        await cleaner.close()

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(main())
