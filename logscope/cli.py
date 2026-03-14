import sys
import typer
from pathlib import Path
from typing import Optional
from typing_extensions import Annotated
from .viewer import stream_logs, run_dashboard

app = typer.Typer(
    help="LogScope — Beautiful log viewer for the terminal",
    add_completion=False,
    rich_markup_mode="rich"
)

@app.command()
def main(
    log_file: Annotated[Optional[Path], typer.Argument(help="Path to the log file (leave empty to read from STDIN via pipe)")] = None,
    follow: Annotated[bool, typer.Option("--follow", "-f", help="Follow log output in real-time (like tail -f)")] = False,
    level: Annotated[Optional[str], typer.Option("--level", "-l", help="Filter logs by level (e.g. ERROR, WARNING, INFO)")] = None,
    search: Annotated[Optional[str], typer.Option("--search", "-s", help="Search string to filter logs")] = None,
    dashboard: Annotated[bool, typer.Option("--dashboard", "-d", help="Open visual dashboard showing log statistics")] = False,
    export_html: Annotated[Optional[Path], typer.Option("--export-html", help="Export the beautiful log output to an HTML file")] = None,
):
    """
    [blue]LogScope[/blue] parses standard logs and makes them [bold]beautiful[/bold] and [bold]readable[/bold].
    """
    if log_file is None:
        if sys.stdin.isatty():
            typer.echo("❌ Error: Please provide a log file path or pipe data to STDIN (cat file | logscope).", err=True)
            raise typer.Exit(1)
        file_obj = sys.stdin
    else:
        file_obj = open(log_file, "r", encoding="utf-8")

    try:
        if dashboard:
            run_dashboard(file_obj, follow=follow, level_filter=level, search_filter=search)
        else:
            stream_logs(file_obj, follow=follow, level=level, search=search, export_html=export_html)
    finally:
        if log_file is not None:
            file_obj.close()

if __name__ == "__main__":
    app()
