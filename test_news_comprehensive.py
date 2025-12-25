#!/usr/bin/env python3
"""
Final comprehensive test for news service
Tests both Vietnamese keywords and international Vietnam news
"""

import sys
sys.path.insert(0, '.')

from news_service import fetch_latest_news
from datetime import datetime

def main():
    print("\n" + "="*85)
    print(" 📰 NEWS SERVICE - COMPREHENSIVE TEST")
    print("="*85 + "\n")
    
    test_cases = [
        {
            "keywords": None,
            "max_results": 6,
            "desc": "Latest Vietnam News (International Sources)",
            "note": "Reuters, Bloomberg, VnExpress International, etc."
        },
        {
            "keywords": "công nghệ",
            "max_results": 6,
            "desc": "Technology News (Vietnamese Sources)",
            "note": "VnExpress, Dân Trí, Báo Mới, VnEconomy, etc."
        },
        {
            "keywords": "kinh tế",
            "max_results": 5,
            "desc": "Economic News (Vietnamese Sources)",
            "note": "VnEconomy, Dân Trí, Báo Mới, etc."
        },
        {
            "keywords": "thể thao",
            "max_results": 5,
            "desc": "Sports News",
            "note": "Mixed sources"
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"{'─'*85}")
        print(f"Test {i}: {test['desc']}")
        print(f"Keywords: {test['keywords'] if test['keywords'] else 'None (default)'}")
        print(f"Expected: {test['note']}")
        print(f"{'─'*85}")
        
        result = fetch_latest_news(
            keywords=test['keywords'],
            max_results=test['max_results'],
            timelimit='d'
        )
        
        if not result:
            print("❌ No results found\n")
            continue
        
        print(f"\n✅ Found {len(result)} articles")
        
        # Count Vietnamese sources
        vn_count = 0
        for article in result:
            url = article['url'].lower()
            if any(s in url for s in ['vnexpress', 'dantri', 'tuoitre', 'baomoi', 
                                      'tienphong', 'vietnamnet', 'vneconomy', 'thanhnien']):
                vn_count += 1
        
        print(f"📊 Vietnamese sources: {vn_count}/{len(result)}\n")
        
        # Show first 4 articles
        for article in result[:4]:
            url = article['url'].lower()
            is_vn = any(s in url for s in ['vnexpress', 'dantri', 'tuoitre', 'baomoi', 
                                           'tienphong', 'vietnamnet', 'vneconomy', 'thanhnien'])
            
            date_str = article['date']
            try:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_display = dt.strftime('%d/%m %H:%M')
            except:
                date_display = date_str[:10] if date_str else 'N/A'
            
            marker = '🇻🇳' if is_vn else '🌐'
            print(f"  {marker} {article['title'][:65]}")
            print(f"     📰 {article['source']} | 📅 {date_display}")
        
        if len(result) > 4:
            print(f"\n  ... and {len(result) - 4} more articles")
        
        print()
    
    print("="*85)
    print(" ✅ ALL TESTS COMPLETED!")
    print(" 💡 Tip: Use Vietnamese keywords (công nghệ, kinh tế) for local news")
    print(" 💡 Tip: Use keywords=None for international Vietnam news")
    print("="*85 + "\n")

if __name__ == "__main__":
    main()
