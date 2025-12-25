#!/usr/bin/env python3
"""
Test script for Web Search MCP service
Quick test without needing full MCP infrastructure
"""

import json
import logging
from ddgs import DDGS

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('WebSearchTest')

def perform_web_search(query: str, num_results: int = 5, region: str = 'vn-vi'):
    """
    Perform web search using DuckDuckGo (reliable and fast)
    
    Args:
        query: Search query
        num_results: Number of results
        region: Region code (e.g., 'vn-vi' for Vietnam)
    """
    try:
        search_results = []
        
        # Use DuckDuckGo Search with new API
        ddgs = DDGS()
        results = list(ddgs.text(query, region=region, max_results=num_results))
        
        for idx, result in enumerate(results, start=1):
            search_results.append({
                "rank": idx,
                "title": result.get('title', 'No title'),
                "url": result.get('href') or result.get('link') or result.get('url', ''),
                "snippet": (result.get('body') or result.get('description', ''))[:200] + "..." if len(result.get('body', '')) > 200 else (result.get('body') or result.get('description', ''))
            })
        
        return search_results
        
    except Exception as e:
        logger.error(f"Error during web search: {e}")
        raise

def test_search_function(query: str, num_results: int = 5, region: str = 'vn-vi'):
    """
    Test the search functionality directly
    """
    try:
        logger.info(f"Searching for: '{query}' (num_results={num_results}, region={region})")
        
        search_results = perform_web_search(query, num_results, region)
            
        logger.info(f"Found {len(search_results)} results for query: '{query}'")
        
        return {
            "success": True,
            "query": query,
            "total_results": len(search_results),
            "results": search_results
        }
        
    except Exception as e:
        error_msg = f"Error searching: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "query": query,
            "results": []
        }

def test_web_search():
    """Test the web search function"""
    
    print("="*60)
    print("Testing Web Search MCP Service (via DuckDuckGo)")
    print("="*60)
    
    # Test 1: Basic search
    print("\n[Test 1] Search: 'Python programming'")
    result1 = test_search_function("Python programming", num_results=3)
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    # Test 2: Tech search
    print("\n[Test 2] Search: 'ESP32 tutorial'")
    result2 = test_search_function("ESP32 tutorial", num_results=3)
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    # Test 3: Vietnamese search
    print("\n[Test 3] Vietnamese search: 'học machine learning'")
    result3 = test_search_function("học machine learning", num_results=3)
    print(json.dumps(result3, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60)

if __name__ == "__main__":
    try:
        test_web_search()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\nError during testing: {e}")
        import traceback
        traceback.print_exc()
