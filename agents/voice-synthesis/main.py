"""
Main entrypoint for Voice Synthesis Agent deployment.
Serves the Google ADK agent as a FastAPI application.
"""

import os
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from agent import agent
from google.adk.runners import InMemoryRunner
from google.genai import types
import uvicorn

PORT = int(os.environ.get('PORT', 8080))
app = FastAPI(title=agent.name)

# Initialize runner
runner = InMemoryRunner(agent=agent)

@app.get("/")
async def root():
    return {"status": "healthy", "agent": agent.name, "model": agent.model, "tools": len(agent.tools)}

@app.post("/invoke")
async def invoke_agent(request: Request):
    """Invoke the agent with a prompt (stateless, no session history)"""
    try:
        body = await request.json()
        prompt = body.get("prompt", "")

        # Create Content object for ADK
        content = types.Content(role='user', parts=[types.Part(text=prompt)])

        # Generate unique user ID
        user_id = f"user_{uuid.uuid4().hex[:8]}"

        # Create session (synchronous call)
        session = runner.session_service.create_session(
            app_name=agent.name,
            user_id=user_id
        )

        # Invoke agent via runner with created session
        full_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session.id, new_message=content):
            if hasattr(event, 'content') and event.content:
                if hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            full_response += part.text

        return JSONResponse(content={"success": True, "response": full_response})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

if __name__ == "__main__":
    print(f"🚀 Starting {agent.name} on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
