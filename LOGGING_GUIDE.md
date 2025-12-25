# MCP Server Logging Guide

## 📋 Tổng Quan

Tất cả MCP servers đã được cấu hình với logging chi tiết để bạn có thể theo dõi hoạt động khi chạy `python mcp_pipe.py`.

## 🎯 Các Log Levels

- **INFO** ✅: Hoạt động bình thường (requests, results, status)
- **WARNING** ⚠️: Cảnh báo (tham số được điều chỉnh, etc.)
- **ERROR** ❌: Lỗi (search failed, calculation errors)
- **DEBUG** 🔍: Chi tiết kỹ thuật (khi cần troubleshoot sâu)

## 📊 Format Log

```
2025-12-24 10:30:45 - [ServiceName] - LEVEL - Message
```

## 🔍 Google Search Service Logs

### Khi nhận request:
```
============================================================
🔍 NEW SEARCH REQUEST RECEIVED
Query: 'Python programming'
Requested results: 5
Language: vi
⏳ Starting web search...
```

### Khi tìm thấy kết quả:
```
✅ Search completed successfully!
Found 5 results for query: 'Python programming'
Top result: Python.org - Official Website...
============================================================
```

### Khi có lỗi:
```
============================================================
❌ SEARCH FAILED
Query: 'invalid query'
Error: Connection timeout
============================================================
```

## 🧮 Calculator Service Logs

### Khi nhận request:
```
============================================================
🧮 CALCULATOR REQUEST RECEIVED
Expression: 2 + 2 * 10
```

### Khi tính toán thành công:
```
✅ Calculation successful!
Result: 22
============================================================
```

### Khi có lỗi:
```
❌ CALCULATION FAILED
Expression: invalid_expr
Error: name 'invalid_expr' is not defined
============================================================
```

## 🚀 Cách Xem Logs

### 1. Chạy server trực tiếp:
```bash
python calculator.py
# hoặc
python google_search.py
```

Logs sẽ xuất hiện trên stderr (terminal của bạn).

### 2. Chạy qua mcp_pipe.py:
```bash
python mcp_pipe.py calculator.py
```

Logs từ cả mcp_pipe.py VÀ service sẽ hiển thị.

### 3. Chạy tất cả services:
```bash
python mcp_pipe.py
```

Logs từ tất cả services sẽ được hiển thị với prefix [ServiceName].

### 4. Test logging:
```bash
python test_logging.py
```

Chạy automated tests và hiển thị tất cả logs.

## 🎨 Log Symbols

- 🔍 - Search operation
- 🧮 - Calculator operation
- 🚀 - Server startup
- 📡 - Server ready
- 💡 - Available tools
- ⏳ - Processing
- ✅ - Success
- ❌ - Error
- ⚠️ - Warning
- 🛑 - Shutdown

## 📝 Ví Dụ Output Thực Tế

### Running Calculator Service:
```
2025-12-24 10:30:45 - [Calculator] - INFO - ============================================================
2025-12-24 10:30:45 - [Calculator] - INFO - Calculator MCP Service Starting...
2025-12-24 10:30:45 - [Calculator] - INFO - ============================================================
2025-12-24 10:30:45 - [Calculator] - INFO - 🚀 Starting MCP server with stdio transport...
2025-12-24 10:30:45 - [Calculator] - INFO - 📡 Server is ready to receive requests from MCP clients
2025-12-24 10:30:45 - [Calculator] - INFO - 💡 Available tools: calculator
2025-12-24 10:30:45 - [Calculator] - INFO - Waiting for requests...

2025-12-24 10:30:50 - [Calculator] - INFO - ============================================================
2025-12-24 10:30:50 - [Calculator] - INFO - 🧮 CALCULATOR REQUEST RECEIVED
2025-12-24 10:30:50 - [Calculator] - INFO - Expression: math.sqrt(144)
2025-12-24 10:30:50 - [Calculator] - INFO - ✅ Calculation successful!
2025-12-24 10:30:50 - [Calculator] - INFO - Result: 12.0
2025-12-24 10:30:50 - [Calculator] - INFO - ============================================================
```

### Running Google Search Service:
```
2025-12-24 10:31:00 - [GoogleSearch] - INFO - ============================================================
2025-12-24 10:31:00 - [GoogleSearch] - INFO - Google Search MCP Service Starting...
2025-12-24 10:31:00 - [GoogleSearch] - INFO - ============================================================
2025-12-24 10:31:00 - [GoogleSearch] - INFO - 🚀 Starting MCP server with stdio transport...
2025-12-24 10:31:00 - [GoogleSearch] - INFO - 📡 Server is ready to receive requests from MCP clients
2025-12-24 10:31:00 - [GoogleSearch] - INFO - 💡 Available tools: search_google
2025-12-24 10:31:00 - [GoogleSearch] - INFO - Waiting for requests...

2025-12-24 10:31:05 - [GoogleSearch] - INFO - ============================================================
2025-12-24 10:31:05 - [GoogleSearch] - INFO - 🔍 NEW SEARCH REQUEST RECEIVED
2025-12-24 10:31:05 - [GoogleSearch] - INFO - Query: 'ESP32 programming'
2025-12-24 10:31:05 - [GoogleSearch] - INFO - Requested results: 5
2025-12-24 10:31:05 - [GoogleSearch] - INFO - Language: vi
2025-12-24 10:31:05 - [GoogleSearch] - INFO - ⏳ Starting web search...
2025-12-24 10:31:07 - [GoogleSearch] - INFO - ✅ Search completed successfully!
2025-12-24 10:31:07 - [GoogleSearch] - INFO - Found 5 results for query: 'ESP32 programming'
2025-12-24 10:31:07 - [GoogleSearch] - INFO - Top result: ESP32 Programming Guide - Espressif...
2025-12-24 10:31:07 - [GoogleSearch] - INFO - ============================================================
```

## 🔧 Troubleshooting với Logs

### Không thấy logs?
1. Kiểm tra logging level trong file
2. Đảm bảo chạy từ terminal (không redirect stderr)
3. Thử: `python script.py 2>&1 | less` để xem tất cả output

### Logs bị lộn xộn?
- Mỗi service có separators (====) để dễ đọc
- Mỗi request có timestamp riêng
- Emoji giúp nhận diện nhanh loại message

### Cần debug sâu hơn?
Thay đổi level trong code:
```python
logging.basicConfig(level=logging.DEBUG)  # Thay vì INFO
```

## 💡 Tips

1. **Grep logs**: `python mcp_pipe.py 2>&1 | grep "ERROR"`
2. **Save logs**: `python mcp_pipe.py 2>&1 | tee server.log`
3. **Watch logs**: `tail -f server.log` (nếu đã save)
4. **Filter by service**: `python mcp_pipe.py 2>&1 | grep "GoogleSearch"`

## 🎯 Best Practices

1. ✅ Luôn check logs khi có vấn đề
2. ✅ Save logs khi deploy production
3. ✅ Monitor logs để tối ưu performance
4. ✅ Logs giúp hiểu flow của requests
5. ✅ Dùng timestamps để đo latency

---

**Lưu ý**: Logs được output ra stderr để tách biệt với MCP protocol messages (stdout).
