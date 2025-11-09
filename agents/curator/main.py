"""
Main entrypoint for Tour Curator Agent deployment.
Serves the Google ADK agent as a FastAPI application.
"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from agent import agent
import uvicorn

# Get port from environment
PORT = int(os.environ.get('PORT', 8080))

# Create FastAPI app wrapper
app = FastAPI(title=agent.name)

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
    """Invoke the agent with a prompt (stateless, no session history)"""
    try:
        body = await request.json()
        prompt = body.get("prompt", "")

        # For stateless single-shot requests, invoke agent directly
        # No session management needed for one-off requests
        response = await agent.run_async(prompt)

        # Extract text from response
        full_response = str(response)

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
