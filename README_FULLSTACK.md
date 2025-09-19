# Sahay - Full-Stack Voice Agent Application

A comprehensive full-stack voice agent application that combines the power of Google's Gemini AI with real-time voice interaction capabilities. The application features both wellness and study modes, providing users with an empathetic AI companion for different aspects of their daily lives.

## 🌟 Features

### Core Functionality
- **Real-time Voice Interaction**: Seamless voice conversation with AI using WebSocket communication
- **Voice Activity Detection**: Smart detection of speech vs. silence using Silero VAD
- **Dual Modes**: Wellness mode for mindfulness and emotional support, Study mode for learning and productivity
- **Audio Processing**: High-quality audio capture and playback with noise suppression
- **Modern UI**: Beautiful, responsive interface built with React and Tailwind CSS

### Technical Features
- **Backend**: FastAPI server with WebSocket support for real-time communication
- **Frontend**: React application with TypeScript and modern UI components
- **Voice AI**: Integration with Google Gemini 2.0 Flash for natural conversation
- **Audio Handling**: Browser-based audio capture and playback with PCM conversion
- **Error Handling**: Comprehensive error handling and user feedback

## 🏗️ Architecture

```
┌─────────────────┐    WebSocket    ┌─────────────────┐    WebSocket    ┌─────────────────┐
│   Frontend      │◄──────────────►│   Backend       │◄──────────────►│   Gemini AI     │
│   (React)       │                 │   (FastAPI)     │                 │   (Awaaz)       │
└─────────────────┘                 └─────────────────┘                 └─────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────┐                 ┌─────────────────┐
│   Audio Service │                 │   Voice Activity│
│   (Browser)     │                 │   Detector      │
└─────────────────┘                 └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with pip
- Node.js 16+ with npm
- Google Gemini API key
- Microphone and speakers

### Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd gemini-multimodal-playground-main
   python setup.py
   ```

2. **Configure environment**:
   ```bash
   # Edit backend/.env
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

3. **Start the application**:
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   python main.py

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

4. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - Health check: http://localhost:8000/health

## 📁 Project Structure

```
├── backend/                 # FastAPI backend server
│   ├── main.py             # Main server with WebSocket endpoints
│   ├── requirements.txt    # Python dependencies
│   └── venv/              # Python virtual environment
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API and audio services
│   │   └── pages/          # Application pages
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Vite configuration
├── standalone/             # Original standalone implementation
└── setup.py               # Setup script
```

## 🔧 Configuration

### Backend Configuration (backend/.env)
```env
GEMINI_API_KEY=your_gemini_api_key_here
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

### Frontend Configuration (frontend/.env)
```env
VITE_API_URL=http://localhost:8000
```

### Voice Configuration
The voice agent can be configured through the frontend interface:
- **System Prompt**: Customize the AI's personality and behavior
- **Voice Selection**: Choose from available voices (Puck, Charon, Kore, Fenrir, Aoede)
- **Google Search**: Enable/disable web search capabilities
- **Interruptions**: Allow/disable interrupting the AI while speaking

## 🎯 Usage

### Wellness Mode
- Focus on mindfulness and emotional wellbeing
- Empathetic responses for mental health support
- Gentle, supportive tone
- Safe space for sharing feelings

### Study Mode
- Educational support and learning assistance
- Productivity-focused responses
- Encouraging tone for academic success
- Help with focus and concentration

### Voice Interaction
1. Click "Start Conversation" to begin
2. Allow microphone access when prompted
3. Speak naturally - the AI will respond with voice
4. Use the mute button to temporarily disable microphone
5. Click "End Call" to stop the session

## 🛠️ Development

### Backend Development
```bash
cd backend
source venv/bin/activate
python main.py
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build

# Backend (serves frontend from dist/)
cd backend
python main.py
```

## 🔍 API Endpoints

### WebSocket Endpoints
- `ws://localhost:8000/ws/{client_id}` - Main voice interaction endpoint

### HTTP Endpoints
- `GET /` - Serve frontend application
- `GET /health` - Health check
- `GET /api/voices` - Get available voice options

### WebSocket Message Types
- `config` - Send configuration to voice agent
- `audio` - Send/receive audio data
- `text` - Send/receive text messages
- `status` - Status updates (listening, speaking, etc.)
- `error` - Error messages

## 🐛 Troubleshooting

### Common Issues

1. **Microphone Access Denied**
   - Ensure browser has microphone permissions
   - Check browser security settings
   - Try refreshing the page

2. **WebSocket Connection Failed**
   - Verify backend is running on port 8000
   - Check firewall settings
   - Ensure GEMINI_API_KEY is set correctly

3. **Audio Not Playing**
   - Check browser audio permissions
   - Verify speakers are working
   - Try refreshing the page

4. **Voice Activity Detection Issues**
   - Speak clearly and at normal volume
   - Reduce background noise
   - Check microphone quality

### Debug Mode
Enable debug logging by setting environment variables:
```bash
export DEBUG=1
python main.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google Gemini AI for voice capabilities
- Silero VAD for voice activity detection
- React and FastAPI communities
- All contributors and testers

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the GitHub issues
3. Create a new issue with detailed information

---

**Happy voice chatting with Sahay! 🎤✨**
