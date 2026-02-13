from agents.consultant_agent.agent import create_consultant_agent
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
import uuid

def test_multiplier():
    agent = create_consultant_agent()
    session_service = InMemorySessionService()
    runner = Runner(
        agent=agent,
        app_name="consultant-test-multiplier",
        session_service=session_service,
        auto_create_session=True
    )
    
    user_id = "test-user-scale-v2"
    session_id = str(uuid.uuid4())
    # Requesting 80% scale
    prompt = "Create a scalable Twitter clone with React, Go, and Cassandra. Please use 80% scale (compact layout)."
    
    print(f"Testing Consultant Agent with prompt: {prompt}")
    events = runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=types.Content(parts=[types.Part(text=prompt)])
    )
    
    result_text = ""
    for event in events:
         if event.content:
             for part in event.content.parts:
                 if part.text:
                     print(part.text)
                     result_text += part.text

if __name__ == "__main__":
    test_multiplier()
