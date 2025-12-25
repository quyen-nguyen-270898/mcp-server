#!/usr/bin/env python3
"""
Simple demo to show logging output
Run this to see what logs look like when MCP services run
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("""
╔════════════════════════════════════════════════════════════════════╗
║           MCP Server Logging Demo                                 ║
║                                                                    ║
║  This demo shows the logging output you'll see when running       ║
║  'python mcp_pipe.py' with your MCP client                        ║
╚════════════════════════════════════════════════════════════════════╝

📝 Importing calculator service...
""")

# Import calculator (this will show startup logs)
import calculator

print("""
✅ Calculator service loaded!

📝 Importing google_search service...
""")

# Import google search (this will show startup logs)
import google_search

print("""
✅ Google Search service loaded!

╔════════════════════════════════════════════════════════════════════╗
║                    Startup Logs Shown Above                        ║
║                                                                    ║
║  When you run 'python mcp_pipe.py', you'll see similar logs       ║
║  for each service that starts up.                                 ║
║                                                                    ║
║  Then, when your ESP32 client makes requests through DeepSeek,    ║
║  you'll see request logs like:                                     ║
║                                                                    ║
║  🔍 NEW SEARCH REQUEST RECEIVED                                    ║
║  Query: 'your search term'                                         ║
║  ⏳ Starting web search...                                         ║
║  ✅ Search completed successfully!                                 ║
║  Found 5 results                                                   ║
║                                                                    ║
║  OR for calculator:                                                ║
║                                                                    ║
║  🧮 CALCULATOR REQUEST RECEIVED                                    ║
║  Expression: 2 + 2 * 10                                            ║
║  ✅ Calculation successful!                                        ║
║  Result: 22                                                        ║
╚════════════════════════════════════════════════════════════════════╝

💡 Tips:
   - All logs go to stderr so they don't interfere with MCP protocol
   - Each request has clear separators (===) for easy reading
   - Emojis help you quickly identify log types
   - Timestamps show exact timing of events

🚀 Now you can run:
   python mcp_pipe.py

   And watch these logs in real-time as your ESP32 makes requests!
""")
