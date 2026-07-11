#!/usr/bin/env python3
"""Fetch real-time news from RSS feeds"""
import json
import sys
sys.path.insert(0, '.')

try:
    import feedparser
    
    feeds = {
        'CNBC': 'https://www.cnbcindonesia.com/market/rss',
        'Kontan': 'https://kontan.co.id/rss/market',
        'Reuters': 'https://www.reuters.com/markets/asia/rss'
    }
    
    headlines = []
    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:3]:  # Top 3 per source
                headlines.append({
                    'source': source,
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.get('published', '')
                })
        except:
            pass
    
    print(json.dumps(headlines[:10]))  # Top 10 headlines
except Exception as e:
    print(json.dumps([]))
