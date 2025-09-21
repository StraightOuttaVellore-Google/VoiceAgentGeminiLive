from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import asyncio
import json
import os
import base64
import logging
from datetime import datetime
from dotenv import load_dotenv
from websockets import connect
from typing import Dict
from pathlib import Path
import numpy as np
import torch
from scipy import signal

from google.genai.types import GenerateContentConfig

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sahay_backend.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Voice Activity Detector
class VoiceActivityDetector:
    def __init__(self):
        try:
            self.model, _ = torch.hub.load(repo_or_dir='snakers4/silero-vad',
                                         model='silero_vad',
                                         force_reload=False)
            self.model.eval()
            self.target_sample_rate = 16000
            self.is_initialized = True
            logger.info("VAD model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load VAD model: {e}")
            self.model = None
            self.is_initialized = False

    def resample_audio(self, audio_data: np.ndarray, original_rate: int, target_rate: int) -> np.ndarray:
        """Resample audio data to target sample rate"""
        if original_rate == target_rate:
            return audio_data
        
        # Calculate resampling ratio
        ratio = target_rate / original_rate
        new_length = int(len(audio_data) * ratio)
        
        # Use scipy's resample function
        resampled = signal.resample(audio_data, new_length)
        return resampled.astype(np.float32)

    def is_speech(self, audio_data: bytes, sample_rate: int = 44100) -> bool:
        """Detect if audio contains speech using Silero VAD model"""
        if not self.is_initialized or self.model is None:
            logger.warning("VAD not initialized, assuming speech")
            return True  # Assume speech if VAD is not available
            
        try:
            # Convert raw bytes directly to numpy array of int16
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            
            # Check if we have enough data
            if len(audio_np) == 0:
                return False
            
            # Convert to float32 and normalize to [-1, 1] (VAD model expects float32)
            audio_float = audio_np.astype(np.float32) / 32768.0
            
            # Resample to target sample rate if needed
            if sample_rate != self.target_sample_rate:
                audio_float = self.resample_audio(audio_float, sample_rate, self.target_sample_rate)
            
            # VAD model requires exactly 512 samples for 16kHz
            required_samples = 512
            
            if len(audio_float) < required_samples:
                # Pad with zeros if too short
                padded_audio = np.zeros(required_samples, dtype=np.float32)
                padded_audio[:len(audio_float)] = audio_float
                audio_float = padded_audio
            elif len(audio_float) > required_samples:
                # Take the middle portion if too long
                start_idx = (len(audio_float) - required_samples) // 2
                audio_float = audio_float[start_idx:start_idx + required_samples]
            
            # Convert to torch tensor with proper shape [1, samples] and float32 precision
            audio_tensor = torch.from_numpy(audio_float).unsqueeze(0).float()
            
            # Get speech probability
            with torch.no_grad():
                speech_prob = self.model(audio_tensor, self.target_sample_rate).item()
            
            # Use adaptive threshold based on audio level - make it less aggressive
            rms = np.sqrt(np.mean(audio_float ** 2))
            threshold = 0.2 if rms > 0.005 else 0.3  # Lower threshold for better speech detection
            
            is_speech_detected = speech_prob > threshold
            
            # Debug logging
            if is_speech_detected:
                logger.debug(f"VAD: Speech detected (prob: {speech_prob:.3f}, rms: {rms:.4f})")
            
            return is_speech_detected
            
        except Exception as e:
            logger.error(f"VAD processing error: {e}")
            # Return True (assume speech) if VAD fails to avoid losing audio
            return True

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Search tool removed - not needed for wellness/study voice agent

