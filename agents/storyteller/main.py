"""
Main entrypoint for Storytelling Agent deployment.
Serves the Google ADK agent as a FastAPI application.
"""

import os
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from adk_agent import agent
from google.adk.runners import InMemoryRunner
from google.genai import types
import uvicorn

PORT = int(os.environ.get('PORT', 8080))
app = FastAPI(title=agent.name)

# Runner will be created per request to avoid session conflicts

@app.get("/")
async def root():
    return {"status": "healthy", "agent": agent.name, "model": agent.model, "tools": len(agent.tools)}

@app.post("/invoke")
async def invoke_agent(request: Request):
    try:
        body = await request.json()
        prompt = body.get("prompt", "")

        # Create unique user ID and session ID for this request
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        session_id = f"session_{uuid.uuid4().hex[:8]}"

        # Create message content
        content = types.Content(role='user', parts=[types.Part(text=prompt)])

        # Create a fresh runner for each request to avoid session conflicts
        runner = InMemoryRunner(agent=agent)

        # Use runner to invoke agent with explicit session_id
        full_response = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    full_response = event.content.parts[0].text
                    break

        return JSONResponse(content={"success": True, "response": full_response})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

if __name__ == "__main__":
    print(f"🚀 Starting {agent.name} on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
