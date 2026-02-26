"""
===========================================================================
  GEMINI TOOL/FUNCTION CALLING — Educational Interactive Chat Example
===========================================================================

CONCEPT: What is Tool/Function Calling?
----------------------------------------
Large Language Models (LLMs) like Gemini are great at generating text, but they
can't do things like check your clock, query a database, or call an API.

"Tool calling" (also called "function calling") bridges that gap:
  1. You TELL the model what tools/functions are available (name, description, params).
  2. The model DECIDES when a tool is needed based on the user's message.
  3. The model REQUESTS a tool call (it does NOT execute it — you do!).
  4. YOUR CODE executes the function locally and sends the result back.
  5. The model uses that result to craft a final human-friendly response.

The model never runs code itself — it just says "I need this function called
with these arguments." Your application is the one that actually runs the function.

HIGH-LEVEL FLOW:
-----------------
  User sends message
       ↓
  Gemini analyzes message + available tools
       ↓
  Does the model want to call a tool?
    ├── NO  → Gemini replies directly with text
    └── YES → Gemini returns a function_call request
                  ↓
              Your code executes the function locally
                  ↓
              Send the function result back to Gemini
                  ↓
              Gemini crafts a final response using the result
                  ↓
              Display the response to the user

SETUP INSTRUCTIONS:
-------------------
  1. Install the Google GenAI SDK:
       pip install google-genai

  2. Get a free API key from: https://aistudio.google.com/apikey

  3. Set your API key as an environment variable:
       export GEMINI_API_KEY="your-api-key-here"

  4. Run this script:
       python gemini_chat_tool_calling.py

  5. Try typing: "What time is it?"
     Watch the tool-calling flow in action!

  6. Type /exit to quit.
"""

import os
import sys
import json
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Step 0: Import the Google GenAI SDK
# ---------------------------------------------------------------------------
# We use the official "google-genai" package (not the older google-generativeai).
# - `genai` is the main client module
# - `types` provides typed config objects for tools, content, etc.
from google import genai
from google.genai import types


# ---------------------------------------------------------------------------
# Step 1: Define the local tool function
# ---------------------------------------------------------------------------
# This is a real Python function that runs on YOUR machine.
# The model will NEVER execute this — it only requests that we call it.

def get_current_time() -> dict:
    """
    Returns the current local time in three formats:
      - iso:      ISO 8601 format  (e.g. "2026-02-18T14:30:00+05:30")
      - human:    Human-readable   (e.g. "Tuesday, February 18, 2026 02:30 PM")
      - timezone: Timezone name    (e.g. "IST" or "UTC")
    """
    now = datetime.now().astimezone()  # current time with local timezone info

    return {
        "iso": now.isoformat(),
        "human": now.strftime("%A, %B %d, %Y %I:%M %p"),
        "timezone": now.tzname() or "Unknown",
    }


# ---------------------------------------------------------------------------
# Step 2: Create the tool declaration for Gemini
# ---------------------------------------------------------------------------
# This is a JSON-like description that tells the model:
#   - What the function is called
#   - What it does (description)
#   - What parameters it expects (none, in this case)
#
# IMPORTANT: This declaration does NOT contain the actual code.
# It's just metadata so the model knows the tool exists and when to use it.

get_current_time_declaration = {
    "name": "get_current_time",
    "description": (
        "Returns the current local date and time. "
        "Use this whenever the user asks about the current time or date."
    ),
    "parameters": {
        "type": "object",
        "properties": {},       # No input parameters needed
        "required": [],         # Nothing is required
    },
}


# ---------------------------------------------------------------------------
# Step 3: Map tool names to actual Python functions
# ---------------------------------------------------------------------------
# When the model says "call get_current_time", we look up the real function here.
# For a single tool this is simple; with many tools this dict scales nicely.

TOOL_FUNCTIONS = {
    "get_current_time": get_current_time,
}


# ---------------------------------------------------------------------------
# Step 4: Handle a tool call from the model
# ---------------------------------------------------------------------------
# This function:
#   a) Prints that the model requested a tool (educational output)
#   b) Looks up and executes the real Python function
#   c) Prints the result (educational output)
#   d) Sends the result back to Gemini and returns the final response

