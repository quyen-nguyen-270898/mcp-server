# News Service - Hướng Dẫn Sử Dụng

## 📰 Giới Thiệu

News Service là tool chuyên biệt để lấy tin tức thời sự mới nhất từ nhiều nguồn khác nhau. Khác với search thông thường, tool này tập trung vào tin tức và sự kiện đang diễn ra.

## 🎯 Tính Năng

- ✅ Tin tức mới nhất (24h, 1 tuần, 1 tháng)
- ✅ **Lọc thông minh theo ngày** - đảm bảo tin luôn mới (từ 23-25/12/2025)
- ✅ Hỗ trợ đa ngôn ngữ (Việt Nam, English, etc.)
- ✅ Tin tức theo chủ đề (công nghệ, thể thao, kinh tế...)
- ✅ Thông tin đầy đủ: title, URL, source, date, excerpt
- ✅ Nguồn tin uy tín: VnExpress, Reuters, Bloomberg, Dân trí, Tiền Phong...
- ✅ Tối ưu cho ESP32

## 🚀 Cài Đặt & Chạy

### Chạy News Service:
```bash
python mcp_pipe.py news_service.py
```

### Hoặc chạy tất cả services:
```bash
python mcp_pipe.py
```

## 🛠️ Tool Interface

### Tool: `get_latest_news`

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `keywords` | string | No | `null` | Từ khóa tin tức. Để trống = tin tổng hợp |
| `max_results` | int | No | `5` | Số lượng tin (1-10) |
| `timelimit` | string | No | `"d"` | `"d"` = 24h, `"w"` = 1 tuần, `"m"` = 1 tháng |
| `region` | string | No | `"vn-vi"` | Vùng: `"vn-vi"`, `"en-us"`, `"en-gb"` |

### Ví Dụ Request (MCP format):

```json
{
  "name": "get_latest_news",
  "arguments": {
    "keywords": "công nghệ AI",
    "max_results": 5,
    "timelimit": "d",
    "region": "vn-vi"
  }
}
```

### Example Response:

```json
{
  "success": true,
  "query": "công nghệ AI",
  "total_results": 5,
  "timelimit": "d",
  "region": "vn-vi",
  "articles": [
    {
      "rank": 1,
      "title": "Công nghệ AI hỗ trợ tăng trưởng ngành bảo hiểm",
      "url": "https://vnexpress.net/article-123",
      "source": "VnExpress",
      "date": "2025-12-24T09:00:00+00:00",
      "excerpt": "Các chuyên gia cho rằng AI sẽ giúp ngành bảo hiểm..."
    }
  ]
}
```

## 📋 Use Cases

### 1. Tin Tức Tổng Hợp
```python
# Lấy tin tức Việt Nam 24h qua
get_latest_news()  # Không cần parameters

# Response: Tin tức tổng hợp từ nhiều nguồn
```

### 2. Tin Tức Theo Chủ Đề
```python
# Tin công nghệ
get_latest_news(keywords="công nghệ", max_results=5)

# Tin thể thao
get_latest_news(keywords="bóng đá", max_results=5)

# Tin kinh tế
get_latest_news(keywords="chứng khoán", max_results=5)
```

### 3. Tin Tức Quốc Tế
```python
# Breaking news (English)
get_latest_news(
    keywords="breaking news",
    max_results=5,
    region="en-us"
)

# Tech news (English)
get_latest_news(
    keywords="AI technology",
    max_results=5,
    region="en-us"
)
```

### 4. Tin Tức Tuần/Tháng
```python
# Tin tuần qua
get_latest_news(
    keywords="startup Việt Nam",
    timelimit="w"
)

# Tin tháng qua
get_latest_news(
    keywords="crypto",
    timelimit="m"
)
```

## 🎨 Sử Dụng qua ESP32/DeepSeek

### Tự Động (AI tự gọi):

**User:** "Cho tôi biết tin tức mới nhất"
→ AI gọi: `get_latest_news()`

**User:** "Tin công nghệ hôm nay"
→ AI gọi: `get_latest_news(keywords="công nghệ")`

