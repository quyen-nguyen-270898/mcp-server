#!/usr/bin/env python3
"""
Unified server runner - Runs all MCP servers on different ports
Or creates a FastAPI router to serve multiple servers on one port
"""
import os
import sys
import asyncio
import logging
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from importlib import import_module

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCPHub')

# Import all MCP servers
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logger.info("Loading MCP servers...")
from calculator import mcp as calculator_mcp
from news_service import mcp as news_mcp
from google_search import mcp as search_mcp

MCP_SERVERS = {
    "calculator": calculator_mcp,
    "news_service": news_mcp,
    "google_search": search_mcp,
}

# Create main FastAPI app
app = FastAPI(title="MCP Server Hub", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Status and available servers"""
    return {
        "status": "ok",
        "message": "MCP Server Hub - SSE Transport",
        "servers": list(MCP_SERVERS.keys()),
        "endpoints": {
            name: f"/sse/{name}" for name in MCP_SERVERS.keys()
        }
    }

@app.get("/health")
async def health():
    """Health check for Render"""
    return {"status": "healthy"}

# Mount each MCP server's SSE endpoint
for name, mcp_server in MCP_SERVERS.items():
    # Get the FastAPI app from the MCP server with SSE transport
    mcp_http_app = mcp_server.http_app(transport="sse")
    
    # Mount it under /sse/<server_name>
    app.mount(f"/sse/{name}", mcp_http_app)
    logger.info(f"✓ Mounted {name} at /sse/{name}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting MCP Hub on port {port}...")
    logger.info("Servers available:")
    for name in MCP_SERVERS.keys():
        logger.info(f"  - {name}: http://localhost:{port}/sse/{name}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
