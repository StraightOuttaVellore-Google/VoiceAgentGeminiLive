#!/usr/bin/env python3
"""
Setup script for the Sahay Full-Stack Voice Agent Application
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd, capture_output=True, text=True)
        print(f"✓ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return False

def setup_backend():
    """Setup the backend environment"""
    print("\n🔧 Setting up backend...")
    
    backend_dir = Path("backend")
    
    # Create virtual environment if it doesn't exist
    if not (backend_dir / "venv").exists():
        print("Creating Python virtual environment...")
        if not run_command("python3 -m venv venv", cwd=backend_dir):
            return False
    
    # Install dependencies
    print("Installing Python dependencies...")
    pip_cmd = "venv/bin/pip" if os.name != 'nt' else "venv\\Scripts\\pip"
    if not run_command(f"{pip_cmd} install -r requirements.txt", cwd=backend_dir):
        return False
    
    # Create .env file if it doesn't exist
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("Creating .env file...")
        with open(env_file, "w") as f:
            f.write("""# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
""")
        print("⚠️  Please update backend/.env with your actual GEMINI_API_KEY")
    
    return True

def setup_frontend():
    """Setup the frontend environment"""
    print("\n🔧 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    
    # Install dependencies
    print("Installing Node.js dependencies...")
    if not run_command("npm install", cwd=frontend_dir):
        return False
    
    # Create .env file if it doesn't exist
    env_file = frontend_dir / ".env"
    if not env_file.exists():
        print("Creating .env file...")
        with open(env_file, "w") as f:
            f.write("""# Frontend Configuration
VITE_API_URL=http://localhost:8000
""")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Sahay Full-Stack Voice Agent Application")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update backend/.env with your GEMINI_API_KEY")
    print("2. Start the backend: cd backend && source venv/bin/activate && python main.py")
    print("3. Start the frontend: cd frontend && npm run dev")
    print("4. Open http://localhost:5173 in your browser")

if __name__ == "__main__":
    main()
