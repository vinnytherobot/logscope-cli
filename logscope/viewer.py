import sys
import time
import re
from collections import deque
from pathlib import Path
from datetime import datetime
from typing import Optional, List, TextIO, Set, Pattern

from rich.console import Console, Group
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.highlighter import RegexHighlighter
from rich.theme import Theme

from .parser import parse_line, LogEntry
from .themes import DEFAULT_THEMES

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

class LogScopeHighlighter(RegexHighlighter):
    """Apply style to anything that looks like an IP address, URL, or timestamp."""
    base_style = "logscope."
    highlights = [
        r"(?P<ip>\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b)",
        r"(?P<url>https?://[a-zA-Z0-9./?=#_%:-]+)",
        r"(?P<timestamp>\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)",
        r"(?P<uuid>\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b)",
        r"(?P<email>\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b)",
        r"(?P<path>(?:[a-zA-Z]:|\/)[a-zA-Z0-9._\-\/\\ ]+)",
        r"(?P<status_ok>\b(200|201|204)\b)",
        r"(?P<status_warn>\b(301|302|400|401|403|404)\b)",
        r"(?P<status_err>\b(500|502|503|504)\b)",
        r"(?P<method>\b(GET|POST|PUT|DELETE|PATCH|OPTIONS|HEAD)\b)",
    ]


class LogScopeManager:
    """Manages the console state and current theme."""
    def __init__(self, theme_name: str = "default"):
        self._no_color = False
        self.apply_theme(theme_name)

    def apply_theme(self, theme_name_or_dict, no_color: bool = False):
        self._no_color = no_color
        if isinstance(theme_name_or_dict, str):
            theme_config = DEFAULT_THEMES.get(theme_name_or_dict, DEFAULT_THEMES["default"])
        else:
            theme_config = theme_name_or_dict

        self.level_mapping = theme_config["levels"]
        self.rich_theme = Theme(theme_config["highlights"])
        self.console = Console(
            theme=self.rich_theme,
            highlighter=LogScopeHighlighter(),
            no_color=no_color,
        )

    def format_log(self, entry: LogEntry, line_number: Optional[int] = None) -> Text:
        """Format a log entry with current theme's colors and emojis."""
        icon, style = self.level_mapping.get(entry.level, self.level_mapping.get("UNKNOWN", ("⚪", "dim white")))

        text = Text()
        if line_number is not None:
            text.append(f"{line_number:>4} │ ", style="dim")

        text.append(f"{icon} {entry.level:<7} ", style=style)

        meta_parts: List[str] = []
        if entry.service:
            meta_parts.append(f"svc:{entry.service}")
        if entry.trace_id:
            tid = entry.trace_id
            if len(tid) > 14:
                tid = tid[:6] + "…" + tid[-4:]
            meta_parts.append(f"trace:{tid}")
        if entry.span_id:
            sid = entry.span_id
            if len(sid) > 12:
                sid = sid[:6] + "…" + sid[-3:]
            meta_parts.append(f"span:{sid}")
        if meta_parts:
            text.append("[" + "] [".join(meta_parts) + "] ", style="dim cyan")

        text.append(entry.message)
        return text

# Global manager instance
manager = LogScopeManager()


def _normalize_level_token(token: str) -> str:
    t = token.strip().upper()
    if t == "WARNING":
        return "WARN"
    if t == "ERR":
        return "ERROR"
    if t == "EMERGENCY":
        return "FATAL"
    return t


# Severity order for --min-level (low → high). UNKNOWN is handled separately in filters.
LEVEL_ORDER: List[str] = [
    "TRACE",
    "DEBUG",
    "INFO",
    "NOTICE",
    "WARN",
    "ERROR",
    "CRITICAL",
    "ALERT",
    "FATAL",
]


