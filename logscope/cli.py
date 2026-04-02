import sys
import gzip
import typer
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from typing_extensions import Annotated
from .viewer import stream_logs, run_dashboard, manager
from .themes import DEFAULT_THEMES

app = typer.Typer(
    help="LogScope — Beautiful log viewer for the terminal",
    add_completion=False,
    rich_markup_mode="rich"
)

def parse_relative_time(time_str: str) -> Optional[datetime]:
    """Parse relative time like '10m', '1h', '2d' or ISO strings."""
    if not time_str:
        return None

    # Check if absolute ISO format first
    try:
        return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
    except ValueError:
        pass

    # Regex for relative formats: <digit><unit>
    match = re.match(r'^(\d+)([smhd])$', time_str.lower())
    if not match:
        return None

    value, unit = int(match.group(1)), match.group(2)
    now = datetime.now()

    if unit == 's': return now - timedelta(seconds=value)
    if unit == 'm': return now - timedelta(minutes=value)
    if unit == 'h': return now - timedelta(hours=value)
    if unit == 'd': return now - timedelta(days=value)

    return None

def load_theme(requested_theme: Optional[str], no_color: bool = False):
    """Load theme from config file or use requested/default. Persist if requested."""
    config_file = Path(".logscoperc")
    if not config_file.exists():
        config_file = Path.home() / ".logscoperc"

    config = {}
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            pass

    # If requested via CLI, save it to the config for future use
    if requested_theme:
        config["theme"] = requested_theme
        try:
            # We prefer saving to local .logscoperc if it exists, otherwise home. 
            # If neither exists, we'll create one in the home directory for persistence.
            save_path = Path(".logscoperc") if Path(".logscoperc").exists() else Path.home() / ".logscoperc"
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            manager.console.print(f"[bold green]✅ Theme '{requested_theme}' saved as your default preference![/bold green]")
        except Exception as e:
            manager.console.print(f"[dim red]⚠️ Failed to save theme preference: {e}[/dim red]")
    else:
        requested_theme = config.get("theme", "default")

    if "custom_themes" in config:
        DEFAULT_THEMES.update(config["custom_themes"])

    manager.apply_theme(requested_theme, no_color=no_color)

@app.command()
def main(
    log_file: Annotated[Optional[Path], typer.Argument(help="Path to the log file (leave empty to read from STDIN via pipe)")] = None,
    follow: Annotated[bool, typer.Option("--follow", "-f", help="Follow log output in real-time (like tail -f)")] = False,
    level: Annotated[Optional[str], typer.Option("--level", "-l", help="Filter by level; comma-separated for multiple (e.g. ERROR,WARN,INFO)")] = None,
    search: Annotated[Optional[str], typer.Option("--search", "-s", help="Search string to filter logs (substring unless --regex)")] = None,
    dashboard: Annotated[bool, typer.Option("--dashboard", "-d", help="Open visual dashboard showing log statistics")] = False,
    export_html: Annotated[Optional[Path], typer.Option("--export-html", help="Export the beautiful log output to an HTML file")] = None,
    line_numbers: Annotated[bool, typer.Option("--line-numbers", "-n", help="Show line numbers for each log message")] = False,
    since: Annotated[Optional[str], typer.Option("--since", help="Show logs since a point in time (e.g. '1h', '30m', '2026-01-01T00:00:00')")] = None,
    until: Annotated[Optional[str], typer.Option("--until", help="Show logs until a point in time")] = None,
    theme: Annotated[Optional[str], typer.Option("--theme", "-t", help="Choose a theme for colors and emojis (default, neon, ocean, forest, minimal)")] = None,
    use_regex: Annotated[bool, typer.Option("--regex", "-e", help="Treat --search as a regular expression")] = False,
    case_sensitive: Annotated[bool, typer.Option("--case-sensitive", help="Case-sensitive substring or regex search")] = False,
    invert_match: Annotated[bool, typer.Option("--invert-match", "-v", help="Hide lines that match --search (grep -v)")] = False,
    no_color: Annotated[bool, typer.Option("--no-color", help="Disable colors and terminal highlighting")] = False,
    highlight: Annotated[Optional[str], typer.Option("--highlight", "-H", help="Highlight specific keyword in log messages (can be used multiple times)")] = None,
    highlight_color: Annotated[str, typer.Option("--highlight-color", help="Rich style for highlighted keywords (default: bold magenta)")] = "bold magenta",
):
    """
    [blue]LogScope[/blue] parses standard logs and makes them [bold]beautiful[/bold] and [bold]readable[/bold].
    """
    if use_regex and not search:
        typer.echo("❌ Error: --regex requires --search.", err=True)
        raise typer.Exit(1)
    if invert_match and not search:
        typer.echo("❌ Error: --invert-match requires --search.", err=True)
        raise typer.Exit(1)

    search_pattern = None
    if search and use_regex:
        try:
            flags = 0 if case_sensitive else re.IGNORECASE
            search_pattern = re.compile(search, flags)
        except re.error as exc:
            typer.echo(f"❌ Error: invalid regular expression: {exc}", err=True)
            raise typer.Exit(1)

    if log_file is None:
        if sys.stdin.isatty():
            typer.echo("❌ Error: Please provide a log file path or pipe data to STDIN (cat file | logscope).", err=True)
            raise typer.Exit(1)
        file_obj = sys.stdin
    else:
        if log_file.suffix.lower() == ".gz":
            file_obj = gzip.open(log_file, "rt", encoding="utf-8", errors="replace")
        else:
            file_obj = open(log_file, "r", encoding="utf-8", errors="replace")

    since_dt = parse_relative_time(since) if since else None
    until_dt = parse_relative_time(until) if until else None

    load_theme(theme, no_color=no_color)

    # Inform user about themes only if they are using default and haven't hidden the tip by having a config
    has_config = Path(".logscoperc").exists() or (Path.home() / ".logscoperc").exists()
    if not theme and not has_config:
        manager.console.print("[dim]💡 Tip: Use '--theme' or create a '.logscoperc' file to change colors. Themes: neon, ocean, forest, minimal[/dim]\n")

    try:
        if dashboard:
            run_dashboard(
                file_obj,
                follow=follow,
                level_filter=level,
                search_filter=search,
                show_line_numbers=line_numbers,
                since=since_dt,
                until=until_dt,
                use_regex=use_regex,
                search_pattern=search_pattern,
                case_sensitive=case_sensitive,
                invert_match=invert_match,
                highlight=highlight,
                highlight_color=highlight_color,
            )
        else:
            stream_logs(
                file_obj,
                follow=follow,
                level=level,
                search=search,
                export_html=export_html,
                show_line_numbers=line_numbers,
                since=since_dt,
                until=until_dt,
                use_regex=use_regex,
                search_pattern=search_pattern,
                case_sensitive=case_sensitive,
                invert_match=invert_match,
                highlight=highlight,
                highlight_color=highlight_color,
            )
    finally:
        if log_file is not None:
            file_obj.close()

if __name__ == "__main__":
    app()
