#!/usr/bin/env python3
"""
🚀 Cloud Deployment Script for Aegis of Alderaan
Deploys your backend to Railway for a public URL
"""

import subprocess
import sys
import os
import json
import time

def check_command_exists(command):
    """Check if a command exists in the system"""
    try:
        subprocess.run([command, "--version"], 
                      check=True, 
                      capture_output=True, 
                      text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_railway_cli():
    """Install Railway CLI"""
    print("📦 Installing Railway CLI...")
    try:
        # Try npm install
        subprocess.run(["npm", "install", "-g", "@railway/cli"], 
                      check=True)
        print("✅ Railway CLI installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Railway CLI via npm")
        print("📋 Please install manually:")
        print("   npm install -g @railway/cli")
        print("   Or visit: https://railway.app/cli")
        return False

def check_env_file():
    """Check if .env file exists with required variables"""
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("📋 Please create .env with:")
        print("""
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/aegis_db
NEO4J_URI=neo4j+s://your-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
JWT_SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
        """)
        return False
    
    print("✅ .env file found")
    return True

def deploy_to_railway():
    """Deploy to Railway platform"""
    print("\n🚀 Deploying Aegis Guardian to Railway...")
    print("=" * 50)
    
    # Check if Railway CLI exists
    if not check_command_exists("railway"):
        print("❌ Railway CLI not found")
        if not install_railway_cli():
            return False
    else:
        print("✅ Railway CLI found")
    
    # Check environment file
    if not check_env_file():
        return False
    
    try:
        print("\n🔑 Logging into Railway...")
        print("👆 This will open your browser for authentication")
        subprocess.run(["railway", "login"], check=True)
        
        print("\n📋 Initializing Railway project...")
        result = subprocess.run(["railway", "init"], 
                              capture_output=True, 
                              text=True)
        
        if "already exists" in result.stderr.lower():
            print("✅ Railway project already exists")
        else:
            print("✅ Railway project initialized")
        
        print("\n🏗️ Deploying to Railway...")
        print("⏳ This may take 2-5 minutes...")
        
        # Deploy the application
        deploy_result = subprocess.run(["railway", "up"], 
                                     capture_output=True, 
                                     text=True)
        
        if deploy_result.returncode == 0:
            print("✅ Deployment successful!")
            
            # Get the domain
            print("\n🌐 Getting your deployment URL...")
            domain_result = subprocess.run(["railway", "domain"], 
                                         capture_output=True, 
                                         text=True)
            
            if domain_result.returncode == 0 and domain_result.stdout.strip():
                url = domain_result.stdout.strip()
                print(f"\n🎉 SUCCESS! Your backend is live at:")
                print(f"   🔗 {url}")
                print(f"\n📋 API Endpoints:")
                print(f"   📚 Documentation: {url}/docs")
                print(f"   💓 Health Check: {url}/health")
                print(f"   🤖 Agents: {url}/agents")
                print(f"   🌐 Network: {url}/network/topology")
                
                # Create a deployment info file
                deployment_info = {
                    "platform": "Railway",
                    "url": url,
                    "deployed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "endpoints": {
                        "docs": f"{url}/docs",
                        "health": f"{url}/health", 
                        "agents": f"{url}/agents",
                        "network": f"{url}/network/topology"
                    }
                }
                
                with open("deployment_info.json", "w") as f:
                    json.dump(deployment_info, f, indent=2)
                
                print(f"\n📄 Deployment info saved to: deployment_info.json")
                
            else:
                print("⚠️ Deployed successfully, but couldn't get domain")
                print("   Check Railway dashboard: https://railway.app/dashboard")
            
            return True
        else:
            print("❌ Deployment failed!")
            print(f"Error: {deploy_result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Railway command failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ Deployment cancelled by user")
        return False

def deploy_to_render():
    """Instructions for Render deployment"""
    print("\n🎨 Render Deployment Instructions:")
    print("=" * 40)
    print("1. Push your code to GitHub")
    print("2. Go to https://render.com")
    print("3. Click 'New' → 'Web Service'")
    print("4. Connect your GitHub repository")
    print("5. Choose 'Docker' as runtime")
    print("6. Set environment variables from your .env file")
    print("7. Click 'Create Web Service'")
    print("\n✅ render.yaml configuration file already created!")

def main():
    """Main deployment function"""
    print("🛡️ Aegis of Alderaan - Cloud Deployment")
    print("=" * 50)
    
    print("\nChoose deployment platform:")
    print("1. 🚄 Railway (Recommended - Fast & Easy)")
    print("2. 🎨 Render (Great for Docker)")
    print("3. ❌ Exit")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            if deploy_to_railway():
                print("\n🎉 Deployment completed successfully!")
                print("🔗 Your backend is now accessible via the URL above!")
            else:
                print("\n❌ Deployment failed. Please check the errors above.")
            break
            
        elif choice == "2":
            deploy_to_render()
            break
            
        elif choice == "3":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
