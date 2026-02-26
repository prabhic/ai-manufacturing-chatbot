"""
GEMINI FUNCTION CALLING — Simplest Possible Example
=====================================================

This is the most minimal example to understand how function calling works.
No chat loop, no conversation history — just ONE request-response cycle
that clearly shows the 4-step flow:

  Step 1: Define a tool (tell the model what's available)
  Step 2: Send a prompt (the model decides to call the tool)
  Step 3: Execute the tool locally (YOU run it, not the model)
  Step 4: Send the result back (the model writes a human-friendly reply)

Run:
  pip install google-genai
  export GEMINI_API_KEY="your-key"
  python gemini_chat_tool_calling_simple.py
"""

import os
import sys
from datetime import datetime
from google import genai
from google.genai import types

# ── Step 1: Define a local Python function ──────────────────────────────
# This function runs on YOUR computer. The model never executes it.

def get_current_time() -> dict:
    """Return the current local time."""
    now = datetime.now().astimezone()
    return {
        "iso": now.isoformat(),
        "human": now.strftime("%A, %B %d, %Y %I:%M %p"),
        "timezone": now.tzname() or "Unknown",
    }


# ── Step 2: Describe the tool for Gemini ────────────────────────────────
# This is just a description (metadata). It tells the model:
#   "A tool called get_current_time exists. It returns the current time."
# The model uses this to decide WHEN to call it.

tool_declaration = {
    "name": "get_current_time",
    "description": "Returns the current local date and time.",
    "parameters": {"type": "object", "properties": {}},
}


# ── Main Program ────────────────────────────────────────────────────────

def main():
    # Check API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Set GEMINI_API_KEY first:  export GEMINI_API_KEY='your-key'")
        sys.exit(1)

    # Create client and config
    client = genai.Client(api_key=api_key)
    model = "gemini-3-flash-preview"
    config = types.GenerateContentConfig(
        tools=[types.Tool(function_declarations=[tool_declaration])]
    )

    # ── Step 3: Send a prompt ───────────────────────────────────────────
    # We ask something that requires knowing the time.
    # Gemini will realize it needs the tool and REQUEST a function call.
    user_message = "What time is it right now?"
    print(f"You: {user_message}")

    response = client.models.generate_content(
        model=model,
        contents=[user_message],
        config=config,
    )

    # ── Step 4: Check if Gemini requested a tool call ───────────────────
    part = response.candidates[0].content.parts[0]

    if not (part.function_call and part.function_call.name):
        # No tool call — model replied directly (unlikely for this prompt)
        print(f"Gemini: {response.text}")
        return

    # The model said: "I need get_current_time to answer this."
    print(f"\n→ Gemini requested tool: {part.function_call.name}")

    # ── Step 5: Execute the tool locally ────────────────────────────────
    # WE run the function. The model only asked for it.
    result = get_current_time()
    print(f"→ Tool result: {result}")

    # ── Step 6: Send the result back to Gemini ──────────────────────────
    # We build the conversation so far:
    #   Turn 1 (user):  "What time is it?"
    #   Turn 2 (model): function_call request
    #   Turn 3 (user):  function result
    # Then Gemini uses the result to write a final answer.

    final_response = client.models.generate_content(
        model=model,
        contents=[
            types.Content(role="user", parts=[types.Part(text=user_message)]),
            response.candidates[0].content,  # model's function_call turn
            types.Content(role="user", parts=[
                types.Part.from_function_response(
                    name="get_current_time",
                    response={"result": result},
                )
            ]),
        ],
        config=config,
    )

    print(f"\nGemini: {final_response.text}")


if __name__ == "__main__":
    main()
