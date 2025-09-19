import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { logger, LogLevel, LogEntry } from '@/services/loggingService';
import { Download, Trash2, Eye, EyeOff } from 'lucide-react';

export const LogViewer = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<LogEntry[]>([]);
  const [levelFilter, setLevelFilter] = useState<LogLevel | 'ALL'>('ALL');
  const [sourceFilter, setSourceFilter] = useState<string>('ALL');
  const [isVisible, setIsVisible] = useState(false);

  const refreshLogs = () => {
    const allLogs = logger.getLogs();
    setLogs(allLogs);
  };

  useEffect(() => {
    refreshLogs();
    const interval = setInterval(refreshLogs, 1000); // Refresh every second
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    let filtered = logs;

    if (levelFilter !== 'ALL') {
      filtered = filtered.filter(log => log.level >= levelFilter);
    }

    if (sourceFilter !== 'ALL') {
      filtered = filtered.filter(log => log.source === sourceFilter);
    }

    setFilteredLogs(filtered);
  }, [logs, levelFilter, sourceFilter]);

  const getLevelColor = (level: LogLevel) => {
    switch (level) {
      case LogLevel.DEBUG: return 'bg-gray-500';
      case LogLevel.INFO: return 'bg-blue-500';
      case LogLevel.WARN: return 'bg-yellow-500';
      case LogLevel.ERROR: return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const exportLogs = () => {
    const logData = logger.exportLogs();
    const blob = new Blob([logData], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sahay-logs-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const clearLogs = () => {
    logger.clearLogs();
    setLogs([]);
    setFilteredLogs([]);
  };

  const stats = logger.getLogStats();
  const sources = Array.from(new Set(logs.map(log => log.source)));

  if (!isVisible) {
    return (
      <Button
        variant="outline"
        size="sm"
        onClick={() => setIsVisible(true)}
        className="fixed bottom-4 right-4 z-50"
      >
        <Eye className="w-4 h-4 mr-2" />
        View Logs ({logs.length})
      </Button>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-4xl h-[80vh] flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <CardTitle className="text-lg font-semibold">Sahay Logs</CardTitle>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={exportLogs}>
              <Download className="w-4 h-4 mr-2" />
              Export
            </Button>
            <Button variant="outline" size="sm" onClick={clearLogs}>
              <Trash2 className="w-4 h-4 mr-2" />
              Clear
            </Button>
            <Button variant="outline" size="sm" onClick={() => setIsVisible(false)}>
              <EyeOff className="w-4 h-4 mr-2" />
              Close
            </Button>
          </div>
        </CardHeader>
        
        <CardContent className="flex-1 flex flex-col space-y-4">
          {/* Stats */}
          <div className="flex flex-wrap gap-2 text-sm">
            <Badge variant="outline">Total: {stats.total}</Badge>
            {Object.entries(stats.byLevel).map(([level, count]) => (
              <Badge key={level} variant="outline" className={getLevelColor(LogLevel[level as keyof typeof LogLevel])}>
                {level}: {count}
              </Badge>
            ))}
          </div>

          {/* Filters */}
          <div className="flex space-x-4">
            <Select value={levelFilter} onValueChange={(value) => setLevelFilter(value as LogLevel | 'ALL')}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Level" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">All Levels</SelectItem>
                <SelectItem value={LogLevel.DEBUG.toString()}>Debug</SelectItem>
                <SelectItem value={LogLevel.INFO.toString()}>Info</SelectItem>
                <SelectItem value={LogLevel.WARN.toString()}>Warn</SelectItem>
                <SelectItem value={LogLevel.ERROR.toString()}>Error</SelectItem>
              </SelectContent>
            </Select>

            <Select value={sourceFilter} onValueChange={setSourceFilter}>
              <SelectTrigger className="w-40">
                <SelectValue placeholder="Source" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">All Sources</SelectItem>
                {sources.map(source => (
                  <SelectItem key={source} value={source}>{source}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Logs */}
          <ScrollArea className="flex-1 border rounded-md p-4">
            <div className="space-y-2">
              {filteredLogs.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">No logs to display</p>
              ) : (
                filteredLogs.map((log, index) => (
                  <div key={index} className="flex items-start space-x-3 p-2 rounded hover:bg-muted/50">
                    <Badge className={`${getLevelColor(log.level)} text-white text-xs`}>
                      {LogLevel[log.level]}
                    </Badge>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 text-sm">
                        <span className="text-muted-foreground">{formatTimestamp(log.timestamp)}</span>
                        <Badge variant="outline" className="text-xs">{log.source}</Badge>
                      </div>
                      <p className="text-sm mt-1 break-words">{log.message}</p>
                      {log.data && (
                        <pre className="text-xs text-muted-foreground mt-1 bg-muted p-2 rounded overflow-x-auto">
                          {JSON.stringify(log.data, null, 2)}
                        </pre>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};
