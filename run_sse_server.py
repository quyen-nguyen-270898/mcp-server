#!/usr/bin/env python3
"""
Run all MCP servers with SSE transport for Render deployment
SSE transport allows MCP clients to connect directly via Server-Sent Events
"""
import os
import sys
import asyncio
import logging
from importlib import import_module

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MCPServers')

# MCP servers to run
SERVERS = {
    "calculator": "calculator",
    "news_service": "news_service", 
    "google_search": "google_search",
}

async def run_server(name: str, module_name: str, port: int):
    """Run a single MCP server with SSE transport"""
    try:
        logger.info(f"Loading {name} from {module_name}...")
        module = import_module(module_name)
        mcp = module.mcp
        
        logger.info(f"Starting {name} on port {port} with SSE transport...")
        await mcp.run_async(
            transport="sse",
            host="0.0.0.0",
            port=port,
            show_banner=True
        )
    except Exception as e:
        logger.error(f"Failed to start {name}: {e}", exc_info=True)

async def main():
    """Start all MCP servers"""
    port = int(os.getenv("PORT", 8000))
    
    # For Render, we can only bind to one port
    # So we'll use the first server only, or you can modify to use FastAPI to route to multiple
    logger.info(f"Starting MCP servers on port {port}...")
    
    # Run calculator server (change this to the server you want)
    server_name = os.getenv("MCP_SERVER", "calculator")
    
    if server_name not in SERVERS:
        logger.error(f"Unknown server: {server_name}")
        sys.exit(1)
    
    await run_server(server_name, SERVERS[server_name], port)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
