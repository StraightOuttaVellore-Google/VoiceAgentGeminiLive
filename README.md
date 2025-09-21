# Sahay: AI-Powered Voice Journalling for Mental Wellness 🌱

Sahay is a revolutionary, AI-powered mental wellness ecosystem designed as a proactive and confidential companion for Indian youth. Our prototype is not just an app; it's an agentic system built to address the dual challenges of mental stress and academic pressure through voice journalling.

## 🌟 What is Sahay?

At its core is a real-time, empathetic voice AI (powered by Google Gemini) that allows users to journal their thoughts and feelings in a judgment-free space, with a strict privacy-first guarantee (no audio is ever stored). This is orchestrated by a sophisticated multi-agent architecture built on Google's Agent Development Kit (ADK). Specialized agents for insight, safety, and memory collaborate through a central Model Context Protocol (MCP) Server, allowing for deep, nuanced analysis.

The platform uniquely integrates this advanced wellness support with a suite of intelligent study tools to help users manage a primary source of their stress. Sahay is designed to be a culturally resonant, evidence-based first line of support, empowering a generation to build resilience.

## 🎯 Key Features

### Voice Journalling System
- **Wellness Journal**: A safe space for voice journalling about daily experiences, emotions, and wellbeing
- **Study Journal**: A supportive space for voice journalling about academic experiences, challenges, and learning journey
- **CBT & Socratic Methods**: Uses evidence-based Cognitive Behavioral Therapy and Socratic questioning techniques
- **Active Listening**: AI companion that listens more than it speaks, focusing on understanding and processing experiences

### Technical Features
- **Real-time Voice Processing**: Powered by Google Gemini Live API
- **Voice Activity Detection**: Smart detection of speech vs. silence
- **Audio Queue System**: Prevents overlapping audio responses
- **Multilingual Support**: English and Hindi language support
- **Privacy-First**: No audio data is stored or logged

## 🏗️ Architecture

```
├── frontend/          # React + TypeScript web application
├── backend/           # FastAPI Python backend
└── standalone/        # Python standalone application
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12 or higher
- Node.js 18 or higher
- Google Gemini API key

### 1. Get Your Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated API key

### 2. Backend Setup
```bash
# Clone the repository
git clone https://github.com/StraightOuttaVellore-Google/VoiceAgentGeminiLive.git
cd VoiceAgentGeminiLive

# Create and activate virtual environment
python -m venv backend/venv
# Windows:
backend\venv\Scripts\activate
# Linux/Mac:
source backend/venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Create environment file
echo "GEMINI_API_KEY=your_api_key_here" > .env

# Start the backend server
python backend/main.py
```

### 3. Frontend Setup
```bash
# In a new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Access the Application
Open http://localhost:3000 in your browser

## 🎙️ How to Use

### Wellness Journal Mode
1. Click on "Wellness Journal" in the mode toggle
2. Click the microphone button to start journalling
3. Speak about your daily experiences, emotions, and feelings
4. Sahay will listen actively and ask thoughtful questions using CBT techniques
5. Process your thoughts and gain insights about your wellbeing patterns

### Study Journal Mode
1. Click on "Study Journal" in the mode toggle
2. Click the microphone button to start journalling
3. Speak about your academic experiences, study challenges, and learning journey
4. Sahay will help you reflect on your study patterns and academic pressures
5. Gain insights about your productivity, social interactions, and academic goals

## 🔧 Configuration Options

- **Voice Selection**: Choose from different voice options (Puck, Charon, Kore, Fenrir, Aoede)
- **Interruptions**: Allow or disable interrupting Sahay while speaking
- **Voice Activity Detection**: Enable/disable smart speech detection
- **Audio Quality**: Optimized for 24kHz audio processing

## 🛠️ Development

### Project Structure
```
frontend/
├── src/
│   ├── components/     # React components
│   ├── services/       # Audio and voice services
│   └── pages/          # Application pages
backend/
├── main.py            # FastAPI application
├── requirements.txt   # Python dependencies
└── venv/             # Virtual environment
standalone/
├── standalone.py      # Standalone Python app
├── awaaz_connection.py # Gemini API connection
└── voice_activity_detector.py # VAD implementation
```

### Key Technologies
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Backend**: FastAPI, WebSockets, NumPy, SciPy, PyTorch
- **AI**: Google Gemini Live API, Silero VAD
- **Audio**: Web Audio API, PyAudio

## 🧠 AI Approach

### CBT (Cognitive Behavioral Therapy) Integration
- Identifies unhelpful thought patterns
- Challenges limiting beliefs through gentle questioning
- Helps users understand the connection between thoughts, feelings, and behaviors

### Socratic Questioning
- Uses open-ended questions to encourage deeper reflection
- Guides self-discovery about emotional and academic patterns
- Helps users explore their experiences more thoroughly

### Data Collection for Personalization
- **Wellness**: Daily routines, activity levels, social connections, emotional states
- **Study**: Study patterns, productivity levels, academic pressures, learning habits
- **Insights**: Sentiment analysis, behavioral patterns, stress indicators

## 🔒 Privacy & Security

- **No Audio Storage**: All voice data is processed in real-time and never stored
- **Local Processing**: Voice activity detection runs locally on your device
- **Secure Communication**: All data transmission is encrypted
- **No Personal Data**: No personal information is collected or stored

## 🐛 Troubleshooting

