# Hướng dẫn Deploy MCP Server lên Render

## Bước 1: Chuẩn bị

### 1.1 Cập nhật requirements.txt
Thêm các dependencies cho web server:

```bash
pip install fastapi uvicorn
```

Đảm bảo file `requirements.txt` có:
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
```

### 1.2 Commit code lên GitHub
```bash
git add .
git commit -m "Add Render deployment files"
git push origin main
```

## Bước 2: Tạo Web Service trên Render

### 2.1 Đăng ký/Đăng nhập Render
- Truy cập https://render.com
- Đăng ký hoặc đăng nhập (có thể dùng GitHub account)

### 2.2 Tạo Web Service mới

#### Cách 1: Sử dụng render.yaml (Recommended)
1. Click **"New"** → **"Blueprint"**
2. Connect GitHub repository của bạn
3. Render sẽ tự động phát hiện file `render.yaml`
4. Click **"Apply"** để deploy

#### Cách 2: Tạo thủ công
1. Click **"New"** → **"Web Service"**
2. Connect GitHub repository
3. Điền thông tin:
   - **Name**: `mcp-server` (hoặc tên bạn muốn)
   - **Region**: Singapore (hoặc gần bạn nhất)
   - **Branch**: `main`
   - **Root Directory**: để trống (hoặc thư mục chứa code)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python web_server.py`
4. Chọn **Free** plan
5. Click **"Create Web Service"**

## Bước 3: Cấu hình Environment Variables

Trong dashboard của Web Service, vào tab **"Environment"**:

1. Thêm biến môi trường cần thiết (nếu có):
   - `GOOGLE_API_KEY`: API key cho Google Search (nếu dùng)
   - `NEWS_API_KEY`: API key cho news (nếu cần)
   - Các biến khác theo nhu cầu

**Lưu ý**: 
- Biến `PORT` sẽ được Render tự động set, không cần thêm
- Biến `PYTHON_VERSION` để chọn phiên bản Python (mặc định 3.11)

## Bước 4: Deploy và Kiểm tra

### 4.1 Deploy
- Render sẽ tự động build và deploy
- Xem logs trong tab **"Logs"** để theo dõi quá trình
- Đợi đến khi status là **"Live"** (màu xanh)

### 4.2 Lấy URL
- URL của service sẽ có dạng: `https://mcp-server-xxxx.onrender.com`
- Copy URL này

### 4.3 Test endpoints

**Health check**:
```bash
curl https://mcp-server-xxxx.onrender.com/health
```

**List servers**:
```bash
curl https://mcp-server-xxxx.onrender.com/servers
```

**Test calculator**:
```bash
curl -X POST https://mcp-server-xxxx.onrender.com/mcp/calculator \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {}
  }'
```

**Test news service**:
```bash
curl -X POST https://mcp-server-xxxx.onrender.com/mcp/news_service \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_latest_news",
      "arguments": {
        "source": "vnexpress",
        "max_articles": 5
      }
    }
  }'
```

## Bước 5: Sử dụng trong Claude Desktop

Cập nhật file cấu hình MCP client (Claude Desktop config):

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "news_service": {
      "url": "https://mcp-server-xxxx.onrender.com/mcp/news_service",
      "transport": "http"
    },
    "calculator": {
      "url": "https://mcp-server-xxxx.onrender.com/mcp/calculator",
      "transport": "http"
    },
    "google_search": {
      "url": "https://mcp-server-xxxx.onrender.com/mcp/google_search",
      "transport": "http"
    }
  }
}
```

## Lưu ý quan trọng

### 1. Free Tier Limitations
- **Spin down**: Service sẽ tự động tắt sau 15 phút không hoạt động
- **Spin up**: Request đầu tiên sau khi tắt sẽ mất ~30-60 giây để khởi động lại
- **750 giờ/tháng**: Miễn phí (đủ cho 1 service chạy 24/7)

### 2. Keep Service Alive
Nếu không muốn service bị spin down, có thể:
- Nâng cấp lên Starter plan ($7/tháng)
- Hoặc dùng cron job để ping service mỗi 10 phút:

```bash
# Cron job trên máy local hoặc service khác
*/10 * * * * curl https://mcp-server-xxxx.onrender.com/health
```

### 3. Monitoring
- Xem logs realtime trong Render dashboard
- Set up alerts trong tab **"Settings"** → **"Notifications"**

### 4. Custom Domain (Optional)
- Tab **"Settings"** → **"Custom Domain"**
- Add domain của bạn và cấu hình DNS

## Troubleshooting

### Build failed
- Kiểm tra `requirements.txt` có đầy đủ dependencies
- Xem logs để biết package nào bị lỗi

### Service không start
- Kiểm tra logs xem có error gì
- Đảm bảo `web_server.py` đúng đường dẫn
- Kiểm tra Python version

### Timeout khi call API
- Free tier có thể chậm khi cold start
- Tăng timeout trong client lên 60-90 giây cho request đầu tiên

### 502 Bad Gateway
- Service đang khởi động (đợi 30-60 giây)
- Hoặc service bị crash (xem logs)

## Auto-deploy

Mỗi khi bạn push code mới lên GitHub:
1. Render tự động detect changes
2. Tự động build và deploy phiên bản mới
3. Không cần làm gì thêm!

Để tắt auto-deploy: **Settings** → **"Auto-Deploy"** → Tắt

## Các lệnh hữu ích

```bash
# Test local trước khi deploy
python web_server.py

# Test API local
curl http://localhost:8000/health

# View Render logs (cần Render CLI)
render logs -s mcp-server

# Redeploy manually
# Vào dashboard → click "Manual Deploy" → "Deploy latest commit"
```

## Tài liệu tham khảo
- Render Docs: https://render.com/docs
- Render Python Guide: https://render.com/docs/deploy-fastapi
- FastAPI Docs: https://fastapi.tiangolo.com
