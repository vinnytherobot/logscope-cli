import sys
import time
from pathlib import Path
from typing import Optional, List, TextIO

from rich.console import Console, Group
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.highlighter import RegexHighlighter
from rich.theme import Theme

from .parser import parse_line, LogEntry


class LogScopeHighlighter(RegexHighlighter):
    """Apply style to anything that looks like an IP address, URL, or timestamp."""
    base_style = "logscope."
    highlights = [
        r"(?P<ip>\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b)",
        r"(?P<url>https?://[a-zA-Z0-9./?=_%:-]+)",
        r"(?P<timestamp>\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:\.\d+)?Z?)",
        r"(?P<uuid>\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b)",
        r"(?P<email>\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b)",
    ]


theme = Theme({
    "logscope.ip": "bold green",
    "logscope.url": "underline blue",
    "logscope.timestamp": "cyan",
    "logscope.uuid": "bold magenta",
    "logscope.email": "underline yellow",
})

console = Console(theme=theme, highlighter=LogScopeHighlighter())

LEVEL_MAPPING = {
    "INFO": ("🔵", "bold blue"),
    "WARNING": ("🟡", "bold yellow"),
    "ERROR": ("🔴", "bold red"),
    "DEBUG": ("🟢", "bold green"),
    "CRITICAL": ("💥", "bold underline red"),
    "UNKNOWN": ("⚪", "dim white")
}


def format_log(entry: LogEntry) -> Text:
    """Format a log entry with colors and emojis."""
    icon, style = LEVEL_MAPPING.get(entry.level, LEVEL_MAPPING["UNKNOWN"])
    
    text = Text()
    text.append(f"{icon} {entry.level:<7} ", style=style)
    text.append(entry.message)
    return text


def get_lines(file: TextIO, follow: bool):
    """Generator that yields lines from a file, optionally tailing it."""
    # yield existing lines
    for line in file:
        if line.strip():
            yield line
            
    if not follow:
        return

    # Tailing stdin does not work effectively like a file.
    if file.name == '<stdin>':
        return

    # tailing
    console.print(f"[dim]-- 🔭 Tailing new logs... (Press Ctrl+C to exit) --[/dim]")
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


def stream_logs(file: TextIO, follow: bool, level: Optional[str] = None, search: Optional[str] = None, export_html: Optional[Path] = None):
    """Basic console mode: prints directly to stdout, supporting tails."""
    if export_html:
        console.record = True

    try:
        for line in get_lines(file, follow):
            entry = parse_line(line)
            
            # Apply filters
            if level and entry.level != level.upper():
                continue
                
            if search and search.lower() not in line.lower():
                continue
                
            formatted = format_log(entry)
            console.print(formatted)
    finally:
        if export_html:
            console.save_html(str(export_html), clear=False)
            console.print(f"\n[bold green]✅ Logs exported successfully to {export_html}[/bold green]")


def run_dashboard(file: TextIO, follow: bool, level_filter: Optional[str] = None, search_filter: Optional[str] = None):
    """Dashboard mode: Shows a summary stats panel and recent logs layout."""
    
    stats = {
        "ERROR": 0,
        "WARNING": 0,
        "INFO": 0,
        "DEBUG": 0,
        "CRITICAL": 0,
        "UNKNOWN": 0
    }
    
    recent_logs: List[Text] = []
    MAX_LOGS = 25 # Number of lines to keep in the scrolling window

    def generate_layout() -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="body")
        )
        
        # Stats table
        table = Table(show_header=False, expand=True, border_style="dim", box=None)
        table.add_column("Errors", justify="center")
        table.add_column("Warnings", justify="center")
        table.add_column("Info", justify="center")
        table.add_column("Critical", justify="center")
        
        table.add_row(
            f"[bold red]🔴 Errors: {stats.get('ERROR', 0)}[/bold red]",
            f"[bold yellow]🟡 Warnings: {stats.get('WARNING', 0)}[/bold yellow]",
            f"[bold blue]🔵 Info: {stats.get('INFO', 0)}[/bold blue]",
            f"[bold magenta]💥 Critical: {stats.get('CRITICAL', 0)}[/bold magenta]"
        )
        
        layout["header"].update(Panel(table, title="[bold]✨ LogScope Live Dashboard[/bold]", border_style="cyan"))
        
        # Logs
        log_group = Group(*recent_logs)
        title = "Recent Logs (Auto-highlight enabled)"
        if follow:
            title += " - [blink green]● LIVE[/blink green]"
            
        layout["body"].update(Panel(log_group, title=title))
        
        return layout

    console.clear()
    
    try:
        with Live(generate_layout(), console=console, refresh_per_second=10) as live:
            for line in get_lines(file, follow):
                entry = parse_line(line)
                
                # Apply filters
                if level_filter and entry.level != level_filter.upper():
                    continue
                if search_filter and search_filter.lower() not in line.lower():
                    continue
                    
                # Update stats tally
                entry_level = entry.level if entry.level in stats else "UNKNOWN"
                stats[entry_level] += 1

                formatted = format_log(entry)
                recent_logs.append(formatted)
                if len(recent_logs) > MAX_LOGS:
                    recent_logs.pop(0)
                    
                live.update(generate_layout())
    except KeyboardInterrupt:
        pass
