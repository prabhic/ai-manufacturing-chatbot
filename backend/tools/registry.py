"""
Tool Registry — central place to register all tools.

Each tool module must expose:
  - DECLARATION: dict  (the function declaration for Gemini)
  - execute(**kwargs): callable  (the actual function to run)

To add a new tool:
  1. Create a new file in backend/tools/ (e.g., weather_tool.py)
  2. Import and add it to the TOOLS dict below.
"""

from backend.tools import time_tool

# Map tool name → tool module
# Each module has .DECLARATION and .execute()
TOOLS: dict = {
    "get_current_time": time_tool,
}


def get_declarations() -> list[dict]:
    """Return all tool declarations for Gemini."""
    return [tool.DECLARATION for tool in TOOLS.values()]


def execute_tool(name: str, args: dict) -> dict:
    """Look up and execute a tool by name."""
    if name not in TOOLS:
        raise ValueError(f"Unknown tool: {name}")
    return TOOLS[name].execute(**args)
