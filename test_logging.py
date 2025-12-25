#!/usr/bin/env python3
"""
Test MCP Server Logging
Simulates MCP client requests to verify server logging is working
"""

import json
import sys
import subprocess
import time

def test_mcp_tool(server_script: str, tool_name: str, arguments: dict):
    """
    Send a test request to MCP server and display logs
    
    Args:
        server_script: Path to MCP server script (e.g., 'calculator.py')
        tool_name: Name of the tool to call
        arguments: Dictionary of arguments for the tool
    """
    print(f"\n{'='*70}")
    print(f"Testing {server_script} - Tool: {tool_name}")
    print(f"{'='*70}\n")
    
    # Prepare the MCP request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    print(f"📤 Sending request:")
    print(json.dumps(request, indent=2, ensure_ascii=False))
    print()
    
    # Start the server process
    try:
        process = subprocess.Popen(
            ['python', server_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        # Send request
        request_str = json.dumps(request) + '\n'
        stdout, stderr = process.communicate(input=request_str, timeout=10)
        
        # Display server logs (from stderr)
        if stderr:
            print(f"📋 Server Logs:")
            print(stderr)
        
        # Display response (from stdout)
        if stdout:
            print(f"\n📥 Server Response:")
            # Parse and pretty-print JSON lines
            for line in stdout.strip().split('\n'):
                if line.strip():
                    try:
                        response_json = json.loads(line)
                        print(json.dumps(response_json, indent=2, ensure_ascii=False))
                    except json.JSONDecodeError:
                        print(line)
        
    except subprocess.TimeoutExpired:
        process.kill()
        print("⏱️ Request timed out")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n{'='*70}\n")

def main():
    """Run test scenarios"""
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║               MCP Server Logging Test Suite                       ║
║                                                                    ║
║  This script tests logging output from MCP servers                ║
║  Watch for detailed logs showing server activity                  ║
╚════════════════════════════════════════════════════════════════════╝
""")
    
    # Test 1: Calculator
    print("\n🧮 Test 1: Calculator Service")
    test_mcp_tool(
        'calculator.py',
        'calculator',
        {'python_expression': '2 + 2 * 10'}
    )
    
    time.sleep(1)
    
    # Test 2: Calculator with math
    print("\n🧮 Test 2: Calculator with Math Functions")
    test_mcp_tool(
        'calculator.py',
        'calculator',
        {'python_expression': 'math.sqrt(144) + math.pi'}
    )
    
    time.sleep(1)
    
    # Test 3: Google Search
    print("\n🔍 Test 3: Web Search Service")
    test_mcp_tool(
        'google_search.py',
        'search_google',
        {
            'query': 'Python programming',
            'num_results': 3,
            'lang': 'en'
        }
    )
    
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                     Tests Completed!                               ║
║                                                                    ║
║  You should see detailed logs above showing:                       ║
║  • Server startup messages                                         ║
║  • Request received notifications                                  ║
║  • Processing steps                                                ║
║  • Results and completion status                                   ║
║                                                                    ║
║  When running with mcp_pipe.py, these logs will appear in          ║
║  your terminal to help you debug and monitor server activity.      ║
╚════════════════════════════════════════════════════════════════════╝
""")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
