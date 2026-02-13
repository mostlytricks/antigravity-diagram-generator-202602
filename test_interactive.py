from agents.consultant_agent.agent import create_consultant_agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
import uuid
import time

def run_interactive_session():
    # 1. Setup Session Service (The "Memory")
    session_service = InMemorySessionService()
    
    agent = create_consultant_agent()
    runner = Runner(
        agent=agent,
        app_name="interactive-test",
        session_service=session_service,
        auto_create_session=True
    )
    
    # CRITICAL: Generate Session ID ONCE and reuse it
    user_id = "interactive-user"
    session_id = str(uuid.uuid4())
    print(f"--- Starting Interactive Session (ID: {session_id}) ---")

    # Turn 1: User Request
    prompt_1 = "I want a simple E-commerce system."
    print(f"\nUser: {prompt_1}")
    events_1 = runner.run(
        user_id=user_id,
        session_id=session_id, # Reuse ID
        new_message=types.Content(parts=[types.Part(text=prompt_1)])
    )
    print("Agent:", end=" ")
    for e in events_1:
        if e.content: print(e.content.parts[0].text)

    # Turn 2: User Feedback
    prompt_2 = "Actually, I don't want a database. Just use a file system."
    print(f"\nUser: {prompt_2}")
    events_2 = runner.run(
        user_id=user_id,
        session_id=session_id, # Reuse ID
        new_message=types.Content(parts=[types.Part(text=prompt_2)])
    )
    print("Agent:", end=" ")
    for e in events_2:
        if e.content: print(e.content.parts[0].text)

    # Turn 3: Confirmation
    prompt_3 = "Yes, that looks good. Go ahead."
    print(f"\nUser: {prompt_3}")
    events_3 = runner.run(
        user_id=user_id,
        session_id=session_id, # Reuse ID
        new_message=types.Content(parts=[types.Part(text=prompt_3)])
    )
    print("Agent:", end=" ")
    for e in events_3:
        if e.content: print(e.content.parts[0].text)

if __name__ == "__main__":
    run_interactive_session()
