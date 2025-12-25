# Giải Pháp Deploy MCP Server lên Render

## ❌ Vấn đề gặp phải

MCP servers của bạn sử dụng **FastMCP** với `transport="stdio"` - nghĩa là chúng giao tiếp qua standard input/output, không phải HTTP. Khi deploy lên web hosting như Render, bạn cần một web server wrapper.

## ✅ Giải pháp

Đã tạo [web_server.py](web_server.py) - một FastAPI wrapper để:
1. Import trực tiếp các MCP servers (calculator, news_service, google_search)
2. Expose chúng qua HTTP JSON-RPC endpoints
3. Sử dụng FastMCP API đúng cách với `async get_tool()` và `get_tools()`

## 🔑 Điểm quan trọng

FastMCP API:
- `get_tool(name)` và `get_tools()` là **async functions** - cần `await`
- Tools được lưu nội bộ, truy cập qua methods public chứ không phải `_tools` attribute

## 🧪 Test Local

```bash
# Cách 1: Chạy script test tự động
./test_web_server.sh

# Cách 2: Test thủ công
python web_server.py &

# Health check
curl http://localhost:8000/health

# Test calculator
curl -X POST http://localhost:8000/mcp/calculator \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"calculator","arguments":{"python_expression":"2+2*3"}}}'

# Test news
curl -X POST http://localhost:8000/mcp/news_service \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_latest_news","arguments":{"source":"vnexpress","max_results":2}}}'
```

## 🚀 Deploy lên Render

Xem hướng dẫn chi tiết trong [RENDER_DEPLOY_GUIDE.md](RENDER_DEPLOY_GUIDE.md)

**TL;DR:**
1. Push code lên GitHub: `git push origin main`
2. Tạo Blueprint trên Render.com từ repo
3. Render tự động detect [render.yaml](render.yaml) và deploy

## 📚 Tài liệu

- [render.yaml](render.yaml) - Cấu hình Render
- [RENDER_DEPLOY_GUIDE.md](RENDER_DEPLOY_GUIDE.md) - Hướng dẫn chi tiết tiếng Việt
- [web_server.py](web_server.py) - FastAPI wrapper cho MCP servers
- [test_web_server.sh](test_web_server.sh) - Script test local

## 🌐 Endpoints sau khi deploy

```
https://your-app.onrender.com/                    # Status & list servers
https://your-app.onrender.com/health              # Health check
https://your-app.onrender.com/servers             # Detailed server info
https://your-app.onrender.com/mcp/{server_name}   # JSON-RPC endpoint
```

## ⚠️ Lưu ý

- **Free tier** của Render sẽ spin down sau 15 phút không dùng
- Request đầu tiên có thể mất 30-60 giây để khởi động lại
- Nâng cấp lên Starter plan ($7/tháng) để tránh spin down
