#!/usr/bin/env python3
"""
Web server wrapper for MCP servers on Render
Exposes MCP servers via HTTP/SSE endpoints
"""
import os
import logging
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import asyncio
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('WebServer')

app = FastAPI(title="MCP Server", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Available MCP servers
MCP_SERVERS = {
    "calculator": "calculator.py",
    "google_search": "google_search.py",
    "news_service": "news_service.py",
}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "MCP Server is running",
        "servers": list(MCP_SERVERS.keys())
    }

@app.get("/health")
async def health():
    """Health check for Render"""
    return {"status": "healthy"}

@app.post("/mcp/{server_name}")
async def mcp_endpoint(server_name: str, request: Request):
    """
    MCP endpoint - accepts JSON-RPC requests and returns responses
    """
    if server_name not in MCP_SERVERS:
        return JSONResponse(
            status_code=404,
            content={"error": f"Server '{server_name}' not found"}
        )
    
    try:
        # Get request body
        body = await request.json()
        logger.info(f"Request to {server_name}: {json.dumps(body)[:200]}")
        
        # Start MCP server process
        script_path = MCP_SERVERS[server_name]
        process = subprocess.Popen(
            ["python", script_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send request
        stdout, stderr = process.communicate(
            input=json.dumps(body) + "\n",
            timeout=30
        )
        
        if stderr:
            logger.warning(f"Server stderr: {stderr}")
        
        # Parse response
        response = json.loads(stdout.strip())
        return JSONResponse(content=response)
        
    except subprocess.TimeoutExpired:
        process.kill()
        return JSONResponse(
            status_code=408,
            content={"error": "Request timeout"}
        )
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Invalid JSON response from server"}
        )
    except Exception as e:
        logger.error(f"Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/servers")
async def list_servers():
    """List available MCP servers"""
    return {
        "servers": [
            {"name": name, "script": script}
            for name, script in MCP_SERVERS.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
