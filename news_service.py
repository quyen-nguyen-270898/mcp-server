# news_service.py
from fastmcp import FastMCP
import sys
import logging
from typing import Optional, List, Dict
import feedparser
import requests
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json

# Configure logging with detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('NewsService')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

logger.info('='*60)
logger.info('News Service MCP Service Starting...')
logger.info('='*60)

# Create an MCP server
mcp = FastMCP("NewsService")

# Cache for RSS feed results (to ensure pagination consistency)
# Key: (source, timelimit, keywords_hash) -> Value: (articles, timestamp)
_news_cache = {}
_cache_ttl = 60  # Cache for 60 seconds

# Vietnamese news sources RSS feeds with priorities
RSS_FEEDS = {
    1: ("VnExpress", "https://vnexpress.net/rss/tin-moi-nhat.rss"),
    2: ("Dân Trí", "https://dantri.com.vn/rss/tin-moi-nhat.rss"),
}

def fetch_rss_feed(source_name: str, url: str, max_per_source: int = 10) -> List[Dict]:
    """Fetch and parse RSS feed from a news source"""
    try:
        logger.info(f"  📡 Fetching from {source_name}...")
        
        # Fetch RSS with timeout
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        # Parse RSS feed
        feed = feedparser.parse(response.content)
        
        articles = []
        for entry in feed.entries[:max_per_source]:
            # Parse publication date
            article_time = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                article_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                article_time = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'published'):
                try:
                    parsed = parsedate_to_datetime(entry.published)
                    # Ensure timezone aware
                    if parsed.tzinfo is None:
                        article_time = parsed.replace(tzinfo=timezone.utc)
                    else:
                        article_time = parsed
                except:
                    pass
            
            # Get description/summary
            description = ""
            if hasattr(entry, 'description'):
                description = entry.description
            elif hasattr(entry, 'summary'):
                description = entry.summary
            
            # Clean HTML tags from description
            import re
            description = re.sub(r'<[^>]+>', '', description)
            description = description.strip()[:300]
            
            article = {
                "title": entry.title if hasattr(entry, 'title') else 'No title',
                "url": entry.link if hasattr(entry, 'link') else '',
                "source": source_name,
                "date": entry.published if hasattr(entry, 'published') else '',
                "excerpt": description,
                "time": article_time
            }
            articles.append(article)
        
        logger.info(f"     ✓ Got {len(articles)} articles from {source_name}")
        return articles
        
    except requests.exceptions.Timeout:
        logger.warning(f"     ⚠️  Timeout fetching {source_name}")
        return []
    except requests.exceptions.RequestException as e:
        logger.warning(f"     ⚠️  Error fetching {source_name}: {str(e)[:100]}")
        return []
    except Exception as e:
        logger.warning(f"     ⚠️  Parse error for {source_name}: {str(e)[:100]}")
        return []

