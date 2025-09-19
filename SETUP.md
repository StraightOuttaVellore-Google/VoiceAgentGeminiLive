# 🚀 Full Stack Awaaz Setup Guide

## Prerequisites

1. **Python 3.8+** with pip
2. **Node.js 18+** with npm
3. **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/apikey)

## Environment Setup

1. Create a `.env` file in the root directory:
```bash
# In the main project directory
echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
```

2. Replace `your_actual_api_key_here` with your actual Gemini API key.

## Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Frontend Setup

```bash
cd frontend
npm install
```

## Running the Application

### Start Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```
Backend will run on: http://localhost:8000

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```
Frontend will run on: http://localhost:3000

## Usage

1. Open http://localhost:3000 in your browser
2. Configure the system prompt and voice settings
3. Click "Start Chatting" to begin voice conversation
4. Speak into your microphone and receive audio responses

## Troubleshooting

### Common Issues:

1. **API Key Error**: Make sure your `.env` file contains a valid Gemini API key
2. **Microphone Access**: Ensure browser has microphone permissions
3. **WebSocket Connection**: Check that backend is running on port 8000
4. **Audio Issues**: Try different voices or refresh the page

### Audio Permissions:
- Chrome: Allow microphone access when prompted
- Firefox: Check site permissions in address bar
- Safari: System Preferences > Security & Privacy > Microphone

## Features

- **Real-time Voice Chat**: Seamless audio streaming with Gemini 2.0 Flash
- **Multiple Voices**: Choose from Puck, Charon, Kore, Fenrir, Aoede
- **Customizable Prompts**: Configure AI personality and behavior
- **Google Search Integration**: Optional web search capabilities
- **Cross-platform**: Works on Windows, macOS, and Linux




