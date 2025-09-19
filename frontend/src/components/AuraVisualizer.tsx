import { AgentStatus, AgentMode } from "./VoiceAgent";

interface AuraVisualizerProps {
  status: AgentStatus;
  mode: AgentMode;
  size?: "small" | "medium" | "large";
}

export const AuraVisualizer = ({ status, mode, size = "large" }: AuraVisualizerProps) => {
  const getSizeClasses = () => {
    switch (size) {
      case "small":
        return "w-16 h-16";
      case "medium":
        return "w-24 h-24";
      case "large":
      default:
        return "w-40 h-40";
    }
  };

  const getAnimationClass = () => {
    switch (status) {
      case "listening":
        return "aura-listening";
      case "thinking":
        return "aura-thinking";
      case "speaking":
        return "aura-speaking";
      case "idle":
      default:
        return "aura-pulse";
    }
  };

  const getGlowIntensity = () => {
    switch (status) {
      case "speaking":
        return "glow-strong";
      case "listening":
      case "thinking":
        return "glow-soft";
      case "idle":
      default:
        return "";
    }
  };

  return (
    <div className="relative flex items-center justify-center">
      {/* Outer Ring */}
      <div 
        className={`
          ${getSizeClasses()} 
          rounded-full 
          border-2 
          border-primary/30 
          ${getAnimationClass()} 
          ${getGlowIntensity()}
          transition-all duration-500
        `}
        style={{
          background: `conic-gradient(from 0deg, 
            hsl(var(--primary) / 0.3), 
            hsl(var(--accent) / 0.2), 
            hsl(var(--primary) / 0.1), 
            hsl(var(--primary) / 0.3)
          )`
        }}
      >
        {/* Inner Core */}
        <div className="absolute inset-3 rounded-full bg-gradient-to-br from-primary/60 to-accent/40 backdrop-blur-sm">
          {/* Central Dot */}
          <div className="absolute inset-6 rounded-full bg-primary/80 shadow-lg">
            {/* Pulsing Center */}
            <div 
              className={`
                absolute inset-2 rounded-full bg-primary 
                ${status === "speaking" ? "animate-ping" : ""}
                ${status === "thinking" ? "animate-spin" : ""}
              `}
            />
          </div>
        </div>

        {/* Status-specific elements */}
        {status === "listening" && (
          <>
            {/* Listening ripples */}
            <div className="absolute inset-0 rounded-full border border-primary/20 animate-ping animation-delay-75" />
            <div className="absolute inset-0 rounded-full border border-primary/10 animate-ping animation-delay-150" />
          </>
        )}

        {status === "thinking" && (
          <>
            {/* Thinking particles */}
            <div className="absolute top-2 right-4 w-1 h-1 bg-primary/60 rounded-full animate-bounce animation-delay-100" />
            <div className="absolute bottom-4 left-3 w-1 h-1 bg-accent/60 rounded-full animate-bounce animation-delay-200" />
            <div className="absolute top-6 left-5 w-1 h-1 bg-primary/40 rounded-full animate-bounce animation-delay-300" />
          </>
        )}

        {status === "speaking" && (
          <>
            {/* Speaking waves */}
            <div className="absolute inset-0 rounded-full border-2 border-primary/30 animate-ping" />
            <div className="absolute -inset-2 rounded-full border border-primary/20 animate-ping animation-delay-75" />
            <div className="absolute -inset-4 rounded-full border border-primary/10 animate-ping animation-delay-150" />
          </>
        )}
      </div>

      {/* Mode-specific ambient effects */}
      {mode === "wellness" && (
        <div className="absolute -inset-8 bg-gradient-radial from-primary/5 via-transparent to-transparent rounded-full animate-pulse" />
      )}
      
      {mode === "study" && (
        <div className="absolute -inset-6 border border-primary/10 rounded-full animate-pulse" />
      )}
    </div>
  );
};