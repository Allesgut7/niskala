# Niskala - Sentiment Client for C++ Integration
# Version: 1.0.0

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from typing import List, Dict
from ai.sentiment_pipeline import SentimentPipeline


class SentimentClient:
    """Wrapper for sentiment pipeline accessible from C++"""
    
    def __init__(self, use_llm: bool = False):
        """Initialize sentiment client
        
        Args:
            use_llm: Enable LLM (requires API key, disabled by default)
        """
        self.pipeline = SentimentPipeline(use_llm=use_llm)
        self.cached_articles = []
    
    def fetch_news(self, limit: int = 20) -> List[Dict]:
        """Fetch and analyze news with sentiment
        
        Args:
            limit: Number of articles to fetch
            
        Returns:
            List of dicts with keys:
            - source: str
            - title: str
            - summary: str
            - sentiment_score: int (-100 to +100)
            - sentiment_label: str (positive/negative/neutral)
            - tickers: List[str] (affected stocks)
            - sectors: List[str] (affected sectors)
            - impact_scores: Dict[str, int] (stock -> impact)
        """
        try:
            articles = self.pipeline.analyze_news_batch(limit=limit)
            self.cached_articles = articles
            
            # Format for C++ consumption
            results = []
            for art in articles:
                results.append({
                    'source': art.get('source', 'Unknown'),
                    'title': art.get('title', ''),
                    'summary': art.get('summary', ''),
                    'sentiment_score': art.get('sentiment_score', 0),
                    'sentiment_label': art.get('sentiment_label', 'neutral'),
                    'tickers': art.get('tickers', []),
                    'sectors': art.get('sectors', []),
                    'impact_scores': art.get('impact_scores', {})
                })
            
            return results
            
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    def get_cached_news(self) -> List[Dict]:
        """Get cached news without refetching"""
        return self.cached_articles


# Test
if __name__ == '__main__':
    client = SentimentClient(use_llm=False)
    news = client.fetch_news(limit=5)
    
    print(f"Fetched {len(news)} articles\n")
    
    for i, article in enumerate(news):
        print(f"[{i+1}] {article['source']} - {article['title'][:60]}")
        print(f"    Sentiment: {article['sentiment_label']} ({article['sentiment_score']:+d})")
        if article['tickers']:
            print(f"    Stocks: {', '.join(article['tickers'][:5])}")
        print()
