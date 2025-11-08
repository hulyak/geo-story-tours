"""
Main entrypoint for Storytelling Agent deployment.
Serves the Google ADK agent as a FastAPI application.
"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from adk_agent import agent
import uvicorn

PORT = int(os.environ.get('PORT', 8080))
app = FastAPI(title=agent.name)

@app.get("/")
async def root():
    return {"status": "healthy", "agent": agent.name, "model": agent.model, "tools": len(agent.tools)}

@app.post("/invoke")
async def invoke_agent(request: Request):
    try:
        body = await request.json()
        prompt = body.get("prompt", "")

        # Invoke the agent directly (stateless) - pass prompt as positional arg
        response = await agent.run_async(prompt)

        # Extract the text response
        full_response = ""
        if response and hasattr(response, 'text'):
            full_response = response.text
        elif response and hasattr(response, 'content'):
            if response.content and response.content.parts:
                full_response = response.content.parts[0].text
        else:
            full_response = str(response)

        return JSONResponse(content={"success": True, "response": full_response})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

if __name__ == "__main__":
    print(f"🚀 Starting {agent.name} on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