### Common Issues
1. **Audio Feedback Loop**: Use headphones to prevent microphone from picking up Sahay's voice
2. **Connection Issues**: Ensure your Gemini API key is correctly set in the `.env` file
3. **Audio Quality**: Check that your microphone permissions are enabled
4. **WebSocket Errors**: Restart the backend server if you encounter connection issues

### Debug Mode
Enable debug logging by checking the browser console for detailed audio processing information.

## 🔗 Related Projects

This project is part of the larger Sahay ecosystem. Here are the other components:

### Backend Services
- **[Backend API](https://github.com/StraightOuttaVellore-Google/google-hackathon-backend)** - FastAPI backend with RESTful APIs and WebSocket support
- **[MCP Server](https://github.com/StraightOuttaVellore-Google/sahay-mcp-server)** - Model Context Protocol server for study data management

### Frontend Applications
- **[Frontend App](https://github.com/StraightOuttaVellore-Google/google-hackathon-frontend)** - React frontend for the complete wellness platform
- **[ADK Wellness Bots](https://github.com/StraightOuttaVellore-Google/adk-mas-healthcare)** - AI-powered wellness agents using Google's Agent Development Kit

### Additional Features
- **[Discord Fullstack](https://github.com/StraightOuttaVellore-Google/discord-fullstack)** - Neumorphic Discord-style chat application

## 🧪 Testing

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test

# Run integration tests
python test_integration.py
```

### Test Coverage
- Unit tests for voice processing
- Integration tests for Gemini API
- WebSocket connection testing
- Audio quality validation
- Error handling scenarios

## 🚀 Deployment

### Production Setup
1. **Environment Configuration**:
   ```bash
   export GEMINI_API_KEY="your-gemini-api-key"
   export NODE_ENV="production"
   export PORT=3000
   ```

2. **Backend Deployment**:
   ```bash
   # Using Docker
   docker build -t sahay-backend ./backend
   docker run -p 8000:8000 sahay-backend
   
   # Using Python directly
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

3. **Frontend Deployment**:
   ```bash
   cd frontend
   npm run build
   # Deploy dist/ folder to your hosting service
   ```

4. **Cloud Deployment**:
   - **Backend**: Google Cloud Run, AWS Lambda, or Azure Functions
   - **Frontend**: Vercel, Netlify, or AWS S3 + CloudFront
   - **Database**: Firebase Firestore or Supabase

## 📊 Performance

### Optimization Features
- **Voice Activity Detection**: Efficient speech detection with Silero VAD
- **Audio Queue Management**: Prevents overlapping audio responses
- **Real-time Processing**: Optimized for low-latency voice interactions
- **Memory Management**: Efficient audio buffer handling

### Monitoring
- **Audio Quality Metrics**: Track audio processing performance
- **API Response Times**: Monitor Gemini API latency
- **Error Rates**: Track and alert on processing errors
- **User Engagement**: Monitor voice journaling usage patterns

## 🔒 Security & Privacy

### Privacy Features
- **No Audio Storage**: All voice data is processed in real-time and never stored
- **Local Processing**: Voice activity detection runs locally on your device
- **Secure Communication**: All data transmission is encrypted
- **No Personal Data**: No personal information is collected or stored

### Security Measures
- **API Key Protection**: Secure handling of Gemini API keys
- **HTTPS Only**: All communications use secure protocols
- **Input Validation**: Comprehensive validation of all user inputs
- **Rate Limiting**: Protection against abuse and overuse

## 🛠️ Development

### Project Structure
```
sahay-aura-glow/
├── backend/              # FastAPI Python backend
│   ├── main.py          # Main application entry point
│   ├── requirements.txt # Python dependencies
│   └── venv/           # Virtual environment
├── frontend/            # React TypeScript frontend
│   ├── src/            # Source code
│   ├── public/         # Static assets
│   ├── package.json    # Node.js dependencies
│   └── dist/           # Build output
├── standalone/          # Standalone Python application
│   ├── standalone.py   # Main standalone app
│   ├── awaaz_connection.py # Gemini API connection
│   └── voice_activity_detector.py # VAD implementation
└── tests/              # Test files
```

### Development Guidelines
- Follow TypeScript best practices for frontend
- Use Python type hints for backend code
- Write comprehensive tests for new features
- Document all API endpoints and functions
- Follow accessibility guidelines for UI components

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines
- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting
- Be respectful and constructive in discussions

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini Live API for voice processing capabilities
- Silero VAD for voice activity detection
- React and TypeScript communities
- FastAPI and Python communities
- The open-source community for various libraries and tools

## 📞 Support

For support and questions:
1. Check the [documentation](https://github.com/StraightOuttaVellore-Google/sahay-aura-glow/wiki)
2. Open an issue in the GitHub repository
3. Contact the development team

## ⚠️ Important Disclaimer

**This application is designed for general wellness support and should not replace professional mental health care. Always consult with qualified healthcare providers for serious mental health concerns.**

### When to Seek Professional Help
- Suicidal thoughts or self-harm
- Severe depression or anxiety
- Substance abuse issues
- Psychotic symptoms
- Any mental health crisis

### Crisis Resources
- **National Suicide Prevention Lifeline**: 988
- **Crisis Text Line**: Text HOME to 741741
- **Emergency Services**: 911

---

**Sahay** - Empowering a generation to build resilience through voice journalling and AI-powered wellness support. 🌱✨
