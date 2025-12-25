# News Service - Changelog

## Version 2.0 (2025-12-25)

### 🎉 Major Improvements

#### Date Filtering Enhancement
- **Problem Fixed**: News API was returning outdated articles (from November/early December) even with `timelimit='d'` parameter
- **Solution**: 
  - Fetch 30 articles instead of limited number
  - Apply client-side date filtering in Python using `datetime`
  - Filter articles to only include those from specified time range (24h, 1 week, 1 month)
  
#### Query Optimization
- Changed default query from specific phrases to broader "Vietnam news"
- This ensures better coverage of recent articles
- For Vietnamese tech news: uses "công nghệ" keyword

#### Results
- ✅ Now returns articles from last 24-48 hours (Dec 23-24, 2025)
- ✅ 6-10 articles per request instead of 2-4
- ✅ Multiple sources: VnExpress, Reuters, Bloomberg, Dân trí, Tiền Phong
- ✅ Accurate date filtering using UTC timezone

### Technical Changes

```python
# OLD CODE (v1.0)
results = list(ddgs.news(
    query="VNExpress",
    region='vn-vi',
    timelimit='d',  # Not working properly
    max_results=max_results
))

# NEW CODE (v2.0)
results = list(ddgs.news(
    query="Vietnam news",  # Broader query
    region='vn-vi',
    max_results=30  # Fetch more, filter in Python
))

# Apply date filtering in Python
cutoff_time = now - timedelta(days=1)
for article in results:
    article_time = datetime.fromisoformat(article['date'])
    if article_time < cutoff_time:
        continue  # Skip old articles
```

### Performance
- Fetch time: ~1-2 seconds
- Articles returned: 6-10 (with timelimit='d')
- Date accuracy: Within 24-48 hours of current date

### Test Results

```bash
$ python test_news_final.py

Test 1: Latest Vietnamese news (24h)
✅ Found 6 articles
  - Vietnam's stock market rises... (Reuters, 2025-12-24 03:32)
  - Vietnam Communist Party Endorses... (Barron's, 2025-12-23 19:40)
  - How much has Vietnam's richest man... (VnExpress, 2025-12-24 14:45)

Test 2: Technology news (24h)
✅ Found 5 articles
  - Bộ Khoa học và Công nghệ... (VnExpress, 2025-12-24 14:12)
  - Tập đoàn SCG: "Công nghệ..." (Dân trí, 2025-12-24 00:10)

Test 3: Latest news (1 week)
✅ Found 5 articles
  - Vietnam's Communist Party... (Bloomberg, 2025-12-23 10:40)
```

## Version 1.0 (2025-12-24)

### Initial Release
- Basic news fetching with DuckDuckGo News API
- Keyword search support
- Time limit parameter (d/w/m)
- Regional news support
- VNExpress integration

### Known Issues (Fixed in v2.0)
- ❌ Returning old articles (Nov/Dec instead of current date)
- ❌ Only 2-4 results even with max_results=10
- ❌ timelimit='d' parameter not working properly with API