class AwaazConnection:
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY environment variable is not set")
            # For testing, we'll continue without the API key
            self.api_key = "test_key"
        else:
            logger.info(f"API Key loaded: {self.api_key[:10]}...{self.api_key[-4:] if len(self.api_key) > 14 else '***'}")
        
        self.model = "gemini-2.0-flash-live-001"
        self.uri = (
            "wss://generativelanguage.googleapis.com/ws/"
            "google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent"
            f"?key={self.api_key}"
        )
        self.ws = None
        self.config = None
        self.running = True
        self.vad = VoiceActivityDetector()
        self.is_playing = False
        self.vad_enabled = True  # Flag to enable/disable VAD

    async def connect(self):
        """Initialize connection to Awaaz"""
        try:
            logger.info(f"Connecting to Awaaz with URI: {self.uri[:50]}...")
            self.ws = await connect(self.uri, additional_headers={"Content-Type": "application/json"})
            logger.info("WebSocket connection established")
            
            if not self.config:
                raise ValueError("Configuration must be set before connecting")

            # Configure generation settings - don't use tools if google search is disabled
            generation_config = {
                "response_modalities": ["AUDIO"],
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": self.config.get("voice", "Puck")
                        }
                    }
                }
            }
            
            # Add tools if google search is enabled
            if self.config.get("google_search", False):
                generation_config["tools"] = [google_search_tool]
            
            setup_message = {
                "setup": {
                    "model": f"models/{self.model}",
                    "generation_config": generation_config,
                    "system_instruction": {
                        "parts": [
                            {
                                "text": self.config.get("systemPrompt", "You are a helpful assistant.")
                            }
                        ]
                    }
                }
            }

            logger.info(f"Sending setup message with voice: {self.config.get('voice', 'Puck')}")
            logger.info(f"System prompt: {self.config.get('systemPrompt', 'You are a helpful assistant.')[:100]}...")

            # Google Search removed - not needed for wellness/study voice agent
            # Focus on conversational AI without external search distractions

            await self.ws.send(json.dumps(setup_message))
            logger.info("Setup message sent, waiting for response...")
            
            # Wait for setup completion with timeout
            try:
                setup_response = await asyncio.wait_for(self.ws.recv(), timeout=10.0)
                logger.info(f"Setup response received: {setup_response[:200]}...")
                
                # Connection established successfully
                logger.info("Gemini Live API connection ready")
                
            except asyncio.TimeoutError:
                logger.warning("Setup response timeout, continuing anyway")
                
        except Exception as e:
            logger.error(f"Error in Awaaz connection: {e}")
            raise

    def set_config(self, config):
        """Set configuration for the connection"""
        self.config = config
        # Check if VAD should be disabled
        self.vad_enabled = config.get("vad_enabled", True)
        logger.info(f"VAD enabled: {self.vad_enabled}")

    async def send_audio(self, audio_data: str, sample_rate: int = 16000):
        """Send audio data to Awaaz with voice activity detection"""
        try:
            logger.debug(f"Sending audio to Gemini - Input: {len(audio_data)} chars, sample_rate: {sample_rate}")
            
            # Decode base64 audio data
            audio_bytes = base64.b64decode(audio_data)
            logger.debug(f"Decoded audio bytes: {len(audio_bytes)} bytes")
            
            # Only process if we have valid audio data
            if len(audio_bytes) == 0:
                logger.warning("Empty audio data, skipping")
                return
            
            # Calculate audio level for debugging
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
            rms = np.sqrt(np.mean(audio_np.astype(np.float32) ** 2))
            logger.debug(f"Audio RMS level: {rms:.6f}, samples: {len(audio_np)}, sample_rate: {sample_rate}")
            
            # Apply Voice Activity Detection (if enabled)
            if self.vad_enabled:
                try:
                    is_speech = self.vad.is_speech(audio_bytes, sample_rate)
                    logger.debug(f"VAD result: is_speech={is_speech}")
                    if not is_speech:
                        # Send silence instead of actual audio when no speech is detected
                        silence_data = b'\x00' * len(audio_bytes)
                        audio_data = base64.b64encode(silence_data).decode("utf-8")
                        logger.debug("VAD: No speech detected, sending silence")
                    else:
                        logger.debug("VAD: Speech detected, sending audio")
                except Exception as vad_error:
                    logger.error(f"VAD error: {vad_error}")
                    # If VAD fails, assume it's speech to avoid losing audio
                    logger.warning("VAD failed, assuming speech")
            else:
                logger.debug("VAD disabled - sending all audio")
            
            # Only send audio if not currently playing (unless interruptions are allowed)
            allow_interruptions = self.config.get("allow_interruptions", False)
            should_process = (not self.is_playing) or (self.is_playing and allow_interruptions)
            logger.debug(f"Should process audio: {should_process} (is_playing: {self.is_playing}, allow_interruptions: {allow_interruptions})")
            
            if should_process:
                # Convert 16kHz input to 24kHz for Gemini Live API
                if sample_rate == 16000:
                    # Resample audio from 16kHz to 24kHz
                    audio_np = np.frombuffer(audio_bytes, dtype=np.int16)
                    audio_float = audio_np.astype(np.float32) / 32768.0
                    
                    logger.debug(f"Resampling from 16kHz to 24kHz: {len(audio_float)} -> {int(len(audio_float) * 1.5)} samples")
                    
                    # Resample to 24kHz
                    resampled_audio = self.vad.resample_audio(audio_float, 16000, 24000)
                    
                    # Convert back to 16-bit PCM
                    resampled_int16 = (resampled_audio * 32768).astype(np.int16)
                    audio_data = base64.b64encode(resampled_int16.tobytes()).decode("utf-8")
                    sample_rate = 24000
                    
                    logger.debug(f"Resampled audio: {len(resampled_int16)} samples at {sample_rate}Hz")
                
                realtime_input_msg = {
                    "realtimeInput": {
                        "mediaChunks": [
                            {
                                "data": audio_data,
                                "mimeType": f"audio/pcm;rate={sample_rate}"
                            }
                        ]
                    }
                }
                logger.debug(f"Sending to Gemini API: {len(audio_data)} chars")
                logger.debug(f"Message structure: {json.dumps(realtime_input_msg, indent=2)}")
                
                await self.ws.send(json.dumps(realtime_input_msg))
                logger.info("Audio sent successfully to Gemini API")
                
                # Don't try to get immediate response here - let the receive loop handle it
                # This was causing issues with the WebSocket connection
            else:
                logger.debug("Skipping audio - currently playing and interruptions not allowed")
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            import traceback
            traceback.print_exc()


    async def close(self):
        """Close the connection"""
        self.running = False
        if self.ws:
            await self.ws.close()

