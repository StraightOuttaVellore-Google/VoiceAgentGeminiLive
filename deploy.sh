#!/bin/bash
# Simple deployment script for Sahay Voice Agent
# Run this script to quickly set up the application on a new device

set -e  # Exit on any error

echo "🚀 Sahay Voice Agent - Quick Deploy"
echo "=================================="

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Please run this script from the project root directory"
    echo "   Make sure you have both 'backend' and 'frontend' folders"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8 or higher is required"
    echo "   Current version: $python_version"
    exit 1
else
    echo "✅ Python $python_version detected"
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    echo "   Please install Node.js from https://nodejs.org/"
    exit 1
else
    echo "✅ Node.js $(node --version) detected"
fi

# Setup backend
echo ""
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
EOF
    echo "⚠️  Please update backend/.env with your actual GEMINI_API_KEY"
fi

cd ..

# Setup frontend
echo ""
echo "🔧 Setting up frontend..."
cd frontend

# Install dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Frontend Configuration
VITE_API_URL=http://localhost:8000
EOF
fi

cd ..

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update backend/.env with your GEMINI_API_KEY"
echo "2. Start the backend:"
echo "   cd backend && source venv/bin/activate && python main.py"
echo "3. Start the frontend (in a new terminal):"
echo "   cd frontend && npm run dev"
echo "4. Open http://localhost:5173 in your browser"
echo ""
echo "🔧 Troubleshooting:"
echo "- If PyAudio fails, install system audio libraries:"
echo "  Ubuntu/Debian: sudo apt-get install portaudio19-dev python3-pyaudio"
echo "  macOS: brew install portaudio"
echo "- If VAD model download fails, check your internet connection"
