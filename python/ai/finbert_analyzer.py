# Niskala - Sentiment Analyzer (Indonesian Model)
# Version: 2.1.0
# Using IndoBERT-based model for Indonesian financial sentiment

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, Optional
import logging

from .models.market_impact_model import FinancialMarketImpactModel


class FinBERTAnalyzer:
    """Sentiment analyzer for Indonesian financial text
    
    Supports two model backends:
    - "legacy" (default): taufiqdp/indonesian-sentiment (3-class)
    - "market_impact": Multi-task FinancialMarketImpactModel (6 tasks)
    """
    
    # Model: IndoBERT fine-tuned for Indonesian sentiment
    # Accuracy: 95.69% on Indonesian text
    # Classes: negatif, netral, positif
    MODEL_NAME = "taufiqdp/indonesian-sentiment"
    
    def __init__(self, model_type: str = "legacy", model_dir: Optional[str] = None):
        self.tokenizer = None
        self.model = None
        self.model_type = model_type
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if model_type == "market_impact":
            if not model_dir:
                model_dir = "indobert-financial/models/indobert-market-impact-v1/"
            self.market_model = FinancialMarketImpactModel(model_dir)
            logging.info(f"FinBERTAnalyzer using market_impact model from {model_dir}")
        else:
            self.market_model = None
            self._load_model()
        
    def _load_model(self):
        """Load Indonesian sentiment model and tokenizer"""
        try:
            logging.info(f"Loading Indonesian sentiment model on {self.device}...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.MODEL_NAME
            )
            self.model.to(self.device)
            self.model.eval()
            logging.info("Indonesian sentiment model loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load sentiment model: {e}")
            raise
    
    def analyze(self, text: str) -> Dict:
        """Analyze sentiment of Indonesian text

        Args:
            text: Indonesian text to analyze (news headline, summary, etc.)

        Returns:
            Dict with sentiment analysis results.
            Legacy mode: score, label, positive, negative, neutral, confidence
            Market impact mode: + sentiment, event, impact, time_horizon, entities, relations
        """
        if not text or not text.strip():
            return self._empty_result()

        if self.model_type == "market_impact":
            return self.market_model.analyze(text)

        try:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

            negative = probs[0][0].item()
            neutral = probs[0][1].item()
            positive = probs[0][2].item()

            score = int((positive - negative) * 100)

            max_prob = max(positive, negative, neutral)
            if max_prob == positive:
                label = "POSITIVE"
            elif max_prob == negative:
                label = "NEGATIVE"
            else:
                label = "NEUTRAL"

            confidence = int(max_prob * 100)

            return {
                'score': score,
                'label': label,
                'positive': positive,
                'negative': negative,
                'neutral': neutral,
                'confidence': confidence
            }

        except Exception as e:
            logging.error(f"Sentiment analysis error: {e}")
            return self._empty_result()
    
    def analyze_batch(self, texts: list) -> list:
        """Analyze multiple texts at once
        
        Args:
            texts: List of Indonesian texts
            
        Returns:
            List of sentiment dicts
        """
        if self.model_type == "market_impact":
            return self.market_model.analyze_batch(texts)
        return [self.analyze(text) for text in texts]
    
    def _empty_result(self) -> Dict:
        """Return empty sentiment result"""
        base = {
            'score': 0,
            'label': 'NEUTRAL',
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 1.0,
            'confidence': 0,
        }
        if self.model_type == "market_impact":
            base.update({
                'sentiment': 'Neutral',
                'event': [],
                'impact': 'Neutral',
                'time_horizon': 'Swing',
                'entities': [],
                'relations': [],
            })
        return base


# Test function
if __name__ == '__main__':
    analyzer = FinBERTAnalyzer()
    
    # Test cases (Indonesian financial news)
    test_texts = [
        "Bank BCA melaporkan laba bersih Q2 naik 15%, melebihi ekspektasi",
        "Pasar saham anjlok karena kekhawatiran resesi global",
        "Perusahaan mengumumkan pembagian dividen",
        "IHSG ditutup menguat 0.5% di tengah sentimen positif",
        "Saham GOTO merosot 10% setelah pengumuman PHK",
    ]
    
    print("=== Indonesian Sentiment Analysis ===\n")
    
    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"Text: {text}")
        print(f"Score: {result['score']:+d} | Label: {result['label']} | Confidence: {result['confidence']}%")
        print()