def fetch_latest_news(keywords: Optional[str] = None, max_results: int = 5, timelimit: str = 'd', region: str = 'vn-vi', offset: int = 0, source: str = 'vnexpress'):
    """
    Fetch latest news from Vietnamese news sources via RSS feeds
    
    Args:
        keywords: Keywords to filter news (optional - filters by title/content)
        max_results: Number of results to return
        timelimit: Time limit - 'd' (day), 'w' (week), 'm' (month)
        region: Not used (kept for API compatibility)
        offset: Number of articles to skip (for pagination)
        source: Which source to fetch from - 'vnexpress', 'dantri', or 'all'
    """
    global _news_cache
    
    # Create cache key based on parameters
    keywords_hash = hashlib.md5(str(keywords).encode()).hexdigest() if keywords else 'none'
    cache_key = f"{source}_{timelimit}_{keywords_hash}"
    current_time = datetime.now(timezone.utc)
    
    # Check cache first
    if cache_key in _news_cache:
        cached_articles, cache_time = _news_cache[cache_key]
        if (current_time - cache_time).total_seconds() < _cache_ttl:
            logger.info(f"📦 Using cached data (age: {int((current_time - cache_time).total_seconds())}s)")
            # Apply pagination to cached data
            total_available = len(cached_articles)
            paginated_articles = cached_articles[offset:offset + max_results]
            has_more = (offset + max_results) < total_available
            
            return {
                'articles': paginated_articles,
                'total_available': total_available,
                'has_more': has_more
            }
    
    try:
        logger.info(f"📰 Fetching news from Vietnamese RSS feeds...")
        
        # Treat empty string as None
        if keywords is not None and keywords.strip() == '':
            keywords = None
        
        if keywords:
            logger.info(f"🔎 Filtering by keywords: '{keywords}'")
        else:
            logger.info(f"📰 Fetching latest news from all major Vietnamese sources")
        
        # Calculate cutoff time based on timelimit
        now = datetime.now(timezone.utc)
        if timelimit == 'd':
            cutoff_time = now - timedelta(hours=24)
        elif timelimit == 'w':
            cutoff_time = now - timedelta(weeks=1)
        elif timelimit == 'm':
            cutoff_time = now - timedelta(days=30)
        else:
            cutoff_time = now - timedelta(hours=24)
        
        logger.info(f"⏰ Filtering articles after: {cutoff_time.strftime('%Y-%m-%d %H:%M')}")
        
        # Filter RSS feeds by source parameter
        all_articles = []
        feeds_to_fetch = RSS_FEEDS.items()
        
        if source == 'vnexpress':
            feeds_to_fetch = [(p, (n, u)) for p, (n, u) in RSS_FEEDS.items() if 'vnexpress' in n.lower()]
        elif source == 'dantri':
            feeds_to_fetch = [(p, (n, u)) for p, (n, u) in RSS_FEEDS.items() if 'dân trí' in n.lower()]
        # else source == 'all': fetch from all feeds
        
        for priority, (source_name, rss_url) in feeds_to_fetch:
            articles = fetch_rss_feed(source_name, rss_url, max_per_source=30)
            for article in articles:
                article['priority'] = priority
            all_articles.extend(articles)
        
        logger.info(f"📊 Total fetched: {len(all_articles)} articles from {len(RSS_FEEDS)} sources")
        
        # Filter by keywords if provided
        if keywords:
            keywords_lower = keywords.lower()
            filtered_articles = []
            for article in all_articles:
                title_lower = article.get('title', '').lower()
                excerpt_lower = article.get('excerpt', '').lower()
                if keywords_lower in title_lower or keywords_lower in excerpt_lower:
                    filtered_articles.append(article)
            all_articles = filtered_articles
            logger.info(f"🔍 After keyword filter: {len(all_articles)} articles")
        
        # Filter by time
        filtered_count = 0
        time_filtered_articles = []
        for article in all_articles:
            article_time = article.get('time')
            if article_time and article_time < cutoff_time:
                filtered_count += 1
                continue
            time_filtered_articles.append(article)
        
        all_articles = time_filtered_articles
        
        if filtered_count > 0:
            logger.info(f"🗑️  Filtered out {filtered_count} old articles")
        
        # Sort by: 1) Date (descending - newest first), 2) Source priority (ascending)
        all_articles.sort(key=lambda x: (
            -(x.get('time') or datetime.min.replace(tzinfo=timezone.utc)).timestamp(),
            x.get('priority', 999)
        ))
        
        # Apply pagination
        total_available = len(all_articles)
        start_idx = offset
        end_idx = offset + max_results
        paginated_articles = all_articles[start_idx:end_idx]
        
        logger.info(f"📄 Pagination: Showing {len(paginated_articles)} articles (offset: {offset}, total available: {total_available})")
        
        # Take only max_results
        news_results = []
        for idx, article in enumerate(paginated_articles, start=offset+1):
            article["rank"] = idx
            title = article["title"]
            source = article["source"]
            date = article.get("date", '')
            priority = article.get("priority", 999)
            
            # Log with priority indicator
            priority_label = f"P{priority}" if priority <= 8 else "Other"
            logger.info(f"  ✓ [{idx}] {title[:60]}...")
            logger.info(f"       Source: {source} ({priority_label}) | Date: {date[:10] if date else 'N/A'}")
            
            # Remove 'time' and 'priority' fields before returning
            if 'time' in article:
                del article["time"]
            if 'priority' in article:
                del article["priority"]
            news_results.append(article)
        
        if filtered_count > 0:
            logger.info(f"🗑️  Filtered out {filtered_count} old articles")
        
        logger.info(f"✅ Parsed {len(news_results)} news articles successfully")
        
        # Cache the full sorted articles list (before pagination)
        _news_cache[cache_key] = (all_articles, current_time)
        logger.info(f"💾 Cached {len(all_articles)} articles for {_cache_ttl}s")
        
        # Add metadata about available articles
        return {
            'articles': news_results,
            'total_available': total_available,
            'offset': offset,
            'has_more': end_idx < total_available
        }
        
    except Exception as e:
        logger.error(f"❌ Error fetching news: {e}")
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise

