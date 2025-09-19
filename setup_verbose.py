#!/usr/bin/env python3
"""
Verbose setup script for the Sahay Full-Stack Voice Agent Application
Shows real-time progress during installation
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command_verbose(command, cwd=None):
    """Run a command and show output in real-time"""
    print(f"🔧 Running: {command}")
    print("-" * 60)
    
    try:
        process = subprocess.Popen(
            command, 
            shell=True, 
            cwd=cwd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            encoding='utf-8',
            errors='replace'
        )
        
        # Stream output in real-time
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print(f"✅ Command completed successfully")
            return True
        else:
            print(f"❌ Command failed with return code {process.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def setup_backend_verbose():
    """Setup the backend environment with verbose output"""
    print("\n🔧 Setting up backend...")
    
    backend_dir = Path("backend")
    
    # Determine the correct Python command based on OS
    python_cmd = "python3" if os.name != 'nt' else "python"
    
    # Create virtual environment if it doesn't exist or if it's broken
    venv_path = backend_dir / "venv"
    venv_needs_recreation = False
    
    if not venv_path.exists():
        venv_needs_recreation = True
    elif not (venv_path / "Scripts" / f"{python_cmd}.exe").exists():
        venv_needs_recreation = True
    else:
        # Check if pip is working in the existing virtual environment
        pip_check_cmd = f"venv\\Scripts\\{python_cmd}.exe -m pip --version" if os.name == 'nt' else f"venv/bin/{python_cmd} -m pip --version"
        if not run_command_verbose(pip_check_cmd, cwd=backend_dir):
            print("⚠️  Virtual environment exists but pip is not working, recreating...")
            venv_needs_recreation = True
    
    if venv_needs_recreation:
        if venv_path.exists():
            print("🗑️  Removing existing broken virtual environment...")
            shutil.rmtree(venv_path)
        
        print("📦 Creating Python virtual environment...")
        if not run_command_verbose(f"{python_cmd} -m venv venv --upgrade-deps", cwd=backend_dir):
            return False
        
        # Verify pip is available in the virtual environment
        pip_check_cmd = f"venv\\Scripts\\{python_cmd}.exe -m pip --version" if os.name == 'nt' else f"venv/bin/{python_cmd} -m pip --version"
        if not run_command_verbose(pip_check_cmd, cwd=backend_dir):
            print("📦 Installing pip in virtual environment...")
            ensurepip_cmd = f"venv\\Scripts\\{python_cmd}.exe -m ensurepip --upgrade" if os.name == 'nt' else f"venv/bin/{python_cmd} -m ensurepip --upgrade"
            if not run_command_verbose(ensurepip_cmd, cwd=backend_dir):
                print("❌ Failed to install pip in virtual environment")
                return False
    else:
        print("✅ Virtual environment already exists and pip is working")
    
    # Install dependencies with verbose output
    print("\n📦 Installing Python dependencies...")
    print("This may take several minutes for large packages like PyTorch...")
    pip_cmd = f"venv/bin/{python_cmd} -m pip" if os.name != 'nt' else f"venv\\Scripts\\{python_cmd}.exe -m pip"
    
    # Install dependencies from requirements.txt
    print("\n🚀 Installing Python dependencies...")
    if not run_command_verbose(f"{pip_cmd} install -r requirements.txt", cwd=backend_dir):
        print("❌ Failed to install dependencies from requirements.txt")
        print("Trying to install core dependencies individually...")
        
        # Fallback: install core dependencies individually
        core_deps = [
            "fastapi",
            "uvicorn[standard]",
            "websockets",
            "python-dotenv",
            "numpy",
            "scipy",
            "torch",
            "torchaudio"
        ]
        
        for dep in core_deps:
            print(f"\n📦 Installing {dep}...")
            if not run_command_verbose(f"{pip_cmd} install {dep}", cwd=backend_dir):
                print(f"⚠️  Warning: Failed to install {dep}, continuing...")
    
    # Try to install PyAudio separately as it often has issues
    print("\n📦 Installing PyAudio (may require system audio libraries)...")
    if not run_command_verbose(f"{pip_cmd} install pyaudio", cwd=backend_dir):
        print("⚠️  Warning: PyAudio installation failed. You may need to install system audio libraries:")
        print("   - Ubuntu/Debian: sudo apt-get install portaudio19-dev python3-pyaudio")
        print("   - macOS: brew install portaudio")
        print("   - Windows: pip install pipwin && pipwin install pyaudio")
    
    # Create .env file if it doesn't exist
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("\n📝 Creating .env file...")
        with open(env_file, "w") as f:
            f.write("""# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
""")
        print("⚠️  Please update backend/.env with your actual GEMINI_API_KEY")
    else:
        print("✅ .env file already exists")
    
    return True

def setup_frontend_verbose():
    """Setup the frontend environment with verbose output"""
    print("\n🔧 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    
    # Install dependencies
    print("📦 Installing Node.js dependencies...")
    if not run_command_verbose("npm install", cwd=frontend_dir):
        return False
    
    # Create .env file if it doesn't exist
    env_file = frontend_dir / ".env"
    if not env_file.exists():
        print("\n📝 Creating .env file...")
        with open(env_file, "w") as f:
            f.write("""# Frontend Configuration
VITE_API_URL=http://localhost:8000
""")
    
    return True

def check_system_requirements():
    """Check system requirements and provide helpful information"""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        return False
    else:
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro} detected")
    
    # Check Node.js (optional, will be checked during frontend setup)
    try:
        import subprocess
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} detected")
        else:
            print("⚠️  Node.js not found - will be required for frontend setup")
    except FileNotFoundError:
        print("⚠️  Node.js not found - will be required for frontend setup")
    
    return True

def main():
    """Main setup function with verbose output"""
    print("🚀 Setting up Sahay Full-Stack Voice Agent Application")
    print("=" * 60)
    print("This script will show real-time progress during installation")
    print("Large packages like PyTorch may take 5-10 minutes to download")
    print("=" * 60)
    
    # Check system requirements
    if not check_system_requirements():
        print("❌ System requirements not met")
        sys.exit(1)
    
    # Check if we're in the right directory
    if not Path("backend").exists() or not Path("frontend").exists():
        print("❌ Please run this script from the project root directory")
        print("   Make sure you have both 'backend' and 'frontend' folders")
        sys.exit(1)
    
    # Setup backend
    if not setup_backend_verbose():
        print("❌ Backend setup failed")
        sys.exit(1)
    
    # Setup frontend
    if not setup_frontend_verbose():
        print("❌ Frontend setup failed")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update backend/.env with your GEMINI_API_KEY")
    print("2. Start the backend:")
    if os.name == 'nt':
        print("   cd backend && venv\\Scripts\\activate && python main.py")
    else:
        print("   cd backend && source venv/bin/activate && python3 main.py")
    print("3. Start the frontend: cd frontend && npm run dev")
    print("4. Open http://localhost:5173 in your browser")
    print("\n🔧 Troubleshooting:")
    print("- If PyAudio fails, install system audio libraries first")
    print("- If VAD model download fails, check your internet connection")
    print("- For GPU acceleration, install CUDA-compatible PyTorch")

if __name__ == "__main__":
    main()