**User:** "Breaking news about AI"
→ AI gọi: `get_latest_news(keywords="AI", region="en-us")`

### Format cho ESP32:

```python
# Compact display for ESP32 LCD (40 chars)
for article in response['articles'][:3]:
    print(f"{article['rank']}. {article['title'][:37]}...")
    print(f"   {article['source']}")
    print(f"   {article['date'][:16]}")
    print()
```

Output:
```
1. Công nghệ AI hỗ trợ tăng trưởng...
   VnExpress
   2025-12-24 09:00

2. Camera AI - công cụ then chốt...
   Tuổi Trẻ
   2025-12-24 09:15
```

## 🌍 Regions Supported

| Region | Code | Language | Coverage |
|--------|------|----------|----------|
| Việt Nam | `vn-vi` | Vietnamese | Tin tức VN |
| United States | `en-us` | English | US news |
| United Kingdom | `en-gb` | English | UK news |
| Global | `wt-wt` | English | World news |

## ⏰ Time Limits

- `d` (day): Tin 24 giờ qua - **Mặc định, cập nhật nhất**
- `w` (week): Tin 7 ngày qua
- `m` (month): Tin 30 ngày qua

## 🔍 Keywords Gợi Ý

### Tiếng Việt:
- Tin tổng hợp: `None` hoặc để trống
- Công nghệ: `"công nghệ"`, `"AI"`, `"điện thoại"`
- Thể thao: `"bóng đá"`, `"SEA Games"`, `"thể thao"`
- Kinh tế: `"chứng khoán"`, `"bất động sản"`, `"kinh tế"`
- Chính trị: `"chính trị"`, `"quốc hội"`

### English:
- General: `"breaking news"`, `"latest news"`
- Tech: `"technology"`, `"AI"`, `"tech"`
- Sports: `"football"`, `"NBA"`, `"sports"`
- Business: `"stocks"`, `"crypto"`, `"economy"`

## 📊 Logging

Service có logging chi tiết:

```
============================================================
📰 NEW NEWS REQUEST RECEIVED
Keywords: công nghệ AI
Max results: 5
Time limit: d
Region: vn-vi
⏳ Fetching latest news...
📊 Raw API returned 5 news articles
✅ News fetch completed successfully!
Found 5 news articles
Top article: Công nghệ AI hỗ trợ tăng trưởng ngành bảo hiểm
Source: VnExpress
============================================================
```

## 🐛 Troubleshooting

### Không có kết quả:
- Thử keywords khác (rộng hơn)
- Thử timelimit dài hơn ('w' hoặc 'm')
- Check region có phù hợp không

### Kết quả không đúng ngôn ngữ:
- Đổi region: `vn-vi` cho tiếng Việt
- Dùng keywords bằng ngôn ngữ mong muốn

### Lỗi timeout:
- Giảm max_results xuống 3-5
- Check kết nối internet

## 💡 Tips

1. **Để trống keywords** cho tin tổng hợp mới nhất
2. **Dùng timelimit='d'** cho tin nóng nhất
3. **Region='vn-vi'** cho tin Việt Nam
4. **max_results=3-5** tối ưu cho ESP32
5. **Keywords ngắn gọn** cho kết quả tốt hơn

## 🔄 So Sánh với Search Service

| Feature | News Service | Search Service |
|---------|-------------|----------------|
| Mục đích | Tin tức mới | Tìm kiếm tổng quát |
| Nguồn | Trang tin tức | Toàn web |
| Thời gian | Có filter time | Không filter |
| Date info | ✅ Có | ❌ Không |
| Source info | ✅ Có | ❌ Không |
| Best for | Tin thời sự | Tra cứu thông tin |

## 🧪 Testing

```bash
# Test standalone
python test_news_service.py

# Test qua MCP
python mcp_pipe.py news_service.py
```

## 📈 Performance

- **Latency**: ~2-4 giây
- **Data size**: ~1-3KB per article
- **Rate limit**: ~10-20 requests/minute
- **Freshness**: Cập nhật theo real-time

---

**Lưu ý**: Service sử dụng DuckDuckGo News API, nên nguồn tin đa dạng và tin cậy.
