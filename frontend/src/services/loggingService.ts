/**
 * Logging Service for persistent logging in the frontend
 * Provides different log levels and optional persistence to localStorage
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

export interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  data?: any;
  source: string;
}

class LoggingService {
  private logs: LogEntry[] = [];
  private maxLogs = 1000; // Keep last 1000 logs
  private currentLevel: LogLevel = LogLevel.INFO;
  private enablePersistence = true;

  constructor() {
    // Load existing logs from localStorage
    this.loadLogs();
  }

  private loadLogs(): void {
    if (!this.enablePersistence) return;
    
    try {
      const stored = localStorage.getItem('sahay_logs');
      if (stored) {
        this.logs = JSON.parse(stored);
        // Keep only the most recent logs
        if (this.logs.length > this.maxLogs) {
          this.logs = this.logs.slice(-this.maxLogs);
        }
      }
    } catch (error) {
      console.error('Failed to load logs from localStorage:', error);
    }
  }

  private saveLogs(): void {
    if (!this.enablePersistence) return;
    
    try {
      localStorage.setItem('sahay_logs', JSON.stringify(this.logs));
    } catch (error) {
      console.error('Failed to save logs to localStorage:', error);
    }
  }

  private addLog(level: LogLevel, message: string, data?: any, source: string = 'App'): void {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      data,
      source
    };

    this.logs.push(entry);

    // Keep only the most recent logs
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }

    // Save to localStorage
    this.saveLogs();

    // Also log to console for development
    const logMessage = `[${entry.timestamp}] [${LogLevel[level]}] [${source}] ${message}`;
    switch (level) {
      case LogLevel.DEBUG:
        console.debug(logMessage, data);
        break;
      case LogLevel.INFO:
        console.info(logMessage, data);
        break;
      case LogLevel.WARN:
        console.warn(logMessage, data);
        break;
      case LogLevel.ERROR:
        console.error(logMessage, data);
        break;
    }
  }

  debug(message: string, data?: any, source?: string): void {
    if (this.currentLevel <= LogLevel.DEBUG) {
      this.addLog(LogLevel.DEBUG, message, data, source);
    }
  }

  info(message: string, data?: any, source?: string): void {
    if (this.currentLevel <= LogLevel.INFO) {
      this.addLog(LogLevel.INFO, message, data, source);
    }
  }

  warn(message: string, data?: any, source?: string): void {
    if (this.currentLevel <= LogLevel.WARN) {
      this.addLog(LogLevel.WARN, message, data, source);
    }
  }

  error(message: string, data?: any, source?: string): void {
    if (this.currentLevel <= LogLevel.ERROR) {
      this.addLog(LogLevel.ERROR, message, data, source);
    }
  }

  setLevel(level: LogLevel): void {
    this.currentLevel = level;
  }

  setPersistence(enabled: boolean): void {
    this.enablePersistence = enabled;
  }

  getLogs(level?: LogLevel, source?: string): LogEntry[] {
    let filteredLogs = this.logs;
    
    if (level !== undefined) {
      filteredLogs = filteredLogs.filter(log => log.level >= level);
    }
    
    if (source) {
      filteredLogs = filteredLogs.filter(log => log.source === source);
    }
    
    return filteredLogs;
  }

  clearLogs(): void {
    this.logs = [];
    if (this.enablePersistence) {
      localStorage.removeItem('sahay_logs');
    }
  }

  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }

  getLogStats(): { total: number; byLevel: Record<string, number>; bySource: Record<string, number> } {
    const byLevel: Record<string, number> = {};
    const bySource: Record<string, number> = {};

    this.logs.forEach(log => {
      const levelName = LogLevel[log.level];
      byLevel[levelName] = (byLevel[levelName] || 0) + 1;
      bySource[log.source] = (bySource[log.source] || 0) + 1;
    });

    return {
      total: this.logs.length,
      byLevel,
      bySource
    };
  }
}

// Export singleton instance
export const logger = new LoggingService();

// Set default level based on environment
if (import.meta.env.DEV) {
  logger.setLevel(LogLevel.DEBUG);
} else {
  logger.setLevel(LogLevel.INFO);
}
