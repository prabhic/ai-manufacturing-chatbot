"""
Time Tool — returns the current local date and time.
"""

from datetime import datetime


DECLARATION = {
    "name": "get_current_time",
    "description": (
        "Returns the current local date and time. "
        "Use this whenever the user asks about the current time or date."
    ),
    "parameters": {
        "type": "object",
        "properties": {},
        "required": [],
    },
}


def execute(**kwargs) -> dict:
    """Return current local time in multiple formats."""
    now = datetime.now().astimezone()
    return {
        "iso": now.isoformat(),
        "human": now.strftime("%A, %B %d, %Y %I:%M %p"),
        "timezone": now.tzname() or "Unknown",
    }
