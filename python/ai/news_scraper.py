# Niskala - News RSS Collector
# Version: 1.0.0

import feedparser
import requests
from typing import Dict, List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import re
import logging


class NewsCollector:
    """RSS news collector for Indonesian financial news sources"""
    
    # RSS feeds for Indonesian financial news
    RSS_FEEDS = {
        'CNBC ID': {
            'url': 'https://www.cnbcindonesia.com/market/rss',
            'category': 'market',
            'language': 'id'
        },
        'Kontan': {
            'url': 'https://www.kontan.co.id/rss/idx',
            'category': 'idx',
            'language': 'id'
        },
        'IDX Channel': {
            'url': 'https://www.idxchannel.com/rss',
            'category': 'idx',
            'language': 'id'
        },
        'ANTARA': {
            'url': 'https://www.antaranews.com/rss/ekonomi',
            'category': 'economy',
            'language': 'id'
        },
        'Bisnis': {
            'url': 'https://www.bisnis.com/rss',
            'category': 'business',
            'language': 'id'
        },
        'Yahoo Finance': {
            'url': 'https://feeds.finance.yahoo.com/rss/2.0/headline?s=^JKSE&region=US&lang=en-US',
            'category': 'market',
            'language': 'en'
        },
    }
    
    IPO_KEYWORDS = [
        'ipo', 'initial public offering', 'go public',
        'tercatat di bursa', 'peluncuran saham',
        'saham baru', 'penawaran umum perdana', 'right issue',
        'saham berhak', 'corporate action', 'efek baru',
        'emas baru', 'pencatatan saham',
    ]

    DELISTING_KEYWORDS = [
        'delisting', 'penghapusan saham', 'suspensi', 'suspended',
        'ditangguhkan', 'dicabut', 'pencatatan ditutup',
        'dihentikan perdagangannya',
    ]

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.sector_keywords = self._build_sector_keywords()
    
    def fetch_news(self, source: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Fetch news from RSS feeds
        
        Args:
            source: Specific source name, or None for all
            limit: Max articles per source
            
        Returns:
            List of news dicts
        """
        articles = []
        
        feeds_to_fetch = {}
        if source:
            if source in self.RSS_FEEDS:
                feeds_to_fetch[source] = self.RSS_FEEDS[source]
        else:
            feeds_to_fetch = self.RSS_FEEDS
        
        for src_name, src_info in feeds_to_fetch.items():
            try:
                fetched = self._fetch_feed(src_name, src_info, limit)
                articles.extend(fetched)
            except Exception as e:
                logging.warning(f"Failed to fetch {src_name}: {e}")
        
        # Sort by timestamp (newest first)
        articles.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return articles
    
    def _fetch_feed(self, src_name: str, src_info: Dict, limit: int) -> List[Dict]:
        """Fetch a single RSS feed"""
        try:
            feed = feedparser.parse(src_info['url'])
            articles = []
            
            for entry in feed.entries[:limit]:
                # Extract title and summary
                title = self._clean_text(entry.get('title', ''))
                summary = self._clean_text(entry.get('summary', entry.get('description', '')))
                
                # Detect affected sectors and tickers
                sectors = self._detect_sectors(title + ' ' + summary)
                tickers = self._detect_tickers(title + ' ' + summary)
                
                article = {
                    'title': title,
                    'summary': summary[:200],
                    'source': src_name,
                    'url': entry.get('link', ''),
                    'timestamp': self._parse_date(entry),
                    'sectors': sectors,
                    'tickers': tickers,
                    'corporate_actions': self._detect_corporate_actions(title + ' ' + summary),
                    'category': src_info.get('category', ''),
                    'language': src_info.get('language', 'en'),
                    'sentiment_score': 0,
                    'sentiment_label': 'NEUTRAL'
                }
                
                articles.append(article)
            
            logging.info(f"Fetched {len(articles)} articles from {src_name}")
            return articles
            
        except Exception as e:
            logging.error(f"Error fetching {src_name}: {e}")
            return []
    
    def _clean_text(self, html: str) -> str:
        """Remove HTML tags and clean text"""
        if not html:
            return ''
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _parse_date(self, entry) -> str:
        """Parse entry date to ISO format"""
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                dt = datetime(*entry.published_parsed[:6])
                return dt.isoformat()
            except Exception:
                pass
        return datetime.now().isoformat()
    
    def _detect_sectors(self, text: str) -> List[str]:
        """Detect mentioned sectors"""
        sectors = []
        text_lower = text.lower()
        
        for sector, keywords in self.sector_keywords.items():
            if any(kw in text_lower for kw in keywords):
                sectors.append(sector)
        
        return sectors
    
    def _detect_tickers(self, text: str) -> List[str]:
        """Detect mentioned stock tickers"""
        # IDX tickers are 4 uppercase letters
        potential = re.findall(r'\b[A-Z]{4}\b', text)
        
        # Common IDX tickers
        known_tickers = {
            'BBCA', 'BBRI', 'BMRI', 'BBNI', 'TLKM', 'GOTO', 'ADRO',
            'UNVR', 'ICBP', 'ASII', 'PGAS', 'ANTM', 'INCO', 'MDKA',
            'EMTK', 'BUKA', 'ISSP', 'ISAT', 'EXCL', 'FREN'
        }
        
        return [t for t in potential if t in known_tickers]
    
    def _detect_corporate_actions(self, text: str) -> List[str]:
        """Detect IPO or delisting mentions in text"""
        text_lower = text.lower()
        actions = []

        if any(kw in text_lower for kw in self.IPO_KEYWORDS):
            actions.append('IPO')

        if any(kw in text_lower for kw in self.DELISTING_KEYWORDS):
            actions.append('DELISTING')

        return actions

    def _build_sector_keywords(self) -> Dict[str, List[str]]:
        """Build sector keyword mapping"""
        return {
            'Banking': ['bank', 'bca', 'bri', 'bn', 'bmri', 'kredit', 'deposito'],
            'Mining': ['tambang', 'mining', 'batu bara', 'coal', 'nikel', 'timah'],
            'Telecommunications': ['telekomunikasi', 'telecom', 'seluler', 'fiber'],
            'Consumer': ['konsumen', 'consumer', 'fmcg', 'makanan', 'minuman'],
            'Infrastructure': ['infrastruktur', 'jalan tol', 'bandara', 'pelabuhan'],
            'Property': ['properti', 'real estate', 'apartemen', 'perumahan'],
            'Energy': ['energi', 'minyak', 'gas', 'oil', 'renewable'],
            'Technology': ['teknologi', 'digital', 'fintech', 'e-commerce'],
            'Agriculture': ['pertanian', 'sawit', 'kelapa sawit', 'CPO'],
            'Automotive': ['otomotif', 'mobil', 'motor', 'kendaraan'],
        }


# Test
if __name__ == '__main__':
    collector = NewsCollector()
    
    print("Fetching news...")
    articles = collector.fetch_news(limit=5)
    
    for i, art in enumerate(articles[:10]):
        print(f"\n[{art['source']}] {art['title'][:80]}")
        if art['sectors']:
            print(f"  Sectors: {', '.join(art['sectors'])}")
        if art['tickers']:
            print(f"  Tickers: {', '.join(art['tickers'])}")
