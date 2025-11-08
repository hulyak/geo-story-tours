"""
Main entrypoint for Tour Curator Agent deployment.
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

# Get port from environment
PORT = int(os.environ.get('PORT', 8080))

# Create FastAPI app wrapper
app = FastAPI(title=agent.name)

# Create ADK runner for agent
runner = InMemoryRunner(agent=agent)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent": agent.name,
        "model": agent.model,
        "tools": len(agent.tools)
    }

@app.post("/invoke")
async def invoke_agent(request: Request):
    """Invoke the agent with a prompt"""
    try:
        body = await request.json()
        prompt = body.get("prompt", "")

        # Create user content in ADK format
        content = types.Content(role='user', parts=[types.Part(text=prompt)])

        # Generate unique session IDs
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())

        # Invoke the agent using the runner
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

        return JSONResponse(content={
            "success": True,
            "response": full_response
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )

if __name__ == "__main__":
    print(f"🚀 Starting {agent.name} on port {PORT}")
    print(f"📦 Model: {agent.model}")
    print(f"🔧 Tools: {len(agent.tools)}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT,
        log_level="info"
    )
