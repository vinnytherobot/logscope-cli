import re
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

# Compiled regex patterns for performance
_BRACKET_LEVEL_PATTERN = re.compile(
    r'\[(TRACE|DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|ERR|CRITICAL|ALERT|FATAL|EMERGENCY)\]',
    re.IGNORECASE
)
_BRACKETLESS_LEVEL_PATTERN = re.compile(
    r'\b(TRACE|DEBUG|INFO|NOTICE|WARN|WARNING|ERROR|ERR|CRITICAL|ALERT|FATAL|EMERGENCY)\b',
    re.IGNORECASE
)

# Multiple timestamp patterns for different log formats
_TIMESTAMP_PATTERNS = [
    # ISO 8601: 2026-03-21T10:00:00Z or 2026-03-21T10:00:00.123Z or 2026-03-21T10:00:00+00:00
    re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)'),
    # ISO-like with space: 2026-03-21 10:00:00 or 2026-03-21 10:00:00.123
    re.compile(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}(?:\.\d+)?)'),
    # Common Log Format / Apache: 21/Mar/2026:10:00:00 +0000 or [21/Mar/2026:10:00:00 +0000]
    re.compile(r'(\d{2}/[A-Za-z]{3}/\d{4}:\d{2}:\d{2}:\d{2}(?:\s+[+-]\d{4})?)'),
    # Syslog-style: Mar 21 10:00:00 (year is assumed current year)
    re.compile(r'([A-Za-z]{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})'),
    # Unix timestamp: 1711054800 (10 digits for seconds)
    re.compile(r'\b(\d{10})\b'),
]

# Month name mapping for parsing
_MONTH_MAP = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

@dataclass
class LogEntry:
    level: str
    message: str
    raw: str
    timestamp: Optional[datetime] = None
    service: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None


# Level normalization constants
_NORMALIZE_LEVEL_MAP = {
    "WARNING": "WARN",
    "EMERGENCY": "FATAL",
    "ERR": "ERROR",
}


def _normalize_level(level: str) -> str:
    """Normalize log level aliases to canonical forms."""
    return _NORMALIZE_LEVEL_MAP.get(level.upper(), level.upper())


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
            level = _normalize_level(data.get('level', data.get('severity', data.get('log.level', 'UNKNOWN'))))
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
    match = _BRACKET_LEVEL_PATTERN.search(line)
    if not match:
        # Try finding without brackets as a fallback, e.g. "INFO:" or "INFO - "
        match = _BRACKETLESS_LEVEL_PATTERN.search(line)

    if match:
        level = _normalize_level(match.group(1))

        # Remove the [LEVEL] part from the message for cleaner display
        message = line.replace(match.group(0), '', 1).strip()
        
        # Clean up common separators left behind like ": " or "- "
        if message.startswith(':') or message.startswith('-'):
            message = message[1:].strip()
            
        return LogEntry(level=level, message=message, raw=line, timestamp=extract_timestamp(line))
    
    # fallback
    return LogEntry(level="UNKNOWN", message=line, raw=line, timestamp=extract_timestamp(line))

def extract_timestamp(text: str) -> Optional[datetime]:
    """Extract a timestamp from a raw string using multiple format patterns."""
    for pattern in _TIMESTAMP_PATTERNS:
        match = pattern.search(text)
        if match:
            ts_str = match.group(1)
            try:
                # Try ISO format first (handles most cases)
                if '-' in ts_str and ('T' in ts_str or ' ' in ts_str[:10]):
                    # Handle ISO-like with space instead of T
                    return datetime.fromisoformat(ts_str.replace('Z', '+00:00').replace(' ', 'T'))
                # Handle Common Log Format: 21/Mar/2026:10:00:00 +0000
                elif '/' in ts_str:
                    parts = ts_str.split()
                    main_part = parts[0]
                    # Parse: DD/Mon/YYYY:HH:MM:SS
                    match_parts = re.match(r'(\d{2})/([A-Za-z]{3})/(\d{4}):(\d{2}):(\d{2}):(\d{2})', main_part)
                    if match_parts:
                        day, month_str, year, hour, minute, second = match_parts.groups()
                        month = _MONTH_MAP.get(month_str, 1)
                        return datetime(int(year), month, int(day), int(hour), int(minute), int(second))
                # Handle Syslog-style: Mar 21 10:00:00
                elif ts_str[0].isalpha():
                    match_parts = re.match(r'([A-Za-z]{3})\s+(\d{1,2})\s+(\d{2}):(\d{2}):(\d{2})', ts_str)
                    if match_parts:
                        month_str, day, hour, minute, second = match_parts.groups()
                        month = _MONTH_MAP.get(month_str, 1)
                        year = datetime.now().year  # Assume current year
                        return datetime(year, month, int(day), int(hour), int(minute), int(second))
                # Handle Unix timestamp
                elif ts_str.isdigit():
                    return datetime.fromtimestamp(int(ts_str))
            except (ValueError, OSError):
                continue
    return None
