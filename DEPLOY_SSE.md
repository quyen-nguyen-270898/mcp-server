# Deploy MCP Server với SSE Transport

## 🎯 Cách Hoạt Động

### Local (hiện tại):
```
MCP Servers (stdio) 
    ↓
mcp_pipe.py (bridge stdio ← → WebSocket)
    ↓
WebSocket Endpoint (MCP_ENDPOINT)
    ↓
Client (Claude Desktop, etc.)
```

### Deploy trên Render (SSE Transport):
```
MCP Servers (SSE/HTTP transport) ← trực tiếp
    ↓
Client kết nối qua SSE endpoint
```

**FastMCP hỗ trợ 3 transports:**
- `stdio` - Standard input/output (cho local, cần mcp_pipe.py làm bridge)
- `sse` - Server-Sent Events (cho web deployment) ✅
- `http` - HTTP JSON-RPC (cũng cho web)

## ✅ Giải Pháp

Thay vì chạy `mcp_pipe.py` (cần WebSocket endpoint), ta chạy MCP servers **trực tiếp với SSE transport**:

**File:** `run_mcp_hub.py`
- Mount tất cả MCP servers với SSE transport
- Expose mỗi server tại `/sse/{server_name}`
- Client MCP kết nối trực tiếp qua SSE

## 🚀 Deploy Steps

### 1. Push code
```bash
git add run_mcp_hub.py render.yaml
git commit -m "Add SSE transport for Render deployment"
git push origin main
```

### 2. Deploy trên Render
- Tạo **Blueprint** từ GitHub repo
- Render auto-detect `render.yaml` 
- Start command: `python run_mcp_hub.py`

### 3. URL sau khi deploy
```
https://your-app.onrender.com/
https://your-app.onrender.com/sse/calculator      # Calculator SSE endpoint
https://your-app.onrender.com/sse/news_service    # News SSE endpoint
https://your-app.onrender.com/sse/google_search   # Search SSE endpoint
```

## 📱 Cấu Hình Client (Claude Desktop)

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "calculator": {
      "url": "https://your-app.onrender.com/sse/calculator",
      "transport": "sse"
    },
    "news_service": {
      "url": "https://your-app.onrender.com/sse/news_service",
      "transport": "sse"
    },
    "google_search": {
      "url": "https://your-app.onrender.com/sse/google_search",
      "transport": "sse"
    }
  }
}
```

**Restart Claude Desktop** sau khi cập nhật config.

## 🧪 Test Local

```bash
# Start server
python run_mcp_hub.py

# Check status
curl http://localhost:8000/

# SSE endpoints
curl http://localhost:8000/sse/calculator
curl http://localhost:8000/sse/news_service
curl http://localhost:8000/sse/google_search
```

## 🆚 So Sánh 2 Cách

| | web_server.py (HTTP wrapper) | run_mcp_hub.py (SSE native) |
|---|---|---|
| **Transport** | Custom HTTP JSON-RPC | FastMCP SSE built-in |
| **Client config** | `"transport": "http"` | `"transport": "sse"` |
| **Chuẩn MCP** | Custom implementation | Native MCP protocol |
| **Tương thích** | Tự code, có thể có bugs | FastMCP official, stable |
| **Recommended** | ❌ Không | ✅ **Khuyên dùng** |

## ⚠️ Lưu Ý

- **Free tier** Render sẽ spin down sau 15 phút không dùng
- Request đầu tiên mất 30-60 giây để wake up
- SSE là transport chuẩn của MCP, được các MCP clients hỗ trợ tốt
- Không cần `mcp_pipe.py` khi deploy (chỉ dùng cho local stdio transport)

## 📚 Files

- [run_mcp_hub.py](run_mcp_hub.py) - **Main server** - SSE transport (khuyên dùng)
- [run_sse_server.py](run_sse_server.py) - Single server runner (nếu chỉ cần 1 server)
- [web_server.py](web_server.py) - HTTP wrapper (cũ, không khuyên dùng)
- [render.yaml](render.yaml) - Render config