def parse_min_level(min_level: Optional[str]) -> Optional[int]:
    """Return index in LEVEL_ORDER for --min-level, or None if not set."""
    if not min_level or not min_level.strip():
        return None
    token = _normalize_level_token(min_level)
    if token not in LEVEL_ORDER:
        return None
    return LEVEL_ORDER.index(token)


def line_passes_min_level(entry_level: str, min_idx: Optional[int]) -> bool:
    if min_idx is None:
        return True
    if entry_level == "UNKNOWN":
        return True
    if entry_level not in LEVEL_ORDER:
        return True
    return LEVEL_ORDER.index(entry_level) >= min_idx


def parse_level_filter(level: Optional[str]) -> Optional[Set[str]]:
    if not level or not level.strip():
        return None
    parts = {_normalize_level_token(p) for p in level.split(",") if p.strip()}
    return parts or None


def line_passes_level(entry_level: str, allowed: Optional[Set[str]]) -> bool:
    if not allowed:
        return True
    return entry_level in allowed


def entry_passes_filters(
    entry: LogEntry,
    level_set: Optional[Set[str]],
    min_idx: Optional[int],
) -> bool:
    if not line_passes_min_level(entry.level, min_idx):
        return False
    if not line_passes_level(entry.level, level_set):
        return False
    return True


def line_passes_search(
    line: str,
    search: Optional[str],
    *,
    pattern: Optional[Pattern[str]],
    use_regex: bool,
    case_sensitive: bool,
    invert_match: bool,
) -> bool:
    if not search:
        return True
    if use_regex and pattern is not None:
        matched = pattern.search(line) is not None
    elif case_sensitive:
        matched = search in line
    else:
        matched = search.lower() in line.lower()
    if invert_match:
        return not matched
    return matched


def get_lines(file: TextIO, follow: bool):
    """Generator that yields lines from a file, optionally tailing it."""
    # yield existing lines
    for line in file:
        if line.strip():
            yield line
            
    if not follow:
        return

    # tailing
    manager.console.print(f"[dim]-- 🔭 Tailing new logs... (Press Ctrl+C to exit) --[/dim]")
    try:
        while True:
            line = file.readline()
            if not line:
                time.sleep(0.1)
                continue
            if line.strip():
                yield line
    except KeyboardInterrupt:
        return


SEVERE_LEVELS = frozenset({"ERROR", "CRITICAL", "ALERT", "FATAL"})


def _binary_sparkline(bits: List[int], width: int = 20) -> str:
    """Compact activity strip: █ = severe line, ░ = calm."""
    if not bits:
        return "░" * min(width, 20)
    tail = bits[-width:]
    return "".join("█" if x else "░" for x in tail)


