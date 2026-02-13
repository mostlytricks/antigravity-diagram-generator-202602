import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents.consultant_agent.agent import create_consultant_agent
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import uuid
import os
from dotenv import load_dotenv

# Load env
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

app = FastAPI(title="Diagram Agent System")

# Initialize Agents
consultant_agent = create_consultant_agent()
session_service = InMemorySessionService()
runner = Runner(
    agent=consultant_agent,
    app_name="consultant-agent-app",
    session_service=session_service,
    auto_create_session=True
)

class PromptRequest(BaseModel):
    prompt: str
    user_id: str = "default_user"
    session_id: str = None

@app.post("/generate")
async def generate_diagram(request: PromptRequest):
    session_id = request.session_id or str(uuid.uuid4())
    print(f"Received request: {request.prompt} (Session: {session_id})")
    
    try:
        events = runner.run(
            user_id=request.user_id,
            session_id=session_id,
            new_message=types.Content(parts=[types.Part(text=request.prompt)])
        )
        
        # Collect response
        response_text = ""
        for event in events:
             if event.content:
                 for part in event.content.parts:
                     if part.text:
                         response_text += part.text + "\n"
        
        return {"status": "success", "response": response_text.strip(), "session_id": session_id}
    except Exception as e:
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("app.server:app", host="127.0.0.1", port=8000, reload=True)
