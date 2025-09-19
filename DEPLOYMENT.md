# Sahay Voice Agent - Deployment Guide

## Quick Start (New Device)

### Option 1: Automated Setup (Recommended)
```bash
# Clone or copy the project to your new device
git clone <your-repo-url> sahay-voice-agent
cd sahay-voice-agent

# Run the automated setup script
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Setup
```bash
# Run the verbose setup script
python3 setup_verbose.py
```

## Prerequisites

### System Requirements
- **Python 3.8+** (required for backend)
- **Node.js 16+** (required for frontend)
- **Git** (for cloning the repository)

### Platform-Specific Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv nodejs npm git
sudo apt-get install portaudio19-dev python3-pyaudio  # For audio support
```

#### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python3 node git
brew install portaudio  # For audio support
```

#### Windows
```bash
# Install Python from https://python.org
# Install Node.js from https://nodejs.org
# Install Git from https://git-scm.com

# For PyAudio (run in Command Prompt as Administrator)
pip install pipwin
pipwin install pyaudio
```

## Configuration

### 1. Backend Configuration
Edit `backend/.env`:
```env
# Gemini API Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### 2. Frontend Configuration
Edit `frontend/.env`:
```env
# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

## Running the Application

### Start Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

### Start Frontend (New Terminal)
```bash
cd frontend
npm run dev
```

### Access the Application
Open your browser and go to: `http://localhost:5173`

## Project Structure

```
sahay-voice-agent/
├── backend/                 # Python FastAPI backend
│   ├── main.py             # Main application file
│   ├── requirements.txt    # Python dependencies
│   ├── venv/              # Virtual environment
│   └── .env               # Backend configuration
├── frontend/               # React TypeScript frontend
│   ├── src/               # Source code
│   ├── package.json       # Node.js dependencies
│   └── .env               # Frontend configuration
├── deploy.sh              # Quick deployment script
├── setup_verbose.py       # Detailed setup script
└── README.md              # Project documentation
```

## Features

### Voice Activity Detection (VAD)
- **Backend**: Silero VAD model for accurate speech detection
- **Frontend**: Real-time VAD status with visual feedback
- **Benefits**: Reduces noise, improves performance, better user experience

### Agent Modes
- **Wellness Mode**: Mindfulness and emotional support
- **Study Mode**: Learning and productivity assistance

### Audio Processing
- **Sample Rate**: 16kHz for optimal VAD performance
- **Format**: PCM audio with real-time processing
- **Chunking**: 512-sample chunks for efficient processing

## Troubleshooting

### Common Issues

#### 1. PyAudio Installation Fails
**Problem**: PyAudio fails to install due to missing system audio libraries

**Solution**:
```bash
# Ubuntu/Debian
sudo apt-get install portaudio19-dev python3-pyaudio

# macOS
brew install portaudio

# Windows
pip install pipwin
pipwin install pyaudio
```

#### 2. VAD Model Download Fails
**Problem**: Silero VAD model fails to download

**Solution**:
- Check internet connection
- Ensure PyTorch is properly installed
- Try running the backend again (model caches after first download)

#### 3. WebSocket Connection Fails
**Problem**: Frontend can't connect to backend

**Solution**:
- Ensure backend is running on port 8000
- Check firewall settings
- Verify API_URL in frontend/.env

#### 4. Audio Not Working
**Problem**: Microphone access denied or no audio

**Solution**:
- Grant microphone permissions in browser
- Check system audio settings
- Ensure microphone is not being used by other applications

### Debug Mode

#### Backend Debug
```bash
cd backend
source venv/bin/activate
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
python main.py
```

#### Frontend Debug
```bash
cd frontend
npm run dev -- --debug
```

## Performance Optimization

### GPU Acceleration (Optional)
For faster VAD processing with CUDA:
```bash
cd backend
source venv/bin/activate
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Memory Optimization
- Reduce buffer duration in `frontend/src/services/audioService.ts`
- Adjust VAD chunk size for your hardware
- Use smaller audio chunks for lower latency

## Security Notes

### Production Deployment
- Change CORS settings in `backend/main.py`
- Use environment variables for sensitive data
- Implement proper authentication if needed
- Use HTTPS in production

### API Key Security
- Never commit API keys to version control
- Use environment variables for sensitive configuration
- Rotate API keys regularly

## Support

### Getting Help
1. Check the troubleshooting section above
2. Review the logs in `backend/server.log`
3. Check browser console for frontend errors
4. Ensure all dependencies are properly installed

### Logs Location
- **Backend**: `backend/server.log`
- **Frontend**: Browser Developer Tools Console

## License

This project is licensed under the MIT License - see the LICENSE file for details.
