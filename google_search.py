# google_search.py
from fastmcp import FastMCP
import sys
import logging
from ddgs import DDGS

# Configure logging with detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('GoogleSearch')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')

logger.info('='*60)
logger.info('Google Search MCP Service Starting...')
logger.info('='*60)

# Create an MCP server
mcp = FastMCP("GoogleSearch")

def perform_web_search(query: str, num_results: int = 5, region: str = 'vn-vi'):
    """
    Perform web search using DuckDuckGo (reliable and fast)
    
    Args:
        query: Search query
        num_results: Number of results to return
        region: Region code (e.g., 'vn-vi' for Vietnam, 'us-en' for US)
    """
    try:
        logger.info(f"🔎 Initiating DuckDuckGo search...")
        logger.info(f"🌍 Region: {region}")
        search_results = []
        
        # Use DuckDuckGo Search with new API
        logger.info(f"📡 Connecting to search API...")
        ddgs = DDGS()
        
        logger.info(f"🔍 Executing search query: '{query}'")
        results = list(ddgs.text(query, region=region, max_results=num_results))
        
        logger.info(f"📊 Raw API returned {len(results)} results")
        
        if not results:
            logger.warning(f"⚠️  API returned empty results list")
            logger.warning(f"   This might be due to rate limiting or query restrictions")
        
        for idx, result in enumerate(results, start=1):
            # Log raw result structure for debugging
            logger.info(f"📋 Result {idx} keys: {list(result.keys())}")
            
            title = result.get('title', 'No title')
            # Try multiple possible URL fields
            url = result.get('href') or result.get('link') or result.get('url', '')
            body = result.get('body') or result.get('description') or result.get('snippet', '')
            
            logger.info(f"  ✓ [{idx}] {title[:60]}...")
            logger.info(f"       URL: {url[:80]}...")
            
            search_results.append({
                "rank": idx,
                "title": title,
                "url": url,
                "snippet": body[:200] + "..." if len(body) > 200 else body
            })
        
        logger.info(f"✅ Parsed {len(search_results)} results successfully")
        return search_results
        
    except Exception as e:
        logger.error(f"❌ Error during web search: {e}")
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise

@mcp.tool()
def search_google(query: str, num_results: int = 5, lang: str = "vi") -> dict:
    """
    Search the web and return top results. Uses DuckDuckGo for reliability.
    
    Args:
        query: Search query string (in any language)
        num_results: Number of results to return (default: 5, max: 10)
        lang: Language/region code (vi=Vietnam, en=US, ja=Japan, ko=Korea, etc.)
    
    Returns:
        dict with success status and list of search results (title, URL, snippet)
    
    Example response:
        {
            "success": true,
            "query": "Python programming",
            "total_results": 5,
            "results": [
                {
                    "rank": 1,
                    "title": "Python.org",
                    "url": "https://www.python.org/",
                    "snippet": "Official Python website..."
                }
            ]
        }
    """
    try:
        logger.info('='*60)
        logger.info(f"🔍 NEW SEARCH REQUEST RECEIVED")
        logger.info(f"Query: '{query}'")
        logger.info(f"Requested results: {num_results}")
        logger.info(f"Language: {lang}")
        
        # Map language to DuckDuckGo region codes
        region_map = {
            'vi': 'vn-vi',  # Vietnam
            'en': 'us-en',  # United States
            'ja': 'jp-jp',  # Japan
            'ko': 'kr-kr',  # Korea
            'zh': 'cn-zh',  # China
            'fr': 'fr-fr',  # France
            'de': 'de-de',  # Germany
            'es': 'es-es',  # Spain
            'th': 'th-th',  # Thailand
        }
        region = region_map.get(lang, 'wt-wt')  # Default to worldwide if unknown
        logger.info(f"🌍 Using region: {region}")
        
        # Limit num_results to prevent abuse
        num_results = min(max(1, num_results), 10)
        if num_results != min(max(1, num_results), 10):
            logger.warning(f"num_results adjusted from original to {num_results}")
        
        logger.info(f"⏳ Starting web search...")
        
        # Perform web search with region
        search_results = perform_web_search(query, num_results, region)
            
        logger.info(f"✅ Search completed successfully!")
        logger.info(f"Found {len(search_results)} results for query: '{query}'")
        
        # Log first result as sample
        if search_results:
            logger.info(f"Top result: {search_results[0]['title'][:50]}...")
        
        logger.info('='*60)
        
        return {
            "success": True,
            "query": query,
            "total_results": len(search_results),
            "results": search_results
        }
        
    except Exception as e:
        error_msg = f"Error searching: {str(e)}"
        logger.error('='*60)
        logger.error(f"❌ SEARCH FAILED")
        logger.error(f"Query: '{query}'")
        logger.error(f"Error: {error_msg}")
        logger.error('='*60)
        return {
            "success": False,
            "error": error_msg,
            "query": query,
            "results": []
        }

# Start the server
if __name__ == "__main__":
    logger.info("🚀 Starting MCP server with stdio transport...")
    logger.info("📡 Server is ready to receive requests from MCP clients")
    logger.info("💡 Available tools: search_google")
    logger.info("Waiting for requests...\n")
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("\n🛑 Server stopped by user")
    except Exception as e:
        logger.error(f"\n❌ Server error: {e}")
        raise
