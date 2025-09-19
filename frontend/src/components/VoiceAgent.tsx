import { useState, useEffect, useRef, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { AuraVisualizer } from "./AuraVisualizer";
import { StatusIndicator } from "./StatusIndicator";
import { ModeToggle } from "./ModeToggle";
import { SahayLogo } from "./SahayLogo";
import { PhoneOff, Mic, MicOff } from "lucide-react";
import { toast } from "sonner";
import { VoiceService, VoiceConfig, VoiceMessage } from "@/services/voiceService";
import { AudioService } from "@/services/audioService";
import { logger } from "@/services/loggingService";
import { LogViewer } from "./LogViewer";

export type AgentStatus = "listening" | "thinking" | "speaking" | "idle" | "connected" | "config_received";
export type AgentMode = "wellness" | "study";

export const VoiceAgent = () => {
  const [status, setStatus] = useState<AgentStatus>("idle");
  const [mode, setMode] = useState<AgentMode>("wellness");
  const [isConnected, setIsConnected] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isInitializing, setIsInitializing] = useState(false);
  const [vadStatus, setVadStatus] = useState({ isSpeech: false, confidence: 0 });
  const [debugInfo, setDebugInfo] = useState({ 
    audioChunksSent: 0, 
    lastAudioLevel: 0, 
    lastAudioTime: null as Date | null 
  });

  const voiceServiceRef = useRef<VoiceService | null>(null);
  const audioServiceRef = useRef<AudioService | null>(null);
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Apply theme to document element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', mode);
  }, [mode]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
      if (voiceServiceRef.current) {
        voiceServiceRef.current.disconnect();
      }
      if (audioServiceRef.current) {
        audioServiceRef.current.cleanup();
      }
    };
  }, []);

  const handleVoiceMessage = useCallback((message: VoiceMessage) => {
    logger.debug('Received voice message', { type: message.type, status: message.status }, 'VoiceAgent');
    switch (message.type) {
      case 'audio':
        logger.info('Audio message received', { 
          dataLength: message.data?.length, 
          mimeType: message.mimeType 
        }, 'VoiceAgent');
        if (message.data && audioServiceRef.current) {
          logger.debug('Attempting to play audio', { mimeType: message.mimeType }, 'VoiceAgent');
          audioServiceRef.current.playAudio(message.data, message.mimeType || 'audio/pcm;rate=24000').catch(error => {
            logger.error('Error playing audio', { error }, 'VoiceAgent');
          });
        } else {
          logger.warn('Cannot play audio - no data or service not ready', {}, 'VoiceAgent');
        }
        break;
      case 'text':
        logger.info('Text response received', { text: message.text }, 'VoiceAgent');
        break;
      case 'status':
        const statusValue = message.status as AgentStatus || 'idle';
        setStatus(statusValue);
        
        // Handle specific status messages
        if (statusValue === 'connected') {
          logger.info('Connected to AI service', { text: message.text }, 'VoiceAgent');
          toast.success('Connected to AI service', {
            description: message.text || 'Ready to start conversation'
          });
        } else if (statusValue === 'config_received') {
          logger.info('Configuration received', { text: message.text }, 'VoiceAgent');
        }
        break;
      case 'error':
        logger.error('Voice service error', { text: message.text }, 'VoiceAgent');
        toast.error('Voice service error', {
          description: message.text || 'An error occurred'
        });
        break;
    }
  }, []);

  const handleStatusChange = useCallback((newStatus: string) => {
    setStatus(newStatus as AgentStatus);
  }, []);

  const handleError = useCallback((error: string) => {
    toast.error('Connection Error', {
      description: error
    });
    setIsConnected(false);
    setStatus('idle');
  }, []);

  const handleConnect = async () => {
    if (isInitializing) return;
    
    setIsInitializing(true);
    
    try {
      // Initialize audio service
      audioServiceRef.current = new AudioService({
        onAudioData: (audioData, sampleRate) => {
          logger.debug('Audio callback received', { 
            dataLength: audioData.length, 
            sampleRate, 
            muted: isMuted 
          }, 'VoiceAgent');
          setDebugInfo(prev => ({
            ...prev,
            audioChunksSent: prev.audioChunksSent + 1,
            lastAudioTime: new Date()
          }));
          if (voiceServiceRef.current && !isMuted) {
            // Send audio at 16kHz (will be converted to 24kHz in backend)
            voiceServiceRef.current.sendAudio(audioData, sampleRate);
          } else {
            logger.debug("Not sending audio - service not ready or muted", {}, 'VoiceAgent');
          }
        },
        onError: handleError,
        onVADStatus: (isSpeech, confidence) => {
          setVadStatus({ isSpeech, confidence });
        }
      });

      await audioServiceRef.current.initialize();

      // Initialize voice service
      voiceServiceRef.current = new VoiceService(
        handleVoiceMessage,
        handleStatusChange,
        handleError
      );

      // Create configuration based on mode
      const config: VoiceConfig = {
        systemPrompt: mode === 'wellness' 
          ? "You are Awaaz, an empathetic AI mentor focused on wellness and mindfulness. Your goal is to provide a safe space for users to talk about their feelings and wellbeing. Use a supportive and gentle tone. You are multilingual and can converse in English and Hindi."
          : "You are Awaaz, an AI study companion focused on learning and productivity. Your goal is to help users with their studies, provide educational support, and maintain focus. Use an encouraging and helpful tone. You are multilingual and can converse in English and Hindi.",
        voice: "Puck",
        allowInterruptions: false,
        mode: mode,
        vad_enabled: false // Disable VAD for testing
      };

      await voiceServiceRef.current.connect(config);
      
      setIsConnected(true);
      setStatus("listening");
      
      // Start continuous recording
      audioServiceRef.current.startRecording();

      toast(`Connected to Sahay in ${mode} mode`, {
        description: `Ready to assist with ${mode === 'wellness' ? 'mindfulness and wellbeing' : 'learning and focus'}`
      });

    } catch (error) {
      logger.error('Connection error', { error }, 'VoiceAgent');
      handleError('Failed to connect to voice service');
    } finally {
      setIsInitializing(false);
    }
  };

  const handleEndCall = () => {
    if (recordingIntervalRef.current) {
      clearInterval(recordingIntervalRef.current);
      recordingIntervalRef.current = null;
    }
    
    if (audioServiceRef.current) {
      audioServiceRef.current.stopRecording();
      audioServiceRef.current.stopPlayback(); // Stop any ongoing playback and clear queue
      audioServiceRef.current.cleanup();
    }
    
    if (voiceServiceRef.current) {
      voiceServiceRef.current.disconnect();
    }
    
    setIsConnected(false);
    setStatus("idle");
    toast("Session ended");
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
    toast(isMuted ? "Microphone enabled" : "Microphone muted");
  };

  const getGreeting = () => {
    if (mode === "wellness") {
      return "Hi there! I'm Sahay, here to support your wellness journey. How are you feeling today?";
    }
    return "Hello! I'm Sahay, ready to help you focus and learn. What would you like to study today?";
  };

  const getModeDescription = () => {
    if (mode === "wellness") {
      return "A peaceful space for mindfulness, reflection, and emotional wellbeing";
    }
    return "A focused environment for learning, concentration, and productivity";
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 transition-colors duration-700">
      {/* Header */}
      <div className="absolute top-6 left-6 right-6 flex items-center justify-between">
        <SahayLogo mode={mode} />
        <ModeToggle mode={mode} onModeChange={setMode} />
      </div>

      {/* Main Content */}
      <div className="flex flex-col items-center space-y-8 max-w-md w-full">
        {/* Welcome Message */}
        {!isConnected && (
          <div className="text-center space-y-2 animate-fade-in">
            <h1 className="text-2xl font-semibold text-foreground">
              Welcome to Sahay
            </h1>
            <p className="text-sm text-text-soft leading-relaxed">
              {getModeDescription()}
            </p>
          </div>
        )}

        {/* Aura Visualizer */}
        <div className="relative">
          <AuraVisualizer 
            status={isConnected ? status : "idle"} 
            mode={mode}
            size="large"
          />
          
          {/* Microphone Status Overlay */}
          {isConnected && (
            <div className="absolute -bottom-3 -right-3">
              <Button
                variant="outline"
                size="sm"
                onClick={toggleMute}
                className={`rounded-full w-10 h-10 p-0 border-2 ${
                  isMuted 
                    ? 'bg-destructive text-destructive-foreground border-destructive' 
                    : 'bg-surface border-border'
                }`}
              >
                {isMuted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
              </Button>
            </div>
          )}
        </div>

        {/* Status Indicator */}
        {isConnected && (
          <div className="space-y-2">
            <StatusIndicator status={status} mode={mode} />
            
            {/* VAD Status Indicator */}
            <div className="flex items-center justify-center space-x-2">
              <div className={`w-2 h-2 rounded-full transition-all duration-200 ${
                vadStatus.isSpeech 
                  ? 'bg-green-500 animate-pulse' 
                  : 'bg-gray-400'
              }`} />
              <span className="text-xs text-text-soft">
                {vadStatus.isSpeech ? 'Speech detected' : 'Listening...'}
                {vadStatus.confidence > 0 && (
                  <span className="ml-1">({Math.round(vadStatus.confidence * 100)}%)</span>
                )}
              </span>
            </div>
          </div>
        )}

        {/* Greeting or Status Message */}
        <div className="text-center space-y-4 animate-slide-in-up">
          {isConnected ? (
            <p className="text-foreground text-lg font-medium float-gentle">
              {status === "listening" && "I'm listening..."}
              {status === "thinking" && "Let me think about that..."}  
              {status === "speaking" && "Speaking..."}
              {status === "idle" && "Ready to help"}
            </p>
          ) : (
            <p className="text-text-soft text-center leading-relaxed max-w-sm">
              {getGreeting()}
            </p>
          )}
        </div>

        {/* Action Button */}
        <div className="flex flex-col items-center space-y-4">
          {!isConnected ? (
            <Button 
              onClick={handleConnect}
              disabled={isInitializing}
              size="lg"
              className="px-8 py-3 text-base font-medium bg-primary text-primary-foreground hover:bg-primary/90 transition-all duration-200 hover:scale-105 glow-soft disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isInitializing ? "Connecting..." : "Start Conversation"}
            </Button>
          ) : (
            <Button 
              onClick={handleEndCall}
              variant="destructive"
              size="lg"
              className="px-8 py-3 text-base font-medium transition-all duration-200 hover:scale-105 flex items-center gap-2"
            >
              <PhoneOff className="w-4 h-4" />
              End Call
            </Button>
          )}
        </div>
      </div>

      {/* Bottom Status */}
      {isConnected && (
        <div className="absolute bottom-6 text-center">
          <p className="text-xs text-text-soft">
            {mode === "wellness" ? "🌱 Wellness Mode" : "📚 Study Mode"}
          </p>
          {/* Debug Info */}
          <div className="mt-2 text-xs text-text-soft space-y-1">
            <p>Audio chunks sent: {debugInfo.audioChunksSent}</p>
            <p>Last audio: {debugInfo.lastAudioTime ? debugInfo.lastAudioTime.toLocaleTimeString() : 'Never'}</p>
            <p>VAD: {vadStatus.isSpeech ? 'Speech' : 'Silence'} ({Math.round(vadStatus.confidence * 100)}%)</p>
          </div>
        </div>
      )}

      {/* Log Viewer */}
      <LogViewer />
    </div>
  );
};