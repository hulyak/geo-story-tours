"""
Main entrypoint for Storytelling Agent deployment.
Serves the Google ADK agent as a FastAPI application.
"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from adk_agent import agent
import uvicorn
from google.adk.messages import UserMessage

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

        # Create a UserMessage as required by ADK
        messages = [UserMessage(content=prompt)]

        # Invoke the agent - it returns an async generator
        full_response = ""
        async for event in agent.run_async(messages):
            if hasattr(event, 'text'):
                full_response += event.text
            elif hasattr(event, 'content'):
                if isinstance(event.content, str):
                    full_response += event.content
                elif hasattr(event.content, 'text'):
                    full_response += event.content.text
                elif hasattr(event.content, 'parts') and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text'):
                            full_response += part.text
            else:
                full_response += str(event)

        return JSONResponse(content={"success": True, "response": full_response})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

if __name__ == "__main__":
    print(f"🚀 Starting {agent.name} on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
