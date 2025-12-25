#!/usr/bin/env python3
"""
Test News Service
Quick test for news fetching functionality
"""

import json
import logging
from ddgs import DDGS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('NewsTest')

def fetch_test_news(keywords: str = None, max_results: int = 5, timelimit: str = 'd', region: str = 'vn-vi'):
    """Test news fetching"""
    try:
        logger.info(f"Fetching news: keywords='{keywords}', limit={timelimit}, region={region}")
        
        news_results = []
        ddgs = DDGS()
        
        search_query = keywords if keywords else "tin tức Việt Nam"
        results = list(ddgs.news(
            query=search_query,
            region=region,
            timelimit=timelimit,
            max_results=max_results
        ))
        
        for idx, article in enumerate(results, start=1):
            news_results.append({
                "rank": idx,
                "title": article.get('title', 'No title'),
                "url": article.get('url') or article.get('link', ''),
                "source": article.get('source', 'Unknown'),
                "date": article.get('date', ''),
                "excerpt": (article.get('body') or article.get('excerpt', ''))[:200]
            })
        
        return {
            "success": True,
            "query": search_query,
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

def test_news_service():
    """Run test scenarios"""
    
    print("="*70)
    print("Testing News Service")
    print("="*70)
    
    # Test 1: General Vietnamese news
    print("\n📰 Test 1: Tin tức tổng hợp Việt Nam (24h qua)")
    result1 = fetch_test_news(keywords=None, max_results=3, timelimit='d', region='vn-vi')
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    # Test 2: Tech news
    print("\n📰 Test 2: Tin công nghệ")
    result2 = fetch_test_news(keywords="công nghệ AI", max_results=3, timelimit='d', region='vn-vi')
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    # Test 3: Sports news
    print("\n📰 Test 3: Tin thể thao")
    result3 = fetch_test_news(keywords="bóng đá", max_results=3, timelimit='d', region='vn-vi')
    print(json.dumps(result3, indent=2, ensure_ascii=False))
    
    # Test 4: International news (English)
    print("\n📰 Test 4: International breaking news")
    result4 = fetch_test_news(keywords="breaking news", max_results=3, timelimit='d', region='en-us')
    print(json.dumps(result4, indent=2, ensure_ascii=False))
    
    print("\n" + "="*70)
    print("All tests completed!")
    print("="*70)

if __name__ == "__main__":
    try:
        test_news_service()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError during testing: {e}")
        import traceback
        traceback.print_exc()
