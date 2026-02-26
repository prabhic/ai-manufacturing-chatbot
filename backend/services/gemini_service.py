"""
Gemini Service — handles all interaction with the Gemini API.

Responsibilities:
  - Maintain per-session conversation history
  - Send messages to Gemini with tool declarations
  - Handle tool call flow (detect → execute → return result)
"""

import uuid
from google import genai
from google.genai import types

from backend.config import settings
from backend.tools.registry import get_declarations, execute_tool


class GeminiService:
    """Manages Gemini API calls and conversation sessions."""

    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model = settings.GEMINI_MODEL

        # Tool configuration for Gemini
        self.config = types.GenerateContentConfig(
            tools=[types.Tool(function_declarations=get_declarations())]
        )

        # In-memory session store: session_id → list of Content messages
        self._sessions: dict[str, list] = {}

    def _get_history(self, session_id: str) -> list:
        """Get or create conversation history for a session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        return self._sessions[session_id]

    def chat(self, message: str, session_id: str | None = None) -> dict:
        """
        Send a user message and get Gemini's response.

        Args:
            message:    The user's text message.
            session_id: Optional session ID for conversation continuity.

        Returns:
            dict with keys: response, tool_used, session_id
        """
        # Create or reuse session
        if not session_id:
            session_id = str(uuid.uuid4())

        history = self._get_history(session_id)

        # Add user message to history
        history.append(
            types.Content(role="user", parts=[types.Part(text=message)])
        )

        # Call Gemini
        response = self.client.models.generate_content(
            model=self.model,
            contents=history,
            config=self.config,
        )

        # Check if model wants to call a tool
        first_part = response.candidates[0].content.parts[0]
        tool_used = None

        if first_part.function_call and first_part.function_call.name:
            # --- Tool call flow ---
            tool_name = first_part.function_call.name
            tool_args = dict(first_part.function_call.args) if first_part.function_call.args else {}
            tool_used = tool_name

            # Execute the tool locally
            tool_result = execute_tool(tool_name, tool_args)

            # Add model's tool-call turn to history
            history.append(response.candidates[0].content)

            # Add tool result as user turn (Gemini convention)
            function_response_part = types.Part.from_function_response(
                name=tool_name,
                response={"result": tool_result},
            )
            history.append(
                types.Content(role="user", parts=[function_response_part])
            )

            # Get final response from Gemini
            final_response = self.client.models.generate_content(
                model=self.model,
                contents=history,
                config=self.config,
            )
            assistant_text = final_response.text

            # Add final response to history
            history.append(
                types.Content(role="model", parts=[types.Part(text=assistant_text)])
            )
        else:
            # --- Direct response (no tool needed) ---
            assistant_text = response.text
            history.append(response.candidates[0].content)

        return {
            "response": assistant_text,
            "tool_used": tool_used,
            "session_id": session_id,
        }

    def clear_session(self, session_id: str) -> None:
        """Clear conversation history for a session."""
        self._sessions.pop(session_id, None)