@mcp.tool()
def get_latest_news(
    keywords: Optional[str] = None,
    max_results: int = 3,
    timelimit: str = 'd',
    region: str = 'vn-vi',
    offset: int = 0,
    source: str = 'vnexpress'
) -> dict:
    """
    Get latest news articles from Vietnamese news sources via RSS feeds.
    Returns 3 articles by default (client reading capacity).
    
    Available sources:
    - VnExpress (vnexpress.net) - Default
    - Dân Trí (dantri.com.vn) - On request
    
    Args:
        keywords: Keywords to filter news by title/content (optional).
                 If None/empty: Returns all latest news from Vietnamese sources
                 Examples: "công nghệ", "thể thao", "kinh tế", "covid", "bóng đá"
        max_results: Number of news articles to return (default: 3, max: 50)
        timelimit: Time range for news:
                  'd' = last 24 hours (default)
                  'w' = last week
                  'm' = last month
        region: Not used (kept for API compatibility)
        offset: Number of articles to skip for pagination (default: 0)
                Use this to get more articles: offset=0 gets first 3,
                offset=3 gets next 3, offset=6 gets next 3, etc.
        source: Which news source to fetch from (default: 'vnexpress')
                Options: 'vnexpress', 'dantri', 'all'
    
    Returns:
        dict with success status, articles, and pagination info
        
    Example response:
        {
            "success": true,
            "query": "Latest Vietnamese News",
            "total_results": 5,
            "total_available": 25,
            "offset": 0,
            "has_more": true,
            "timelimit": "d",
            "articles": [
                {
                    "rank": 1,
                    "title": "Breaking news headline...",
                    "source": "VnExpress",
                    "date": "Thu, 25 Dec 2025 21:24:28 +0700",
                    "url": "https://vnexpress.net/...",
                    "excerpt": "Article excerpt..."
                }
            ]
        }
    """
    try:
        logger.info('='*60)
        logger.info(f"📰 NEW NEWS REQUEST RECEIVED")
        
        # Treat empty string as None
        if keywords is not None and keywords.strip() == '':
            keywords = None
        
        source_label = "VnExpress only" if source == 'vnexpress' else ("Dân Trí only" if source == 'dantri' else "all sources")
        if keywords is None:
            logger.info(f"📰 Mode: Latest Vietnamese News ({source_label})")
            query_display = "Latest Vietnamese News"
        else:
            logger.info(f"Keywords: {keywords}")
            query_display = keywords
            
        logger.info(f"Max results: {max_results}")
        logger.info(f"Time limit: {timelimit}")
        logger.info(f"Offset: {offset}")
        if keywords is not None:
            logger.info(f"Region: {region}")
        
        # Limit max_results to prevent abuse
        max_results = min(max(1, max_results), 50)
        
        # Validate timelimit
        if timelimit not in ['d', 'w', 'm']:
            logger.warning(f"Invalid timelimit '{timelimit}', using 'd' (day)")
            timelimit = 'd'
        
        logger.info(f"⏳ Fetching latest news...")
        
        # Fetch news with pagination
        result_data = fetch_latest_news(keywords, max_results, timelimit, region, offset, source)
        news_articles = result_data['articles']
        total_available = result_data['total_available']
        has_more = result_data['has_more']
        
        logger.info(f"✅ News fetch completed successfully!")
        logger.info(f"Found {len(news_articles)} news articles (total available: {total_available})")
        
        # Log first article as sample
        if news_articles:
            logger.info(f"Top article: {news_articles[0]['title'][:60]}...")
            logger.info(f"Source: {news_articles[0]['source']}")
        
        if has_more:
            logger.info(f"💡 More articles available. Use offset={offset + max_results} to see more.")
        
        logger.info('='*60)
        
        result = {
            "success": True,
            "query": query_display,
            "total_results": len(news_articles),
            "total_available": total_available,
            "offset": offset,
            "has_more": has_more,
            "timelimit": timelimit,
            "articles": news_articles
        }
        
        # Add region only if keywords was specified
        if keywords is not None:
            result["region"] = region
            
        return result
        
    except Exception as e:
        error_msg = f"Error fetching news: {str(e)}"
        logger.error('='*60)
        logger.error(f"❌ NEWS FETCH FAILED")
        logger.error(f"Keywords: {keywords}")
        logger.error(f"Error: {error_msg}")
        logger.error('='*60)
        return {
            "success": False,
            "error": error_msg,
            "query": keywords,
            "articles": []
        }

