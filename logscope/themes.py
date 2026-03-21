# Default themes and mappings for LogScope

DEFAULT_THEMES = {
    "default": {
        "levels": {
            "TRACE": ("🔍", "dim white"),
            "DEBUG": ("🐛", "bold blue"),
            "INFO": ("🔵", "bold green"),
            "NOTICE": ("🔔", "bold cyan"),
            "WARN": ("🟡", "bold yellow"),
            "ERROR": ("🔴", "bold red"),
            "CRITICAL": ("💥", "bold magenta"),
            "ALERT": ("🚨", "bold color(208)"),
            "FATAL": ("💀", "bold dark_red"),
            "UNKNOWN": ("⚪", "dim white")
        },
        "highlights": {
            "logscope.ip": "bold green",
            "logscope.url": "underline blue",
            "logscope.timestamp": "cyan",
            "logscope.uuid": "bold magenta",
            "logscope.email": "underline yellow",
            "logscope.path": "dim blue",
            "logscope.status_ok": "bold green",
            "logscope.status_warn": "bold yellow",
            "logscope.status_err": "bold red",
            "logscope.method": "bold cyan"
        }
    },
    "neon": {
        "levels": {
            "TRACE": ("·", "magenta"),
            "DEBUG": ("⚡", "bold magenta"),
            "INFO": ("✨", "bold pink1"),
            "NOTICE": ("🌌", "bold purple"),
            "WARN": ("🔥", "bold yellow1"),
            "ERROR": ("🧨", "bold red1"),
            "CRITICAL": ("☢️ ", "bold purple"),
            "ALERT": ("📣", "bold orange1"),
            "FATAL": ("☣️ ", "bold dark_red"),
            "UNKNOWN": ("?", "dim white")
        },
        "highlights": {
            "logscope.ip": "bold pink1",
            "logscope.url": "italic underline magenta",
            "logscope.timestamp": "bold purple",
            "logscope.uuid": "bold yellow",
            "logscope.email": "bold pink1",
            "logscope.path": "italic magenta",
            "logscope.status_ok": "bold pink1",
            "logscope.status_warn": "bold yellow",
            "logscope.status_err": "bold red",
            "logscope.method": "bold cyan"
        }
    },
    "ocean": {
        "levels": {
             "TRACE": ("⚓", "dim cyan"),
             "DEBUG": ("🌊", "blue"),
             "INFO": ("💧", "bold blue"),
             "NOTICE": ("🐳", "cyan"),
             "WARN": ("🐚", "yellow"),
             "ERROR": ("🌋", "red"),
             "CRITICAL": ("⛈️ ", "bold blue"),
             "ALERT": ("🚩", "bold orange1"),
             "FATAL": ("🌪️ ", "bold red"),
             "UNKNOWN": ("?", "dim cyan")
        },
        "highlights": {
            "logscope.ip": "bold cyan",
            "logscope.url": "underline deep_sky_blue1",
            "logscope.timestamp": "blue",
            "logscope.uuid": "bold deep_sky_blue3",
            "logscope.email": "underline cyan",
            "logscope.path": "dim cyan",
            "logscope.status_ok": "bold green",
            "logscope.status_warn": "bold yellow",
            "logscope.status_err": "bold red",
            "logscope.method": "bold cyan"
        }
    },
    "forest": {
        "levels": {
            "TRACE": ("🍃", "dim green"),
            "DEBUG": ("🌿", "green"),
            "INFO": ("🌳", "bold green"),
            "NOTICE": ("🍄", "magenta"),
            "WARN": ("🍂", "yellow"),
            "ERROR": ("🪵", "red"),
            "CRITICAL": ("🌲", "bold white"),
            "ALERT": ("🐺", "bold orange1"),
            "FATAL": ("💀", "bold dark_red"),
            "UNKNOWN": ("?", "dim green")
        },
        "highlights": {
            "logscope.ip": "bold green3",
            "logscope.url": "underline dark_green",
            "logscope.timestamp": "yellow4",
            "logscope.uuid": "bold orange4",
            "logscope.email": "underline green",
            "logscope.path": "dim green3",
            "logscope.status_ok": "bold green",
            "logscope.status_warn": "bold yellow",
            "logscope.status_err": "bold red",
            "logscope.method": "bold green1"
        }
    },
    "minimal": {
        "levels": {
            "TRACE": (" ", "dim"),
            "DEBUG": (" ", "dim"),
            "INFO": (" ", "white"),
            "NOTICE": ("!", "cyan"),
            "WARN": ("?", "yellow"),
            "ERROR": ("#", "red"),
            "CRITICAL": ("*", "bold red"),
            "ALERT": ("!", "bold yellow"),
            "FATAL": ("X", "bold red"),
            "UNKNOWN": ("?", "dim")
        },
        "highlights": {
            "logscope.ip": "bold",
            "logscope.url": "underline",
            "logscope.timestamp": "dim",
            "logscope.uuid": "dim",
            "logscope.email": "underline",
            "logscope.path": "italic",
            "logscope.status_ok": "green",
            "logscope.status_warn": "yellow",
            "logscope.status_err": "red",
            "logscope.method": "bold"
        }
    }
}
