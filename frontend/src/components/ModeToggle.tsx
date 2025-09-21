import { Button } from "@/components/ui/button";
import { AgentMode } from "./VoiceAgent";
import { Leaf, BookOpen } from "lucide-react";

interface ModeToggleProps {
  mode: AgentMode;
  onModeChange: (mode: AgentMode) => void;
}

export const ModeToggle = ({ mode, onModeChange }: ModeToggleProps) => {
  return (
    <div className="flex items-center space-x-2 bg-surface/80 backdrop-blur-sm rounded-lg p-1 border border-border">
      <Button
        variant={mode === "wellness" ? "default" : "ghost"}
        size="sm"
        onClick={() => onModeChange("wellness")}
        className={`
          flex items-center space-x-2 transition-all duration-200
          ${mode === "wellness" 
            ? "bg-primary text-primary-foreground shadow-sm" 
            : "text-text-soft hover:text-foreground hover:bg-surface"
          }
        `}
      >
        <Leaf className="w-3 h-3" />
        <span className="text-xs font-medium">Wellness Journal</span>
      </Button>
      
      <Button
        variant={mode === "study" ? "default" : "ghost"}
        size="sm"
        onClick={() => onModeChange("study")}
        className={`
          flex items-center space-x-2 transition-all duration-200
          ${mode === "study" 
            ? "bg-primary text-primary-foreground shadow-sm" 
            : "text-text-soft hover:text-foreground hover:bg-surface"
          }
        `}
      >
        <BookOpen className="w-3 h-3" />
        <span className="text-xs font-medium">Study Journal</span>
      </Button>
    </div>
  );
};