#!/usr/bin/env python3
"""Fetch latest news from multiple RSS sources - sorted by newest"""
import json
import sys
sys.path.insert(0, '.')

try:
    import feedparser
    
    feeds = {
        'Bloomberg': 'https://www.bloombergtechnoz.com/rss',
        'CNBC': 'https://www.cnbcindonesia.com/market/rss',
        'Kontan': 'https://kontan.co.id/rss/market',
        'Bisnis': 'https://rss.bisnis.com/bisnis-finansial',
        'Detik': 'https://rss.detik.com/finance',
    }
    
    all_headlines = []
    seen_titles = set()
    
    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:  # Top 5 per source
                title = entry.title.strip()
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    all_headlines.append({
                        'source': source,
                        'title': title,
                        'link': entry.link,
                        'published': entry.get('published', '')
                    })
        except:
            pass
    
    # Sort by published date (newest first)
    all_headlines.sort(key=lambda x: x.get('published', ''), reverse=True)
    
    # Return top 5 terbaru
    print(json.dumps(all_headlines[:5]))
    
except Exception as e:
    print(json.dumps([]))
