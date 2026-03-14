<div align="center">
  <img src="https://via.placeholder.com/150/000000/FFFFFF/?text=LogScope" alt="LogScope Logo" width="150" height="150">
  
  # LogScope
  
  **Beautiful, simple, and powerful log viewer for the terminal.**
  
  [![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
  [![Typer](https://img.shields.io/badge/CLI-Typer-green)](https://typer.tiangolo.com/)
  [![Rich](https://img.shields.io/badge/UI-Rich-magenta)](https://rich.readthedocs.io/)
  [![License](https://img.shields.io/badge/License-MIT-gray.svg)](#)
</div>

<p align="center">
  A modern CLI tool that turns boring text logs or messy JSON lines into stunning, structured, and colorful terminal outputs—complete with a live dashboard, smart highlighting, and HTML exporting.
</p>

---

## Features that shine

*   **Fast & Lightweight**: Tail files natively or stream huge data directly via pipes (`cat server.log | logscope`).
*   **Colored & Structured Logs**: Automatically identifies `INFO`, `WARNING`, `ERROR`, `CRITICAL`, and `DEBUG`, applying beautiful typography.
*   **Universal Parser**: Reads typical bracket logs (`[INFO]`) **and** parses modern NDJSON / JSON logs out of the box (e.g., Kubernetes, Docker).
*   **Auto-Highlighting**: Magically highlights `IPs`, `URLs`, `Dates/Timestamps`, `UUIDs`, and `E-Mails` with dynamic colors.
*   **Live Dashboard**: Watch logs stream in real-time alongside a live statistics panel keeping track of Error vs Info counts (`--dashboard`).
*   **HTML Export**: Loved your console output so much you want to share it? Export the beautiful log structure directly to an HTML file to share with your team! (`--export-html results.html`)
*   **Filtering**: Only see what matters. Filter by level (`--level ERROR`) or via text search (`--search timeout`).

---

## Installation

Ensure you have Python 3.9+ and pip installed.

```bash
# Clone the repository
git clone https://github.com/vinnytherobot/logscope.git
cd logscope

# Install via Poetry
poetry install
poetry run logscope --help

# Or install globally via pip
pip install -e .
```

---

## Usage & Examples

### Using a File
```bash
# Basic colorized look
logscope /var/log/syslog

# Tailing a log in real-time (like tail -f)
logscope backend.log --follow

# Filter only errors
logscope production.log --level ERROR

# Search text dynamically
logscope server.log --search "Connection Timeout"
```

### Piping from other commands (Stdin support)
LogScope acts as a brilliant text reformatter for other tools!

```bash
kubectl logs my-pod -f | logscope
docker logs api-gateway | logscope --level CRITICAL
cat nginx.log | grep -v GET | logscope --dashboard
```

### The Live Dashboard Mode
Monitor your logs like a pro with a live dashboard tracking error occurrences.

```bash
logscope app.log --dashboard --follow
```

### Exporting to HTML
Need to attach the logs to a Jira ticket or Slack message but want to keep the formatting?

```bash
logscope failed_job.log --export-html bug_report.html
```

---

## Stack

*   [**Rich**](https://github.com/Textualize/rich) -> UI Layouts, Colors, Highlighters, HTML Export.
*   [**Typer**](https://github.com/tiangolo/typer) -> Modern, fast, and robust CLI creation.
*   **Pathlib / Sys** -> File and standard input streaming.

## Contributing
Open an issue or submit a pull request! Tests are written using `pytest`.

```bash
# Running tests
pytest tests/
```

## License
MIT License.

Made by [vinnytherobot](https://github.com/vinnytherobot)