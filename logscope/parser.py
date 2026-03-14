import re
import json
from dataclasses import dataclass

@dataclass
class LogEntry:
    level: str
    message: str
    raw: str

def parse_line(line: str) -> LogEntry:
    """Parse a single line of log and extract severity level."""
    line = line.strip()
    
    # 1. Check if JSON log object (common in docker/kubernetes/modern APIs)
    if line.startswith('{') and line.endswith('}'):
        try:
            data = json.loads(line)
            # Find level key
            level = str(data.get('level', data.get('severity', data.get('log.level', 'UNKNOWN')))).upper()
            # Find message key
            message = str(data.get('message', data.get('msg', data.get('text', line))))
            
            if level == "WARN": level = "WARNING"
            if level == "FATAL": level = "CRITICAL"
            return LogEntry(level=level, message=message, raw=line)
        except json.JSONDecodeError:
            pass

    # 2. Try typical log formats like [INFO], (WARN), ERROR:
    match = re.search(r'\[(INFO|WARN|WARNING|ERROR|DEBUG|CRITICAL|FATAL)\]', line, re.IGNORECASE)
    if not match:
        # Try finding without brackets as a fallback, e.g. "INFO:" or "INFO - "
        match = re.search(r'\b(INFO|WARN|WARNING|ERROR|DEBUG|CRITICAL|FATAL)\b', line, re.IGNORECASE)

    if match:
        level = match.group(1).upper()
        
        # Normalize levels
        if level == "WARN":
            level = "WARNING"
        if level == "FATAL":
            level = "CRITICAL"
            
        # Remove the [LEVEL] part from the message for cleaner display
        message = line.replace(match.group(0), '', 1).strip()
        
        # Clean up common separators left behind like ": " or "- "
        if message.startswith(':') or message.startswith('-'):
            message = message[1:].strip()
            
        return LogEntry(level=level, message=message, raw=line)

    # fallback
    return LogEntry(level="UNKNOWN", message=line, raw=line)
