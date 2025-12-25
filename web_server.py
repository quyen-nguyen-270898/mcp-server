#!/usr/bin/env python3
"""
Web server wrapper for FastMCP servers on Render
Runs MCP servers directly using FastMCP's SSE transport
"""
import os
import sys
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('WebServer')

app = FastAPI(title="MCP Server Hub", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import MCP servers directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize MCP servers
logger.info("Initializing MCP servers...")

try:
    from calculator import mcp as calculator_mcp
    logger.info("✓ Calculator MCP loaded")
except Exception as e:
    logger.error(f"✗ Failed to load calculator: {e}")
    calculator_mcp = None

try:
    from news_service import mcp as news_mcp
    logger.info("✓ News Service MCP loaded")
except Exception as e:
    logger.error(f"✗ Failed to load news_service: {e}")
    news_mcp = None

try:
    from google_search import mcp as search_mcp
    logger.info("✓ Google Search MCP loaded")
except Exception as e:
    logger.error(f"✗ Failed to load google_search: {e}")
    search_mcp = None

MCP_SERVERS = {
    "calculator": calculator_mcp,
    "news_service": news_mcp,
    "google_search": search_mcp,
}

@app.get("/")
async def root():
    """Health check endpoint"""
    available = [name for name, server in MCP_SERVERS.items() if server is not None]
    return {
        "status": "ok",
        "message": "MCP Server Hub is running",
        "servers": available,
        "total": len(available)
    }

@app.get("/health")
async def health():
    """Health check for Render"""
    return {"status": "healthy"}

@app.post("/mcp/{server_name}")
async def mcp_endpoint(server_name: str, request: Request):
    """
    MCP JSON-RPC endpoint
    Handles tools/list and tools/call requests
    """
    if server_name not in MCP_SERVERS:
        return JSONResponse(
            status_code=404,
            content={"error": f"Server '{server_name}' not found"}
        )
    
    mcp_server = MCP_SERVERS[server_name]
    if mcp_server is None:
        return JSONResponse(
            status_code=503,
            content={"error": f"Server '{server_name}' failed to initialize"}
        )
    
    try:
        body = await request.json()
        logger.info(f"Request to {server_name}: {body.get('method', 'unknown')}")
        
        method = body.get("method", "")
        params = body.get("params", {})
        request_id = body.get("id", 1)
        
        # Handle tools/list request
        if method == "tools/list":
            tools = []
            for tool in mcp_server.get_tools():
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                })
            
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"tools": tools}
            })
        
        # Handle tools/call request
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            tool = await mcp_server.get_tool(tool_name)
            if tool is None:
                return JSONResponse(
                    status_code=404,
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Tool '{tool_name}' not found"
                        }
                    }
                )
            
            # Call the tool function
            try:
                result = tool.fn(**arguments)
                return JSONResponse(content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": str(result)
                            }
                        ]
                    }
                })
            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": f"Tool execution failed: {str(e)}"
                        }
                    }
                )
        
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not supported"
                    }
                }
            )
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.get("/servers")
async def list_servers():
    """List available MCP servers and their tools"""
    servers_info = []
    for name, server in MCP_SERVERS.items():
        if server is None:
            servers_info.append({
                "name": name,
                "status": "failed",
                "tools": []
            })
        else:
            tools = [
                {
                    "name": tool.name,
                    "description": tool.description
                }
                for tool in server.get_tools()
            ]
            servers_info.append({
                "name": name,
                "status": "active",
                "tools": tools
            })
    
    return {"servers": servers_info}

@app.get("/mcp/{server_name}/tools")
async def list_tools(server_name: str):
    """List tools available in a specific MCP server"""
    if server_name not in MCP_SERVERS:
        return JSONResponse(
            status_code=404,
            content={"error": f"Server '{server_name}' not found"}
        )
    
    mcp_server = MCP_SERVERS[server_name]
    if mcp_server is None:
        return JSONResponse(
            status_code=503,
            content={"error": f"Server '{server_name}' not available"}
        )
    
    tools = []
    for tool in mcp_server.get_tools():
        tools.append({
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.inputSchema
        })
    
    return {"server": server_name, "tools": tools}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
