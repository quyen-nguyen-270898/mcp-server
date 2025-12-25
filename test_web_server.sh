#!/bin/bash
# Script test nhanh web server trước khi deploy

echo "🚀 Starting web server..."
python web_server.py &
SERVER_PID=$!

# Đợi server khởi động
sleep 5

echo ""
echo "✅ Testing endpoints..."
echo ""

# Test 1: Health check
echo "1️⃣  Health check:"
curl -s http://localhost:8000/health | python -m json.tool
echo ""

# Test 2: List servers
echo "2️⃣  List servers:"
curl -s http://localhost:8000/ | python -m json.tool
echo ""

# Test 3: Calculator tool
echo "3️⃣  Test calculator (2+2*3):"
curl -s -X POST http://localhost:8000/mcp/calculator \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"calculator","arguments":{"python_expression":"2+2*3"}}}' \
  | python -m json.tool
echo ""

# Test 4: News service
echo "4️⃣  Test news service (2 articles):"
curl -s -X POST http://localhost:8000/mcp/news_service \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_latest_news","arguments":{"source":"vnexpress","max_results":2}}}' \
  | python -c "import sys, json; r=json.load(sys.stdin); print(json.dumps(r, indent=2, ensure_ascii=False))" | head -50
echo ""

echo "🛑 Stopping server..."
kill $SERVER_PID

echo ""
echo "✅ All tests completed!"
echo ""
echo "📝 Next steps:"
echo "   1. git push origin main"
echo "   2. Deploy to Render (see RENDER_DEPLOY_GUIDE.md)"