def run_pulse_stream(
    file: TextIO,
    follow: bool,
    level: Optional[str] = None,
    search: Optional[str] = None,
    show_line_numbers: bool = False,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    *,
    use_regex: bool = False,
    search_pattern: Optional[Pattern[str]] = None,
    case_sensitive: bool = False,
    invert_match: bool = False,
    min_idx: Optional[int] = None,
    max_visible: int = 48,
):
    """Futuristic full-screen stream with a live Signal Deck (rate, health, sparkline)."""
    level_set = parse_level_filter(level)
    recent_logs: List[Text] = []
    line_times: deque = deque(maxlen=500)
    severe_bits: deque[int] = deque(maxlen=48)
    rolling_severe: deque[int] = deque(maxlen=40)
    total_matched = 0
    start_clock = time.time()

    def deck_panel() -> Panel:
        now = time.time()
        window = 1.0
        recent_ts = [t for t in line_times if now - t <= window]
        rate = len(recent_ts) / window if recent_ts else 0.0
        elapsed = max(now - start_clock, 0.001)
        avg_rate = total_matched / elapsed
        if rolling_severe:
            bad = sum(rolling_severe)
            health = max(0, 100 - int(100 * bad / len(rolling_severe)))
        else:
            health = 100
        spark = _binary_sparkline(list(severe_bits), width=22)
        deck = Text()
        deck.append("⚡ Pulse Signal Deck ", style="bold cyan")
        deck.append("│ ", style="dim")
        deck.append(f"{rate:5.1f}/s", style="bold white")
        deck.append(" instant  ", style="dim")
        deck.append(f"{avg_rate:5.1f}/s", style="dim")
        deck.append(" avg │ ", style="dim")
        deck.append(f"signal {health:3d}%", style="bold green" if health >= 70 else ("bold yellow" if health >= 40 else "bold red"))
        deck.append(" │ ", style="dim")
        deck.append(spark, style="magenta")
        deck.append(" │ ", style="dim")
        deck.append(f"lines {total_matched}", style="cyan")
        if follow:
            deck.append("  ● LIVE", style="blink green")
        return Panel(deck, border_style="bright_blue", padding=(0, 1))

    def layout_view() -> Layout:
        root = Layout()
        root.split_column(
            Layout(name="logs", ratio=1),
            Layout(name="deck", size=3),
        )
        log_group = Group(*recent_logs) if recent_logs else Text("Waiting for log lines…", style="dim")
        root["logs"].update(Panel(log_group, title="[bold]LogScope Pulse[/bold]", border_style="cyan"))
        root["deck"].update(deck_panel())
        return root

    manager.console.clear()
    try:
        with Live(layout_view(), console=manager.console, refresh_per_second=12) as live:
            line_count = 0
            for line in get_lines(file, follow):
                line_count += 1
                entry = parse_line(line)

                if not entry_passes_filters(entry, level_set, min_idx):
                    continue

                if not line_passes_search(
                    line,
                    search,
                    pattern=search_pattern,
                    use_regex=use_regex,
                    case_sensitive=case_sensitive,
                    invert_match=invert_match,
                ):
                    continue

                if entry.timestamp:
                    if since and entry.timestamp.replace(tzinfo=None) < since.replace(tzinfo=None):
                        continue
                    if until and entry.timestamp.replace(tzinfo=None) > until.replace(tzinfo=None):
                        continue

                total_matched += 1
                line_times.append(time.time())
                is_sev = 1 if entry.level in SEVERE_LEVELS else 0
                severe_bits.append(is_sev)
                rolling_severe.append(is_sev)

                formatted = manager.format_log(entry, line_number=line_count if show_line_numbers else None)
                recent_logs.append(formatted)
                if len(recent_logs) > max_visible:
                    recent_logs.pop(0)
                live.update(layout_view())
    except KeyboardInterrupt:
        pass


def stream_logs(
    file: TextIO,
    follow: bool,
    level: Optional[str] = None,
    search: Optional[str] = None,
    export_html: Optional[Path] = None,
    show_line_numbers: bool = False,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    *,
    use_regex: bool = False,
    search_pattern: Optional[Pattern[str]] = None,
    case_sensitive: bool = False,
    invert_match: bool = False,
    min_idx: Optional[int] = None,
):
    """Basic console mode: prints directly to stdout, supporting tails."""
    if export_html:
        manager.console.record = True

    level_set = parse_level_filter(level)

    line_count = 0
    try:
        for line in get_lines(file, follow):
            line_count += 1
            entry = parse_line(line)

            if not entry_passes_filters(entry, level_set, min_idx):
                continue

            if not line_passes_search(
                line,
                search,
                pattern=search_pattern,
                use_regex=use_regex,
                case_sensitive=case_sensitive,
                invert_match=invert_match,
            ):
                continue

            if entry.timestamp:
                if since and entry.timestamp.replace(tzinfo=None) < since.replace(tzinfo=None):
                    continue
                if until and entry.timestamp.replace(tzinfo=None) > until.replace(tzinfo=None):
                    continue
                
            formatted = manager.format_log(entry, line_number=line_count if show_line_numbers else None)
            manager.console.print(formatted)
    finally:
        if export_html:
            manager.console.save_html(str(export_html), clear=False)
            manager.console.print(f"\n[bold green]✅ Logs exported successfully to {export_html}[/bold green]")


