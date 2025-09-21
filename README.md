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

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini Live API for voice processing capabilities
- Silero VAD for voice activity detection
- The open-source community for various libraries and tools

---

**Sahay** - Empowering a generation to build resilience through voice journalling and AI-powered wellness support. 🌱✨