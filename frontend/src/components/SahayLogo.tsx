import { AgentMode } from "./VoiceAgent";
import { Sparkles, Target } from "lucide-react";

interface SahayLogoProps {
  mode: AgentMode;
}

export const SahayLogo = ({ mode }: SahayLogoProps) => {
  const Icon = mode === "wellness" ? Sparkles : Target;
  
  return (
    <div className="flex items-center space-x-3">
      <div className={`
        w-10 h-10 rounded-full flex items-center justify-center
        ${mode === "wellness" 
          ? "bg-gradient-to-br from-primary/20 to-accent/20" 
          : "bg-gradient-to-br from-primary/20 to-accent/20"
        }
        border border-primary/30
      `}>
        <Icon className="w-5 h-5 text-primary" />
      </div>
      
      <div>
        <h1 className="text-lg font-semibold text-foreground">Sahay</h1>
        <p className="text-xs text-text-soft">
          {mode === "wellness" ? "Wellness Companion" : "Study Assistant"}
        </p>
      </div>
    </div>
  );
};