def run_dashboard(
    file: TextIO,
    follow: bool,
    level_filter: Optional[str] = None,
    search_filter: Optional[str] = None,
    show_line_numbers: bool = False,
    since: Optional[datetime] = None,
    until: Optional[datetime] = None,
    *,
    use_regex: bool = False,
    search_pattern: Optional[Pattern[str]] = None,
    case_sensitive: bool = False,
    invert_match: bool = False,
    min_idx: Optional[int] = None,
):
    """Dashboard mode: Shows a summary stats panel and recent logs layout."""

    level_set = parse_level_filter(level_filter)

    stats = {
        "FATAL": 0,
        "ALERT": 0,
        "CRITICAL": 0,
        "ERROR": 0,
        "WARN": 0,
        "NOTICE": 0,
        "INFO": 0,
        "DEBUG": 0,
        "TRACE": 0,
        "UNKNOWN": 0
    }
    
    total_processed = 0
    recent_logs: List[Text] = []
    MAX_LOGS = 25 # Number of lines to keep in the scrolling window

    def generate_layout() -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="body")
        )
        
        # Stats table
        table = Table(show_header=False, expand=True, border_style="dim", box=None)
        table.add_column("C1", justify="center")
        table.add_column("C2", justify="center")
        table.add_column("C3", justify="center")
        table.add_column("C4", justify="center")
        
        table.add_row(
            f"[bold dark_red]💀 Fatal: {stats.get('FATAL', 0)}[/bold dark_red]",
            f"[bold magenta]💥 Critical: {stats.get('CRITICAL', 0)}[/bold magenta]",
            f"[bold red]🔴 Errors: {stats.get('ERROR', 0)}[/bold red]",
            f"[bold yellow]🟡 Warns: {stats.get('WARN', 0)}[/bold yellow]"
        )
        table.add_row(
            f"[bold green]🔵 Info: {stats.get('INFO', 0)}[/bold green]",
            f"[bold blue]🐛 Debug: {stats.get('DEBUG', 0)}[/bold blue]",
            f"[dim white]🔍 Trace: {stats.get('TRACE', 0)}[/dim white]",
            f"[dim white]⚪ Unknown: {stats.get('UNKNOWN', 0)}[/dim white]"
        )
        
        layout["header"].update(Panel(table, title=f"[bold]✨ LogScope Live Dashboard — Total: {total_processed}[/bold]", border_style="cyan"))
        
        # Logs
        log_group = Group(*recent_logs)
        title = "Recent Logs (Auto-highlight enabled)"
        if follow:
            title += " - [blink green]● LIVE[/blink green]"
            
        layout["body"].update(Panel(log_group, title=title))
        
        return layout

    manager.console.clear()
    
    try:
        with Live(generate_layout(), console=manager.console, refresh_per_second=10) as live:
            for line in get_lines(file, follow):
                entry = parse_line(line)

                if not entry_passes_filters(entry, level_set, min_idx):
                    continue
                if not line_passes_search(
                    line,
                    search_filter,
                    pattern=search_pattern,
                    use_regex=use_regex,
                    case_sensitive=case_sensitive,
                    invert_match=invert_match,
                ):
                    continue

                if entry.timestamp:
                    if since and entry.timestamp.replace(tzinfo=None) < since.replace(tzinfo=None):
                        continue
                    if until and entry.timestamp.replace(tzinfo=None) > until.replace(tzinfo=None):
                        continue
                    
                # Update stats tally
                total_processed += 1
                entry_level = entry.level if entry.level in stats else "UNKNOWN"
                stats[entry_level] += 1

                formatted = manager.format_log(entry, line_number=total_processed if show_line_numbers else None)
                recent_logs.append(formatted)
                if len(recent_logs) > MAX_LOGS:
                    recent_logs.pop(0)
                    
                live.update(generate_layout())
    except KeyboardInterrupt:
        pass
