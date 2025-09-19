import { AgentStatus, AgentMode } from "./VoiceAgent";
import { Ear, Brain, Volume2, Circle } from "lucide-react";

interface StatusIndicatorProps {
  status: AgentStatus;
  mode: AgentMode;
}

export const StatusIndicator = ({ status, mode }: StatusIndicatorProps) => {
  const getStatusConfig = () => {
    switch (status) {
      case "listening":
        return {
          icon: Ear,
          label: "Listening",
          description: "I'm ready to hear what you have to say",
          color: "text-primary"
        };
      case "thinking":
        return {
          icon: Brain,
          label: "Processing",
          description: "Let me consider your message...",
          color: "text-accent"
        };
      case "speaking":
        return {
          icon: Volume2,
          label: "Speaking",
          description: "Sharing my thoughts with you",
          color: "text-primary"
        };
      case "idle":
      default:
        return {
          icon: Circle,
          label: "Ready",
          description: "Here to help whenever you need",
          color: "text-text-soft"
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <div className="flex flex-col items-center space-y-2 animate-fade-in">
      <div className={`flex items-center space-x-2 ${config.color}`}>
        <Icon className="w-4 h-4" />
        <span className="text-sm font-medium">{config.label}</span>
      </div>
      
      <p className="text-xs text-text-soft text-center max-w-48">
        {config.description}
      </p>
    </div>
  );
};