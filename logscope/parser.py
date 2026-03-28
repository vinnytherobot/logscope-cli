import re
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

@dataclass
class LogEntry:
    level: str
    message: str
    raw: str
    timestamp: Optional[datetime] = None
    service: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None


def _extract_json_observability(data: dict) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Pull service / trace / span from common JSON log shapes (K8s, OTel, Docker)."""
    k8s = data.get("kubernetes")
    k8s_d: dict = k8s if isinstance(k8s, dict) else {}
    pod_name = k8s_d.get("pod_name")
    if not pod_name and isinstance(k8s_d.get("pod"), dict):
        pod_name = k8s_d["pod"].get("name")

    service = (
        data.get("service")
        or data.get("service.name")
        or data.get("service_name")
        or pod_name
        or k8s_d.get("container_name")
        or data.get("container")
        or data.get("container.name")
        or data.get("logger")
        or data.get("logger.name")
    )
    if service is not None:
        service = str(service)

    trace_id = data.get("trace_id") or data.get("traceId") or data.get("trace.id")
    if not trace_id and isinstance(data.get("trace"), dict):
        trace_id = data["trace"].get("id")
    if not trace_id and isinstance(data.get("otelTraceID"), str):
        trace_id = data["otelTraceID"]
    if trace_id is not None:
        trace_id = str(trace_id)

    span_id = data.get("span_id") or data.get("spanId") or data.get("span.id")
    if span_id is not None:
        span_id = str(span_id)

    return service, trace_id, span_id

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
            
            # Find timestamp
            timestamp_str = data.get('timestamp', data.get('time', data.get('@timestamp')))
            timestamp = None
            if timestamp_str:
                try:
                    # Basic ISO parsing
                    timestamp = datetime.fromisoformat(str(timestamp_str).replace('Z', '+00:00'))
                except ValueError:
                    pass

            if level == "WARNING": level = "WARN"
            if level == "EMERGENCY": level = "FATAL"
            if level == "ERR": level = "ERROR"
            svc, tid, sid = _extract_json_observability(data)
            return LogEntry(
                level=level,
                message=message,
                raw=line,
                timestamp=timestamp,
                service=svc,
                trace_id=tid,
                span_id=sid,
            )
        except json.JSONDecodeError:
            pass

    # 2. Try typical log formats like [INFO], (WARN), ERROR:
    match = re.search(r'\[(TRACE|DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|ERR|CRITICAL|ALERT|FATAL|EMERGENCY)\]', line, re.IGNORECASE)
    if not match:
        # Try finding without brackets as a fallback, e.g. "INFO:" or "INFO - "
        match = re.search(r'\b(TRACE|DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|ERR|CRITICAL|ALERT|FATAL|EMERGENCY)\b', line, re.IGNORECASE)

    if match:
        level = match.group(1).upper()
        
        # Normalize levels
        if level == "WARNING":
            level = "WARN"
        if level == "EMERGENCY":
            level = "FATAL"
        if level == "ERR":
            level = "ERROR"
            
        # Remove the [LEVEL] part from the message for cleaner display
        message = line.replace(match.group(0), '', 1).strip()
        
        # Clean up common separators left behind like ": " or "- "
        if message.startswith(':') or message.startswith('-'):
            message = message[1:].strip()
            
        return LogEntry(level=level, message=message, raw=line, timestamp=extract_timestamp(line))
    
    # fallback
    return LogEntry(level="UNKNOWN", message=line, raw=line, timestamp=extract_timestamp(line))

def extract_timestamp(text: str) -> Optional[datetime]:
    """Helper to extract a timestamp from a raw string using regex."""
    pattern = r"(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)"
    match = re.search(pattern, text)
    if match:
        try:
            return datetime.fromisoformat(match.group(1).replace('Z', '+00:00'))
        except ValueError:
            return None
    return None