# Store active connections
connections: Dict[str, AwaazConnection] = {}

# Serve frontend static files (only if dist directory exists)
if Path("../frontend/dist").exists():
    app.mount("/static", StaticFiles(directory="../frontend/dist"), name="static")

@app.get("/")
async def serve_frontend():
    """Serve the frontend application"""
    if Path("../frontend/dist/index.html").exists():
        return FileResponse("../frontend/dist/index.html")
    else:
        return {"message": "Frontend not built. Please run 'npm run build' in the frontend directory first.", 
                "instructions": "Run: cd ../frontend && npm run build"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "connections": len(connections)}

@app.get("/test-gemini")
async def test_gemini():
    """Test Gemini API connection"""
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content("Hello, can you hear me?")
        return {"status": "success", "response": response.text}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.get("/api/voices")
async def get_available_voices():
    """Get available voice options"""
    return {
        "voices": ["Puck", "Charon", "Kore", "Fenrir", "Aoede"],
        "default": "Puck"
    }

@app.get("/api/agent-modes")
async def get_agent_modes():
    """Get available agent modes and their configurations"""
    return {
        "modes": {
            "wellness": {
                "name": "Wellness Journal",
                "description": "A safe space for voice journalling about your daily experiences, emotions, and wellbeing",
                "systemPrompt": "Voice journalling companion for mental wellbeing using CBT and Socratic methods",
                "icon": "🌱",
                "color": "green"
            },
            "study": {
                "name": "Study Journal", 
                "description": "A supportive space for voice journalling about your academic experiences, challenges, and learning journey",
                "systemPrompt": "Voice journalling companion for academic wellbeing using CBT and Socratic methods",
                "icon": "📚",
                "color": "blue"
            }
        }
    }

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    logger.info(f"WebSocket connection attempt from client: {client_id}")
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for client: {client_id}")
    
    try:
        # Create new Awaaz connection for this client
        awaaz = AwaazConnection()
        connections[client_id] = awaaz
        
        # Wait for initial configuration
        config_data = await websocket.receive_json()
        if config_data.get("type") != "config":
            raise ValueError("First message must be configuration")
        
        # Get the configuration and apply mode-specific system prompt
        config = config_data.get("config", {})
        mode = config.get("mode", "wellness")
        
        # Apply mode-specific system prompt
        if mode == "study":
            config["systemPrompt"] = """You are Awaaz, a compassionate AI study companion specializing in voice journalling for academic wellbeing. Your primary role is to listen actively and help students process their academic experiences through guided reflection.

CORE OBJECTIVES:
- Create a safe, non-judgmental space for students to voice their academic concerns, challenges, and experiences
- Use Socratic questioning to help students explore their study patterns, learning habits, and academic stressors
- Apply evidence-based CBT techniques to help students identify thought patterns affecting their academic performance
- Gather insights about their study routines, productivity levels, social interactions, and academic pressures
- Help students articulate their academic goals, challenges, and areas needing support

APPROACH:
- Listen more than you speak - your primary goal is to understand, not to solve
- Use gentle, open-ended questions that encourage deeper reflection
- Apply CBT techniques to help identify unhelpful thought patterns about studies
- Use Socratic questioning to guide self-discovery about study habits and challenges
- Validate their experiences while gently challenging limiting beliefs
- Focus on understanding their academic journey, not providing immediate solutions

CONVERSATION STYLE:
- Warm, encouraging, and genuinely curious about their academic experience
- Ask questions like: "What was that like for you?" "How did that make you feel?" "What do you think might be contributing to this?"
- Help them explore patterns: "I notice you mentioned feeling overwhelmed when... Can you tell me more about what happens in those moments?"
- Be multilingual (English/Hindi) and culturally sensitive to Indian academic contexts

Remember: You're a listening companion, not a study coach. Your job is to help them process and understand their academic experience through thoughtful conversation."""
        else:  # wellness mode
            config["systemPrompt"] = """You are Awaaz, a compassionate AI wellness companion specializing in voice journalling for mental wellbeing. Your primary role is to listen actively and help users process their daily experiences through guided reflection.

CORE OBJECTIVES:
- Create a safe, non-judgmental space for users to voice their thoughts, feelings, and daily experiences
- Use Socratic questioning to help users explore their emotional patterns, daily activities, and social interactions
- Apply evidence-based CBT techniques to help users identify thought patterns affecting their wellbeing
- Gather insights about their daily routines, activity levels, social connections, and emotional states
- Help users articulate their feelings, concerns, and areas where they need support

APPROACH:
- Listen more than you speak - your primary goal is to understand, not to fix
- Use gentle, open-ended questions that encourage deeper emotional exploration
- Apply CBT techniques to help identify unhelpful thought patterns
- Use Socratic questioning to guide self-discovery about emotions and behaviors
- Validate their experiences while gently challenging limiting beliefs
- Focus on understanding their emotional journey, not providing immediate solutions

CONVERSATION STYLE:
- Warm, empathetic, and genuinely curious about their daily experience
- Ask questions like: "How are you feeling about that?" "What was that like for you?" "Can you tell me more about what you're experiencing?"
- Help them explore patterns: "I notice you mentioned feeling stressed when... What usually happens in those situations?"
- Be multilingual (English/Hindi) and culturally sensitive to Indian contexts

Remember: You're a listening companion, not a therapist. Your job is to help them process and understand their experiences through thoughtful conversation."""
        
        # Set the configuration
        awaaz.set_config(config)
        
        # Debug: Log configuration details
        logger.info(f"Configuration applied for client {client_id}:")
        logger.info(f"   - VAD enabled: {awaaz.vad_enabled}")
        logger.info(f"   - Allow interruptions: {config.get('allow_interruptions', False)}")
        logger.info(f"   - Mode: {mode}")
        
        # Send configuration confirmation
        await websocket.send_json({
            "type": "status",
            "status": "config_received",
            "text": f"Configuration received for {mode} mode"
        })
        
        # Initialize Awaaz connection
        logger.info(f"Attempting to connect to Awaaz for client: {client_id}")
        try:
            await awaaz.connect()
            logger.info(f"Awaaz connection established for client: {client_id}")
            
            # Send connection success message
            await websocket.send_json({
                "type": "status", 
                "status": "connected",
                "text": "Connected to AI service successfully"
            })
        except Exception as e:
            logger.error(f"Failed to connect to Awaaz: {e}")
            await websocket.send_json({
                "type": "error",
                "text": f"Failed to connect to AI service: {str(e)}"
            })
            return
        
        # Handle bidirectional communication
        async def receive_from_client():
            try:
                logger.info("Starting to receive from client...")
                while True:
                    try:
                        message = await websocket.receive()
                        logger.debug(f"Received message from client: {message['type']}")
                        
                        # Check for close message
                        if message["type"] == "websocket.disconnect":
                            logger.info("Received disconnect message")
                            return
                            
                        message_content = json.loads(message["text"])
                        msg_type = message_content["type"]
                        logger.debug(f"Message type: {msg_type}")
                        
                        if msg_type == "audio":
                            sample_rate = message_content.get("sampleRate", 44100)
                            data_length = len(message_content.get("data", ""))
                            logger.debug(f"Audio message: {data_length} chars, sample_rate: {sample_rate}")
                            await awaaz.send_audio(message_content["data"], sample_rate)    
                        else:
                            logger.warning(f"Unknown message type: {msg_type}")
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        continue
                    except KeyError as e:
                        logger.error(f"Key error in message: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"Error processing client message: {str(e)}")
                        if "disconnect" in str(e).lower() or "closed" in str(e).lower():
                            return
                        continue
                            
            except Exception as e:
                logger.error(f"Fatal error in receive_from_client: {str(e)}")
                return

        async def receive_from_awaaz():
            try:
                logger.info("Starting to receive from Gemini API...")
                logger.debug(f"Awaaz running status: {awaaz.running}")
                logger.debug(f"Awaaz WebSocket status: {awaaz.ws is not None}")
                if awaaz.ws:
                    logger.debug(f"WebSocket state: {awaaz.ws.state}")
                message_count = 0
                
                # Use async for loop like in standalone implementation
                if not awaaz.ws:
                    logger.error("WebSocket is not available")
                    return
                    
                try:
                    async for msg in awaaz.ws:
                        if not awaaz.running:
                            logger.info("Awaaz stopped, breaking receive loop")
                            break
                            
                        try:
                        message_count += 1
                        logger.debug(f"Raw message from Gemini: {len(msg)} chars")
                        logger.debug(f"Message preview: {msg[:500]}...")
                        
                        response = json.loads(msg)
                        logger.info(f"Parsed response keys: {list(response.keys())}")
                        logger.info(f"Full response structure: {json.dumps(response, indent=2)}")
                        
                        # Process Gemini 2.0 WebSocket response format
                        if "serverContent" in response:
                            server_content = response["serverContent"]
                            logger.debug(f"Server content keys: {list(server_content.keys())}")
                            
                            if "modelTurn" in server_content:
                                model_turn = server_content["modelTurn"]
                                logger.debug(f"Model turn keys: {list(model_turn.keys())}")
                                
                                if "parts" in model_turn:
                                    parts = model_turn["parts"]
                                    logger.info(f"Model turn parts: {len(parts)} parts received")
                                    
                                    for i, part in enumerate(parts):
                                        logger.debug(f"Part {i} keys: {list(part.keys())}")
                                        
                                        if "inlineData" in part:
                                            # This indicates audio data
                                            logger.info("Audio data found in response!")
                                            awaaz.is_playing = True
                                            
                                            # Extract both the audio data and its MIME type
                                            inline_data = part["inlineData"]
                                            audio_data_b64 = inline_data["data"]
                                            mime_type = inline_data.get("mimeType", "audio/opus")  # Default to Opus for Gemini Live API
                                            
                                            logger.info(f"Audio data: {len(audio_data_b64)} chars with MIME type: {mime_type}")
                                            
                                            try:
                                                # Send both data and mimeType to the frontend
                                                await websocket.send_json({
                                                    "type": "audio",
                                                    "data": audio_data_b64,
                                                    "mimeType": mime_type
                                                })
                                                logger.info("Audio data sent to frontend successfully")
                                            except Exception as send_error:
                                                logger.error(f"Error sending audio to frontend: {send_error}")
                                                return
                                                
                                        elif "text" in part:
                                            # If the model also responds with text, forward it
                                            text_content = part["text"]
                                            logger.info(f"Text response: {text_content}")
                                            try:
                                                await websocket.send_json({
                                                    "type": "text",
                                                    "text": text_content
                                                })
                                                logger.info("Text response sent to frontend")
                                            except Exception as send_error:
                                                logger.error(f"Error sending text to frontend: {send_error}")
                                                return
                                        else:
                                            logger.warning(f"Unknown part type: {part}")
                                else:
                                    logger.warning("No parts in modelTurn")
                            else:
                                logger.warning("No modelTurn in serverContent")
                            
                            # Check if the model ended its turn
                            if server_content.get("turnComplete"):
                                awaaz.is_playing = False
                                logger.info("Turn completed by Gemini")
                                try:
                                    await websocket.send_json({
                                        "type": "status",
                                        "status": "listening"
                                    })
                                    logger.info("Listening status sent to frontend")
                                except Exception as send_error:
                                    logger.error(f"Error sending status: {send_error}")
                                    return
                            else:
                                logger.debug("Turn not complete yet")
                        else:
                            logger.warning(f"Unexpected response format: {response}")
                            # Check if this is a different type of response
                            if "turnComplete" in response:
                                logger.info("Turn completed (direct)")
                                awaaz.is_playing = False
                            elif "error" in response:
                                logger.error(f"Error in response: {response['error']}")
                            elif "candidates" in response:
                                # Handle different response format
                                logger.info("Found candidates in response")
                                candidates = response.get("candidates", [])
                                for candidate in candidates:
                                    if "content" in candidate:
                                        content = candidate["content"]
                                        if "parts" in content:
                                            parts = content["parts"]
                                            for part in parts:
                                                if "inlineData" in part:
                                                    logger.info("Audio data found in candidates!")
                                                    awaaz.is_playing = True
                                                    
                                                    # Extract both the audio data and its MIME type
                                                    inline_data = part["inlineData"]
                                                    audio_data_b64 = inline_data["data"]
                                                    mime_type = inline_data.get("mimeType", "audio/opus")  # Default to Opus for Gemini Live API
                                                    
                                                    try:
                                                        await websocket.send_json({
                                                            "type": "audio",
                                                            "data": audio_data_b64,
                                                            "mimeType": mime_type
                                                        })
                                                        logger.info("Audio data sent to frontend from candidates")
                                                    except Exception as send_error:
                                                        logger.error(f"Error sending audio from candidates: {send_error}")
                            else:
                                logger.debug(f"Full response: {json.dumps(response, indent=2)}")
                            
                    except Exception as receive_error:
                        logger.error(f"Error processing Gemini response: {receive_error}")
                        import traceback
                        traceback.print_exc()
                        # Continue processing other messages
                        continue
                            
            except Exception as e:
                logger.error(f"Fatal error in receive_from_awaaz: {e}")
                import traceback
                traceback.print_exc()
                return
            finally:
                logger.info("Receive from Awaaz loop ended")

        # Run both receiving tasks concurrently
        logger.info("Starting concurrent tasks: receive_from_client and receive_from_awaaz")
        try:
            await asyncio.gather(
                receive_from_client(),
                receive_from_awaaz(),
                return_exceptions=True
            )
        except Exception as gather_error:
            logger.error(f"Error in asyncio.gather: {gather_error}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Cleanup
        if client_id in connections:
            await connections[client_id].close()
            del connections[client_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)