def handle_tool_call(client, model_name, config, conversation_history, response):
    """
    Process a tool/function call requested by Gemini.

    Args:
        client:               The GenAI client instance.
        model_name:           The model being used (e.g. "gemini-2.0-flash").
        config:               The GenerateContentConfig with tool declarations.
        conversation_history: The list of conversation messages so far.
        response:             The model's response that contains the function call.

    Returns:
        The final text response from Gemini after receiving the tool result.
    """

    # --- Extract the function call from the model's response ---
    # The model tells us WHICH function to call and with WHAT arguments.
    function_call = response.candidates[0].content.parts[0].function_call
    tool_name = function_call.name
    tool_args = dict(function_call.args) if function_call.args else {}

    # --- Educational output: show what the model requested ---
    print(f"\n  🔧 Gemini requested tool: {tool_name}")
    if tool_args:
        print(f"     Arguments: {json.dumps(tool_args, indent=2)}")
    print("     Executing tool locally...")

    # --- Execute the actual Python function ---
    tool_function = TOOL_FUNCTIONS[tool_name]
    tool_result = tool_function(**tool_args)

    # --- Educational output: show what the tool returned ---
    print(f"     Tool result: {json.dumps(tool_result, indent=2)}")

    # --- Append the model's response (with the function call) to history ---
    # This preserves the conversation context so Gemini knows what happened.
    conversation_history.append(response.candidates[0].content)

    # --- Build a function response part ---
    # This is how we send the tool's output back to Gemini.
    # We wrap it in a special Part that Gemini recognizes as a function result.
    function_response_part = types.Part.from_function_response(
        name=tool_name,
        response={"result": tool_result},
    )

    # --- Append the function result as a "user" turn ---
    # Gemini expects function results to come from the user role.
    conversation_history.append(
        types.Content(role="user", parts=[function_response_part])
    )

    # --- Send everything back to Gemini for the final answer ---
    # Now Gemini has: original question + its own tool request + the tool's result.
    # It uses all of this to generate a helpful, human-readable response.
    final_response = client.models.generate_content(
        model=model_name,
        contents=conversation_history,
        config=config,
    )

    return final_response


# ---------------------------------------------------------------------------
# Step 5: The main interactive chat loop
# ---------------------------------------------------------------------------

def main():
    """
    Main entry point. Sets up the Gemini client and runs the chat loop.
    """

    # --- Check for API key ---
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable is not set.")
        print("   Get a free key at: https://aistudio.google.com/apikey")
        print('   Then run: export GEMINI_API_KEY="your-key-here"')
        sys.exit(1)

    # --- Initialize the Gemini client ---
    client = genai.Client(api_key=api_key)

    # --- Choose a model ---
    # "gemini-2.0-flash" is fast and supports function calling.
    model_name = "gemini-2.0-flash"

    # --- Configure tools ---
    # We wrap our function declaration in a Tool object and pass it to the config.
    # This tells Gemini: "Hey, this tool is available if you need it."
    tools = types.Tool(function_declarations=[get_current_time_declaration])
    config = types.GenerateContentConfig(tools=[tools])

    # --- Conversation history ---
    # We keep a simple list of messages. This gives Gemini memory of the
    # conversation so it can refer back to earlier messages.
    conversation_history = []

    # --- Welcome message ---
    print("=" * 60)
    print("  Gemini Chat with Tool Calling — Educational Demo")
    print("=" * 60)
    print(f"  Model: {model_name}")
    print("  Available tools: get_current_time")
    print('  Type /exit to quit.')
    print()
    print("  Try asking: \"What time is it?\"")
    print("=" * 60)
    print()

    # --- Interactive loop ---
    while True:
        # Get user input
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        # Check for exit command
        if user_input.lower() == "/exit":
            print("Goodbye!")
            break

        # Skip empty input
        if not user_input:
            continue

        # --- Add the user's message to conversation history ---
        conversation_history.append(
            types.Content(
                role="user",
                parts=[types.Part(text=user_input)],
            )
        )

        # --- Send the conversation to Gemini ---
        # Gemini sees: all previous messages + tool declarations.
        # It decides whether to reply directly OR request a tool call.
        response = client.models.generate_content(
            model=model_name,
            contents=conversation_history,
            config=config,
        )

        # --- Check: did the model request a tool call? ---
        # We look at the first part of the response. If it has a function_call
        # attribute with a name, the model wants us to execute a tool.
        first_part = response.candidates[0].content.parts[0]
        if first_part.function_call and first_part.function_call.name:
            # ----------------------------------------------------------
            # PATH A: Tool call requested
            # ----------------------------------------------------------
            # The model didn't answer directly — it needs data from our tool.
            # We execute the tool, send the result back, and get the final reply.
            final_response = handle_tool_call(
                client, model_name, config, conversation_history, response
            )

            # Extract and display the final text
            assistant_text = final_response.text
            print(f"\nGemini: {assistant_text}\n")

            # Save the assistant's final response in conversation history
            conversation_history.append(
                types.Content(
                    role="model",
                    parts=[types.Part(text=assistant_text)],
                )
            )

        else:
            # ----------------------------------------------------------
            # PATH B: Direct text response (no tool needed)
            # ----------------------------------------------------------
            # The model answered directly without needing any tool.
            assistant_text = response.text
            print(f"\nGemini: {assistant_text}\n")

            # Save the model's response in conversation history
            conversation_history.append(response.candidates[0].content)


# ---------------------------------------------------------------------------
# Run the application
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()
