#!/usr/bin/env python3
"""Fetch top 5 real-time news from RSS feeds"""
import json
import sys
sys.path.insert(0, '.')

try:
    import feedparser
    
    feeds = {
        'CNBC': 'https://www.cnbcindonesia.com/market/rss',
        'Kontan': 'https://kontan.co.id/rss/market',
    }
    
    headlines = []
    seen_titles = set()
    
    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.title.strip()
                if title not in seen_titles:
                    seen_titles.add(title)
                    headlines.append({
                        'source': source,
                        'title': title,
                        'link': entry.link,
                        'published': entry.get('published', '')
                    })
                    if len(headlines) >= 5:
                        break
        except:
            pass
    
    print(json.dumps(headlines[:5]))
except Exception as e:
    print(json.dumps([]))
