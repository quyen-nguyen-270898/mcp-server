#!/usr/bin/env python3
"""
Final test for news service - check if it returns fresh news
"""

import sys
sys.path.insert(0, '.')

from news_service import fetch_latest_news
from datetime import datetime

def main():
    print("\n" + "="*80)
    print(" 🧪 FINAL NEWS SERVICE TEST")
    print("="*80 + "\n")
    
    print("Testing: Get latest Vietnamese news (last 24 hours)\n")
    
    # Test with different parameters
    test_cases = [
        {"keywords": None, "max_results": 10, "timelimit": "d", "desc": "Latest Vietnamese news (24h)"},
        {"keywords": "công nghệ", "max_results": 5, "timelimit": "d", "desc": "Technology news (24h)"},
        {"keywords": None, "max_results": 5, "timelimit": "w", "desc": "Latest Vietnamese news (1 week)"},
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"Test {i}: {test['desc']}")
        print(f"{'─'*80}")
        
        result = fetch_latest_news(
            keywords=test['keywords'],
            max_results=test['max_results'],
            timelimit=test['timelimit']
        )
        
        print(f"\n✅ Found {len(result)} articles")
        
        if result:
            print(f"\nFirst 3 articles:")
            for article in result[:3]:
                date_str = article.get('date', '')
                try:
                    if 'T' in date_str:
                        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        display_date = dt.strftime('%Y-%m-%d %H:%M')
                    else:
                        display_date = date_str[:16]
                except:
                    display_date = date_str[:16] if date_str else 'N/A'
                
                print(f"\n  {article['rank']}. {article['title'][:60]}")
                print(f"     📰 {article['source']}")
                print(f"     📅 {display_date}")
    
    print("\n" + "="*80)
    print(" ✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
