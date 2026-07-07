# Niskala - Sentiment Analyzer (Indonesian Model)
# Version: 2.0.0
# Using IndoBERT-based model for Indonesian financial sentiment

from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import Dict, Optional
import logging


class FinBERTAnalyzer:
    """Sentiment analyzer for Indonesian financial text"""
    
    # Model: IndoBERT fine-tuned for Indonesian sentiment
    # Accuracy: 95.69% on Indonesian text
    # Classes: negatif, netral, positif
    MODEL_NAME = "taufiqdp/indonesian-sentiment"
    
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
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
            Dict with:
                - score: -100 to +100 (negative to positive)
                - label: POSITIVE, NEGATIVE, NEUTRAL
                - positive: 0-1 probability
                - negative: 0-1 probability
                - neutral: 0-1 probability
                - confidence: 0-100
        """
        if not text or not text.strip():
            return self._empty_result()
        
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Model outputs: [negatif, netral, positif]
            # Index 0 = negatif, Index 1 = netral, Index 2 = positif
            negative = probs[0][0].item()
            neutral = probs[0][1].item()
            positive = probs[0][2].item()
            
            # Calculate score (-100 to +100)
            score = int((positive - negative) * 100)
            
            # Determine label
            max_prob = max(positive, negative, neutral)
            if max_prob == positive:
                label = "POSITIVE"
            elif max_prob == negative:
                label = "NEGATIVE"
            else:
                label = "NEUTRAL"
            
            # Confidence
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
        return [self.analyze(text) for text in texts]
    
    def _empty_result(self) -> Dict:
        """Return empty sentiment result"""
        return {
            'score': 0,
            'label': 'NEUTRAL',
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 1.0,
            'confidence': 0
        }


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
