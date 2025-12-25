#!/usr/bin/env python3
"""
Test Hot News Feature - Vietnam + International
"""

import json
import logging
from ddgs import DDGS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('HotNewsTest')

def fetch_hot_news(max_results=6):
    """Test hot news fetching (Vietnam + International)"""
    try:
        news_results = []
        ddgs = DDGS()
        
        # Fetch Vietnam hot news
        vn_count = max(2, max_results // 2)
        logger.info(f"🇻🇳 Fetching {vn_count} hot Vietnam news...")
        vn_results = list(ddgs.news(
            query="Việt Nam",
            region='vn-vi',
            timelimit='d',
            max_results=vn_count
        ))
        
        for idx, article in enumerate(vn_results, start=1):
            news_results.append({
                "rank": len(news_results) + 1,
                "title": f"🇻🇳 {article.get('title', 'No title')}",
                "url": article.get('url') or article.get('link', ''),
                "source": article.get('source', 'Unknown'),
                "date": article.get('date', ''),
                "excerpt": (article.get('body') or '')[:150],
                "category": "Vietnam"
            })
        
        # Fetch International breaking news
        intl_count = max(2, max_results - len(news_results))
        logger.info(f"🌍 Fetching {intl_count} international breaking news...")
        intl_results = list(ddgs.news(
            query="breaking news",
            region='wt-wt',
            timelimit='d',
            max_results=intl_count
        ))
        
        for idx, article in enumerate(intl_results, start=1):
            news_results.append({
                "rank": len(news_results) + 1,
                "title": f"🌍 {article.get('title', 'No title')}",
                "url": article.get('url') or article.get('link', ''),
                "source": article.get('source', 'Unknown'),
                "date": article.get('date', ''),
                "excerpt": (article.get('body') or '')[:150],
                "category": "International"
            })
        
        return {
            "success": True,
            "query": "Hot news (Vietnam + International)",
            "total_results": len(news_results),
            "articles": news_results
        }
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return {
            "success": False,
            "error": str(e),
            "articles": []
        }

def main():
    print("="*70)
    print("🌟 Testing HOT NEWS Feature (Vietnam + International)")
    print("="*70)
    print("\nFetching hot news from Vietnam 🇻🇳 and International 🌍 sources...")
    print()
    
    result = fetch_hot_news(max_results=6)
    
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n" + "="*70)
    print("✅ Hot news test completed!")
    print("="*70)
    
    # Display formatted for ESP32
    print("\n📱 Format for ESP32 Display (40 chars):")
    print("-"*70)
    for article in result.get('articles', [])[:5]:
        title = article['title'][:37] + "..." if len(article['title']) > 40 else article['title']
        print(f"{article['rank']}. {title}")
        print(f"   {article['source'][:37]}")
        print(f"   {article.get('category', 'News')}")
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
