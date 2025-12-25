# 📰 News Service - Fix Summary

## 🐛 Problem
News service was returning **outdated articles** from November and early December 2025, even though current date is **December 25, 2025**.

Example of bad results:
```
❌ Articles dated: 2025-11-11, 2025-11-12, 2025-12-06
❌ Only 2 articles returned (requested 10)
❌ timelimit='d' parameter not working
```

## ✅ Solution

### 1. Changed Query Strategy
```python
# Before
search_query = "VNExpress"  # Too specific, limited results

# After  
search_query = "Vietnam news"  # Broader, more results
```

### 2. Implemented Client-Side Date Filtering
```python
# Fetch MORE articles (30 instead of 5-10)
results = list(ddgs.news(query, region='vn-vi', max_results=30))

# Filter by date in Python
cutoff_time = datetime.now(timezone.utc) - timedelta(days=1)
for article in results:
    article_time = datetime.fromisoformat(article['date'])
    if article_time >= cutoff_time:
        # Include this article
        news_results.append(article)
```

### 3. Enhanced Logging
```python
logger.info(f"📊 Raw API returned {len(results)} articles")
logger.info(f"⏰ Filtering articles after: {cutoff_time}")
logger.info(f"🗑️  Filtered out {filtered_count} old articles")
logger.info(f"✅ Parsed {len(news_results)} news articles")
```

## 📊 Results

### Before Fix:
```
Query: VNExpress
Results: 2 articles
Dates: 2025-11-11, 2025-11-12 (very old!)
```

### After Fix:
```
Query: Vietnam news
Results: 6-10 articles
Dates: 2025-12-23, 2025-12-24 (fresh!)

Sources:
✅ VnExpress International
✅ Reuters
✅ Bloomberg
✅ Dân trí
✅ Tiền Phong
✅ Barron's
```

## 🧪 Test Results

```bash
$ python test_news_final.py

Test 1: Latest Vietnamese news (24h)
─────────────────────────────────────
✅ Found 6 articles

1. Vietnam's stock market rises on signs of smooth power transition
   📰 Reuters | 📅 2025-12-24 03:32

2. Vietnam Communist Party Endorses To Lam To Stay In Top Job
   📰 Barron's | 📅 2025-12-23 19:40

3. How much has Vietnam's richest man Pham Nhat Vuong added to his wealth
   📰 VnExpress International | 📅 2025-12-24 14:45


Test 2: Technology news (24h)
──────────────────────────────
✅ Found 5 articles

1. Bộ Khoa học và Công nghệ bổ nhiệm 5 cán bộ
   📰 VnExpress | 📅 2025-12-24 14:12

2. Tập đoàn SCG: "Công nghệ là cầu nối để ESG đi từ cam kết đến hành động"
   📰 Báo Dân trí | 📅 2025-12-24 00:10


Test 3: Latest news (1 week)
────────────────────────────
✅ Found 5 articles from this week
```

## 📝 Key Changes

1. **Query**: `"VNExpress"` → `"Vietnam news"`
2. **Fetch count**: `max_results` → `30` (then filter)
3. **Date filtering**: API-side → Python-side (more reliable)
4. **Added imports**: `from datetime import datetime, timedelta, timezone`

## 🎯 Impact

- ✅ Articles are now **fresh** (within 24-48 hours)
- ✅ More results (6-10 instead of 2)
- ✅ Multiple sources (not just one)
- ✅ Accurate date filtering
- ✅ Better logging for debugging

## 🚀 How to Use

### Get latest Vietnamese news:
```python
from news_service import fetch_latest_news

# Get news from last 24 hours
news = fetch_latest_news(
    keywords=None,      # None = latest Vietnamese news
    max_results=10,
    timelimit='d'       # d=day, w=week, m=month
)

# Output: 6-10 articles from Dec 23-24
```

### Search specific topics:
```python
# Technology news
news = fetch_latest_news(
    keywords="công nghệ",
    max_results=5,
    timelimit='d'
)

# Sports news
news = fetch_latest_news(
    keywords="thể thao",
    max_results=5,
    timelimit='d'
)
```

## 🔧 Files Modified

- `news_service.py` - Main service file
  - Added `timedelta`, `timezone` imports
  - Changed query strategy
  - Added date filtering logic
  - Enhanced logging

- `test_news_final.py` - New comprehensive test file

- `NEWS_GUIDE.md` - Updated documentation

- `NEWS_CHANGELOG.md` - Version history

## ✨ Summary

The news service now reliably returns **fresh articles from the last 24 hours** instead of outdated content. This was achieved by:
1. Using a broader query
2. Fetching more results
3. Filtering dates in Python rather than relying on API

The fix ensures ESP32 users see **current news** when querying the MCP server! 🎉
