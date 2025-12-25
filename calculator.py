# server.py
from fastmcp import FastMCP
import sys
import logging

# Configure logging with detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('Calculator')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

logger.info('='*60)
logger.info('Calculator MCP Service Starting...')
logger.info('='*60)

import math
import random

# Create an MCP server
mcp = FastMCP("Calculator")

# Add an addition tool
@mcp.tool()
def calculator(python_expression: str) -> dict:
    """For mathamatical calculation, always use this tool to calculate the result of a python expression. You can use 'math' or 'random' directly, without 'import'."""
    logger.info('='*60)
    logger.info(f"🧮 CALCULATOR REQUEST RECEIVED")
    logger.info(f"Expression: {python_expression}")
    
    try:
        result = eval(python_expression, {"math": math, "random": random})
        logger.info(f"✅ Calculation successful!")
        logger.info(f"Result: {result}")
        logger.info('='*60)
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"❌ CALCULATION FAILED")
        logger.error(f"Expression: {python_expression}")
        logger.error(f"Error: {str(e)}")
        logger.error('='*60)
        return {"success": False, "error": str(e)}

# Start the server
if __name__ == "__main__":
    logger.info("🚀 Starting MCP server with stdio transport...")
    logger.info("📡 Server is ready to receive requests from MCP clients")
    logger.info("💡 Available tools: calculator")
    logger.info("Waiting for requests...\n")
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"\n❌ Server error: {e}")
        raise
