# Web Search Service - Hướng Dẫn Sử Dụng

## Giới Thiệu

Service tìm kiếm web được tích hợp vào MCP server cho phép AI (DeepSeek) tìm kiếm thông tin trên internet và trả kết quả về ESP32.

## Cài Đặt

### 1. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

### 2. Cấu hình MCP endpoint:
```bash
export MCP_ENDPOINT=ws://your-server:port/ws
```

## Chạy Service

### Chạy riêng Web Search service:
```bash
python mcp_pipe.py google_search.py
```

### Chạy tất cả services (bao gồm calculator và search):
```bash
python mcp_pipe.py
```

## Cách Sử Dụng

### 1. Qua DeepSeek API (Tự động)

Khi bạn hỏi AI về thông tin cần tìm kiếm, nó sẽ tự động gọi tool `search_google`.

**Ví dụ câu hỏi:**
- "Tìm kiếm thông tin về ESP32"
- "Search for Python tutorials"
- "Tìm các bài viết về Machine Learning bằng tiếng Việt"

### 2. Tool Interface

**Tool name:** `search_google`

**Parameters:**
- `query` (string, required): Từ khóa tìm kiếm
- `num_results` (int, optional): Số kết quả trả về (mặc định: 5, tối đa: 10)
- `lang` (string, optional): Ngôn ngữ (mặc định: "vi", hỗ trợ mọi ngôn ngữ)

**Example Request (MCP format):**
```json
{
  "name": "search_google",
  "arguments": {
    "query": "ESP32 tutorial",
    "num_results": 5,
    "lang": "en"
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "query": "ESP32 tutorial",
  "total_results": 5,
  "results": [
    {
      "rank": 1,
      "title": "ESP32 Getting Started Guide",
      "url": "https://example.com/esp32-guide",
      "snippet": "Complete guide to getting started with ESP32..."
    },
    {
      "rank": 2,
      "title": "ESP32 Tutorial for Beginners",
      "url": "https://example.com/esp32-beginner",
      "snippet": "Learn ESP32 programming from scratch..."
    }
  ]
}
```

## Kiến Trúc Hệ Thống

```
ESP32 Device
    ↓
DeepSeek AI Server
    ↓
MCP Server (google_search.py)
    ↓
DuckDuckGo Search API
    ↓
Return Results → ESP32
```

## Tính Năng

✅ Tìm kiếm web toàn cầu
✅ Hỗ trợ mọi ngôn ngữ (Tiếng Việt, English, etc.)
✅ Trả về title, URL và snippet
✅ Giới hạn kết quả để tránh quá tải
✅ Error handling hoàn chỉnh
✅ Logging chi tiết
✅ Tối ưu cho ESP32 (JSON nhỏ gọn)

## Testing

Chạy test script để kiểm tra service:
```bash
python test_google_search.py
```

## Lưu Ý

1. **Rate Limiting:** Service sử dụng DuckDuckGo, có giới hạn request. Nên cache kết quả nếu cần.
2. **Network:** Cần kết nối internet để hoạt động.
3. **ESP32 Memory:** Kết quả được tối ưu để phù hợp với bộ nhớ giới hạn của ESP32.
4. **Language:** Tham số `lang` được giữ để tương thích nhưng DuckDuckGo tự động xử lý ngôn ngữ dựa trên query.

## Troubleshooting

### Service không trả kết quả:
- Kiểm tra kết nối internet
- Xem logs: Thông tin chi tiết trong console
- Test trực tiếp: `python test_google_search.py`

### Error "Connection refused":
- Kiểm tra MCP_ENDPOINT đã đúng chưa
- Đảm bảo WebSocket server đang chạy

### ESP32 không nhận được dữ liệu:
- Kiểm tra format JSON
- Xem log của DeepSeek server
- Kiểm tra network giữa ESP32 và DeepSeek

## Ví Dụ Use Cases

### 1. Tra cứu thông tin kỹ thuật
```
User → ESP32: "Tìm datasheet ESP32-S3"
AI tự động gọi: search_google("ESP32-S3 datasheet")
ESP32 nhận: Top 5 links về datasheet
```

### 2. Tìm tutorial
```
User → ESP32: "How to use I2C on ESP32"
AI tự động gọi: search_google("ESP32 I2C tutorial")
ESP32 nhận: Links to tutorials
```

### 3. Tìm tin tức
```
User → ESP32: "Tin tức AI mới nhất"
AI tự động gọi: search_google("tin tức AI mới nhất")
ESP32 nhận: Latest AI news links
```

## Performance

- **Latency:** ~1-3 giây cho mỗi search
- **Throughput:** ~10-20 requests/minute (giới hạn của DuckDuckGo)
- **Data size:** ~500-2000 bytes JSON per result

## Security

- ✅ Không lưu trữ search history
- ✅ Không thu thập thông tin người dùng
- ✅ HTTPS cho mọi requests
- ✅ Input validation và sanitization

## Future Enhancements

- [ ] Cache kết quả tìm kiếm
- [ ] Hỗ trợ tìm kiếm hình ảnh
- [ ] Tìm kiếm tin tức
- [ ] Tìm kiếm video
- [ ] Custom search filters
