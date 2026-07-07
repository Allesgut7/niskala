# Niskala - AI Sentiment Pipeline
# Version: 2.0.0
# Integrates Indonesian Sentiment Model, LLM, News Scraper, and Impact Mapping

from typing import Dict, List, Optional
import logging
from datetime import datetime
import time

from .finbert_analyzer import FinBERTAnalyzer
from .llm_interpreter import LLMInterpreter
from .news_scraper import NewsCollector


class SentimentPipeline:
    """Full AI sentiment analysis pipeline"""
    
    def __init__(self, use_llm: bool = True):
        """Initialize pipeline
        
        Args:
            use_llm: Enable LLM interpretation (requires API key)
        """
        self.finbert = FinBERTAnalyzer()
        self.news_collector = NewsCollector()
        self.use_llm = use_llm
        
        if use_llm:
            self.llm = LLMInterpreter()
        else:
            self.llm = None
        
        self.sector_mapper = SectorMapper()
        self.impact_calculator = ImpactCalculator()
        
        logging.info("Sentiment pipeline initialized")
    
    def analyze_news_batch(self, limit: int = 50) -> List[Dict]:
        """Fetch and analyze news batch
        
        Args:
            limit: Max articles to fetch
            
        Returns:
            List of analyzed news with sentiment
        """
        # Fetch news
        logging.info(f"Fetching {limit} news articles...")
        articles = self.news_collector.fetch_news(limit=limit)
        
        if not articles:
            logging.warning("No articles fetched")
            return []
        
        # Analyze sentiment with FinBERT
        logging.info(f"Analyzing sentiment for {len(articles)} articles...")
        for article in articles:
            text = f"{article['title']} {article['summary']}"
            sentiment = self.finbert.analyze(text)
            
            article['sentiment_score'] = sentiment['score']
            article['sentiment_label'] = sentiment['label']
            article['sentiment_confidence'] = sentiment['confidence']
            article['sentiment_probs'] = {
                'positive': sentiment['positive'],
                'negative': sentiment['negative'],
                'neutral': sentiment['neutral']
            }
        
        # LLM interpretation (for high-impact news)
        if self.use_llm and self.llm:
            high_impact = [a for a in articles if abs(a['sentiment_score']) > 50]
            logging.info(f"Running LLM interpretation for {len(high_impact)} high-impact articles...")
            
            for article in high_impact:
                try:
                    interp = self.llm.interpret(
                        article['title'],
                        article['summary'],
                        article['sentiment_score']
                    )
                    article['llm_interpretation'] = interp
                except Exception as e:
                    logging.error(f"LLM interpretation failed: {e}")
                    article['llm_interpretation'] = None
        
        # Calculate impact scores
        logging.info("Calculating impact matrix...")
        for article in articles:
            impact = self.impact_calculator.calculate_impact(article)
            article['impact_scores'] = impact
        
        return articles
    
    def get_sector_sentiment(self, articles: List[Dict]) -> Dict[str, Dict]:
        """Aggregate sentiment by sector
        
        Args:
            articles: List of analyzed articles
            
        Returns:
            Dict mapping sector -> sentiment stats
        """
        sector_sentiments = {}
        
        for article in articles:
            for sector in article.get('sectors', []):
                if sector not in sector_sentiments:
                    sector_sentiments[sector] = {
                        'scores': [],
                        'count': 0,
                        'avg_score': 0,
                        'label': 'NEUTRAL'
                    }
                
                sector_sentiments[sector]['scores'].append(article['sentiment_score'])
                sector_sentiments[sector]['count'] += 1
        
        # Calculate averages
        for sector, data in sector_sentiments.items():
            if data['scores']:
                avg = sum(data['scores']) / len(data['scores'])
                data['avg_score'] = int(avg)
                
                if avg > 20:
                    data['label'] = 'POSITIVE'
                elif avg < -20:
                    data['label'] = 'NEGATIVE'
                else:
                    data['label'] = 'NEUTRAL'
        
        return sector_sentiments
    
    def get_stock_sentiment(self, articles: List[Dict], symbol: str) -> Dict:
        """Get sentiment for specific stock
        
        Args:
            articles: List of analyzed articles
            symbol: Stock ticker (e.g. BBRI)
            
        Returns:
            Sentiment summary for stock
        """
        relevant = [
            a for a in articles
            if symbol in a.get('tickers', [])
        ]
        
        if not relevant:
            return {
                'symbol': symbol,
                'count': 0,
                'avg_score': 0,
                'label': 'NEUTRAL',
                'articles': []
            }
        
        scores = [a['sentiment_score'] for a in relevant]
        avg_score = int(sum(scores) / len(scores))
        
        if avg_score > 20:
            label = 'POSITIVE'
        elif avg_score < -20:
            label = 'NEGATIVE'
        else:
            label = 'NEUTRAL'
        
        return {
            'symbol': symbol,
            'count': len(relevant),
            'avg_score': avg_score,
            'label': label,
            'articles': relevant[:5]  # Top 5 articles
        }


