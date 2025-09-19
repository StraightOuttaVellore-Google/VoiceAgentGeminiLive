#!/usr/bin/env python3
"""
Development startup script for Sahay Full-Stack Voice Agent Application
Starts both backend and frontend in development mode
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

class DevServer:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True

    def start_backend(self):
        """Start the backend server"""
        print("🚀 Starting backend server...")
        backend_dir = Path("backend")
        
        # Check if virtual environment exists
        venv_python = backend_dir / "venv" / "bin" / "python"
        if not venv_python.exists():
            print("❌ Backend virtual environment not found. Please run setup.py first.")
            return False
        
        try:
            self.backend_process = subprocess.Popen(
                [str(venv_python), "main.py"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Wait a moment to see if backend starts successfully
            time.sleep(2)
            if self.backend_process.poll() is not None:
                print("❌ Backend failed to start")
                return False
            
            print("✅ Backend started on http://localhost:8000")
            return True
            
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return False

    def start_frontend(self):
        """Start the frontend development server"""
        print("🚀 Starting frontend development server...")
        frontend_dir = Path("frontend")
        
        try:
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Wait a moment to see if frontend starts successfully
            time.sleep(3)
            if self.frontend_process.poll() is not None:
                print("❌ Frontend failed to start")
                return False
            
            print("✅ Frontend started on http://localhost:5173")
            return True
            
        except Exception as e:
            print(f"❌ Error starting frontend: {e}")
            return False

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down servers...")
        self.running = False
        self.cleanup()

    def cleanup(self):
        """Clean up running processes"""
        if self.backend_process:
            print("Stopping backend...")
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
        
        if self.frontend_process:
            print("Stopping frontend...")
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
        
        print("✅ Cleanup complete")

    def run(self):
        """Run both servers"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🎯 Starting Sahay Full-Stack Voice Agent Development Servers")
        print("=" * 60)
        
        # Check if we're in the right directory
        if not Path("backend").exists() or not Path("frontend").exists():
            print("❌ Please run this script from the project root directory")
            sys.exit(1)
        
        # Check if .env file exists
        env_file = Path("backend/.env")
        if not env_file.exists():
            print("⚠️  Backend .env file not found. Please run setup.py first.")
            print("   Or create backend/.env with your GEMINI_API_KEY")
            sys.exit(1)
        
        # Start backend
        if not self.start_backend():
            print("❌ Failed to start backend. Exiting.")
            sys.exit(1)
        
        # Start frontend
        if not self.start_frontend():
            print("❌ Failed to start frontend. Exiting.")
            self.cleanup()
            sys.exit(1)
        
        print("\n🎉 Both servers are running!")
        print("📱 Frontend: http://localhost:5173")
        print("🔧 Backend:  http://localhost:8000")
        print("💡 Press Ctrl+C to stop both servers")
        print("=" * 60)
        
        try:
            # Monitor processes
            while self.running:
                # Check if backend is still running
                if self.backend_process and self.backend_process.poll() is not None:
                    print("❌ Backend process died unexpectedly")
                    break
                
                # Check if frontend is still running
                if self.frontend_process and self.frontend_process.poll() is not None:
                    print("❌ Frontend process died unexpectedly")
                    break
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

if __name__ == "__main__":
    server = DevServer()
    server.run()