@mcp.tool()
def get_hot_news(
    max_results: int = 3,
    timelimit: str = 'd',
    offset: int = 0,
    source: str = 'vnexpress'
) -> dict:
    """
    Get HOT/BREAKING news from Vietnamese sources.
    Returns 3 hot articles by default (client reading capacity).
    Filters for urgent, important, or trending news based on keywords.
    
    Hot news indicators include:
    - Khẩn cấp, nóng, nổi bật, đột phá, chấn động
    - Breaking, urgent, exclusive
    - Tin nhanh, tin mới, vừa xảy ra
    
    Args:
        max_results: Number of hot news to return (default: 3, max: 50)
        timelimit: Time range:
                  'd' = last 24 hours (default)
                  'w' = last week
                  'm' = last month
        offset: Number of articles to skip for pagination (default: 0)
                Use this to get more hot news: offset=0 gets first 3,
                offset=3 gets next 3, offset=6 gets next 3, etc.
    
    Returns:
        dict with hot news articles sorted by hotness score and pagination info
    """
    try:
        logger.info('='*60)
        logger.info(f"🔥 HOT NEWS REQUEST RECEIVED")
        source_label = "VnExpress only" if source == 'vnexpress' else ("Dân Trí only" if source == 'dantri' else "all sources")
        logger.info(f"🔥 Source: {source_label}")
        logger.info(f"Max results: {max_results}")
        logger.info(f"Time limit: {timelimit}")
        logger.info(f"Offset: {offset}")
        
        max_results = min(max(1, max_results), 50)
        
        if timelimit not in ['d', 'w', 'm']:
            logger.warning(f"Invalid timelimit '{timelimit}', using 'd'")
            timelimit = 'd'
        
        logger.info(f"🔥 Fetching and analyzing news for hot topics...")
        
        # Fetch ALL available articles to analyze (not just 30)
        # This ensures consistent hot news ranking across pagination
        result_data = fetch_latest_news(keywords=None, max_results=50, timelimit=timelimit, offset=0, source=source)
        all_articles = result_data['articles']
        
        logger.info(f"📊 Analyzing {len(all_articles)} articles for hot indicators...")
        
        # Hot keywords (higher score = hotter)
        # Expanded list to catch more hot news
        hot_indicators = {
            'khẩn cấp': 10, 'nóng': 8, 'đột phá': 7, 'chấn động': 7,
            'nổi bật': 6, 'bất ngờ': 6, 'sốc': 7, 'lần đầu': 5,
            'breaking': 10, 'urgent': 9, 'exclusive': 7,
            'vừa xảy ra': 8, 'mới xảy ra': 8, 'tin nhanh': 6,
            'đặc biệt': 5, 'quan trọng': 4, 'nghiêm trọng': 7,
            'khẩn': 8, 'nhanh': 3, 'mới': 2, 'hot': 6,
            'cháy': 9, 'nổ': 8, 'tai nạn': 6, 'thiệt hại': 5,
            'bắt giữ': 6, 'khởi tố': 6, 'điều tra': 4,
            'biểu tình': 7, 'đình công': 7, 'xung đột': 8,
            'từ chức': 6, 'từ nhiệm': 6, 'bổ nhiệm': 4, 'qua đời': 5,
            'tử vong': 6, 'tử nạn': 7, 'thiệt mạng': 7,
            'tăng đột biến': 6, 'giảm mạnh': 6, 'kỷ lục': 7,
            'nghiêm cấm': 5, 'cấm': 4, 'truy tố': 5,
            'ùn tắc': 4, 'tê liệt': 5, 'gián đoạn': 4,
            'đề xuất': 3, 'kiến nghị': 3, 'yêu cầu': 2,
            'mạnh': 3, 'lớn': 2, 'nghiêm': 4,
        }
        
        # Score each article
        hot_news = []
        for article in all_articles:
            title = article.get('title', '').lower()
            excerpt = article.get('excerpt', '').lower()
            
            # Calculate hotness score
            score = 0
            matched_keywords = []
            
            for keyword, points in hot_indicators.items():
                if keyword in title:
                    score += points * 2  # Title matches worth double
                    matched_keywords.append(keyword)
                elif keyword in excerpt:
                    score += points
                    matched_keywords.append(keyword)
            
            if score > 0:
                article['hotness_score'] = score
                article['hot_keywords'] = matched_keywords
                hot_news.append(article)
                logger.info(f"  🔥 Hot: {article['title'][:50]}... (score: {score})")
        
        # Sort by hotness score (highest first)
        hot_news.sort(key=lambda x: x.get('hotness_score', 0), reverse=True)
        
        logger.info(f"📊 Total hot news found: {len(hot_news)}")
        
        # Apply pagination
        total_hot_available = len(hot_news)
        start_idx = offset
        end_idx = offset + max_results
        paginated_hot_news = hot_news[start_idx:end_idx]
        
        logger.info(f"📄 Hot news pagination: Showing {len(paginated_hot_news)} articles (offset: {offset}, total hot: {total_hot_available})")
        
        # Re-rank and clean up
        for idx, article in enumerate(paginated_hot_news, start=offset+1):
            article['rank'] = idx
            # Remove internal scoring fields
            article.pop('hotness_score', None)
            article.pop('hot_keywords', None)
        
        has_more = end_idx < total_hot_available
        
        logger.info(f"✅ Returning {len(paginated_hot_news)} hot news articles")
        
        if has_more:
            logger.info(f"💡 More hot news available. Use offset={offset + max_results} to see more.")
        
        logger.info('='*60)
        
        return {
            "success": True,
            "query": "Hot News",
            "total_results": len(paginated_hot_news),
            "total_hot_found": total_hot_available,
            "offset": offset,
            "has_more": has_more,
            "timelimit": timelimit,
            "articles": paginated_hot_news
        }
        
    except Exception as e:
        error_msg = f"Error fetching hot news: {e}"
        logger.error('='*60)
        logger.error(f"❌ HOT NEWS FETCH FAILED")
        logger.error(f"Error: {error_msg}")
        logger.error('='*60)
        return {
            "success": False,
            "error": error_msg,
            "articles": []
        }

# Start the server
if __name__ == "__main__":
    logger.info("🚀 Starting MCP server with stdio transport...")
    logger.info("📡 Server is ready to receive requests from MCP clients")
    logger.info("💡 Available tools: get_latest_news, get_hot_news")
    logger.info("Waiting for requests...\n")
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"\n❌ Server error: {e}")
        raise
