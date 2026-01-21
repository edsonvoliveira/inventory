from datetime import datetime


def format_ts(value: str | None) -> str:
    if not value or value == "n/a":
        return "n/a"
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo:
            dt = dt.astimezone()
        return f"Data: {dt:%d/%m/%Y} - Hora: {dt:%H:%M}"
    except ValueError:
        return value