class SectorMapper:
    """Map news to affected sectors and stocks"""
    
    # IDX sector mapping from 05_AI_SENTIMENT.md
    SECTORS = {
        'ENERGY': {
            'keywords': ['minyak', 'oil', 'gas', 'batu bara', 'coal', 'tambang', 'energi'],
            'stocks': ['ADRO', 'PTBA', 'ITMG', 'INDY', 'MEDC']
        },
        'FINANCE': {
            'keywords': ['bank', 'suku bunga', 'interest rate', 'BI Rate', 'kredit', 'deposito'],
            'stocks': ['BBRI', 'BBCA', 'BMRI', 'BBNI', 'BRIS']
        },
        'TECH': {
            'keywords': ['teknologi', 'startup', 'fintech', 'e-commerce', 'digital', 'PHK'],
            'stocks': ['GOTO', 'BUKA', 'EMTK', 'BALI']
        },
        'BASIC': {
            'keywords': ['nickel', 'tembaga', 'emas', 'gold', 'tambang', 'komoditas'],
            'stocks': ['INCO', 'MDKA', 'ANTM', 'BRMS']
        },
        'CONNON': {
            'keywords': ['FMCG', 'makanan', 'minuman', 'rokok', 'consumer'],
            'stocks': ['ICBP', 'UNVR', 'INDF', 'HMSP']
        },
        'CONCYC': {
            'keywords': ['ritel', 'retail', 'mall', 'fashion', 'otomotif'],
            'stocks': ['MAPI', 'LPPF', 'ACES', 'SMSM']
        },
        'HEALTH': {
            'keywords': ['farmasi', 'obat', 'rumah sakit', 'healthcare', 'vaksin'],
            'stocks': ['SIDO', 'KLBF', 'MIKA', 'HEAL']
        },
        'PROPERT': {
            'keywords': ['properti', 'real estate', 'perumahan', 'apartemen', 'REIT'],
            'stocks': ['BSDE', 'CTRA', 'SMRA', 'PWON']
        },
        'INFRA': {
            'keywords': ['telekomunikasi', 'tower', 'infrastruktur', 'tol', 'listrik'],
            'stocks': ['TLKM', 'TOWR', 'TBIG', 'JSMR']
        },
        'TRANS': {
            'keywords': ['penerbangan', 'logistik', 'shipping', 'kurir', 'transportasi'],
            'stocks': ['BIRD', 'CITA', 'ASSA', 'SMDR']
        },
        'INDUST': {
            'keywords': ['industri', 'manufaktur', 'semen', 'konstruksi'],
            'stocks': ['ASII', 'UNTR', 'SMGR', 'GJTL']
        }
    }
    
    def detect_sectors(self, text: str) -> List[str]:
        """Detect affected sectors from text"""
        text_lower = text.lower()
        detected = []
        
        for sector, info in self.SECTORS.items():
            if any(kw in text_lower for kw in info['keywords']):
                detected.append(sector)
        
        return detected
    
    def get_sector_stocks(self, sector: str) -> List[str]:
        """Get stocks in sector"""
        return self.SECTORS.get(sector, {}).get('stocks', [])


class ImpactCalculator:
    """Calculate per-stock impact scores from news"""
    
    def __init__(self):
        self.sector_mapper = SectorMapper()
    
    def calculate_impact(self, article: Dict) -> Dict[str, int]:
        """Calculate impact score for each affected stock
        
        Args:
            article: News article with sentiment
            
        Returns:
            Dict mapping symbol -> impact score (-100 to +100)
        """
        impacts = {}
        base_score = article.get('sentiment_score', 0)
        
        # Direct mention (100% impact)
        for ticker in article.get('tickers', []):
            impacts[ticker] = base_score
        
        # Sector-wide impact (50% impact)
        for sector in article.get('sectors', []):
            sector_stocks = self.sector_mapper.get_sector_stocks(sector)
            for stock in sector_stocks:
                if stock not in impacts:  # Don't override direct mentions
                    impacts[stock] = int(base_score * 0.5)
        
        return impacts


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Test pipeline
    pipeline = SentimentPipeline(use_llm=False)
    
    print("Analyzing news batch...")
    articles = pipeline.analyze_news_batch(limit=10)
    
    print(f"\nAnalyzed {len(articles)} articles")
    
    for i, art in enumerate(articles[:5]):
        print(f"\n[{i+1}] {art['title'][:80]}")
        print(f"    Score: {art['sentiment_score']:+d} ({art['sentiment_label']})")
        print(f"    Confidence: {art['sentiment_confidence']}%")
        if art.get('tickers'):
            print(f"    Tickers: {', '.join(art['tickers'])}")
        if art.get('sectors'):
            print(f"    Sectors: {', '.join(art['sectors'])}")
    
    # Sector sentiment
    print("\n\nSector Sentiment:")
    sector_sent = pipeline.get_sector_sentiment(articles)
    for sector, data in sorted(sector_sent.items(), key=lambda x: x[1]['avg_score'], reverse=True):
        print(f"  {sector:12s}: {data['avg_score']:+4d} ({data['label']}) - {data['count']} articles")
