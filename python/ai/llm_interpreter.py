# Niskala - LLM Interpreter
# Version: 1.0.0

import openai
import anthropic
from typing import Dict, Optional
import logging
import os


class LLMInterpreter:
    """LLM-based news interpretation and analysis"""
    
    def __init__(self, provider: str = "openai"):
        """Initialize LLM client
        
        Args:
            provider: 'openai' or 'anthropic'
        """
        self.provider = provider
        self.openai_client = None
        self.anthropic_client = None
        
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.anthropic_client = anthropic.Anthropic(api_key=api_key)
    
    def interpret(self, title: str, summary: str, finbert_score: int) -> Dict:
        """Interpret financial news using LLM
        
        Args:
            title: News title
            summary: News summary
            finbert_score: FinBERT sentiment score (-100 to +100)
            
        Returns:
            Dict with:
                - interpretation: Text explanation
                - sectors: List of affected sectors
                - tickers: List of affected tickers
                - impact: POSITIVE, NEGATIVE, NEUTRAL
                - confidence: 0-100
                - timeframe: short/medium/long term
                - risk: low/medium/high
        """
        text = f"{title} {summary}"
        if not text or not text.strip():
            return self._empty_result()
        
        try:
            prompt = self._build_prompt(text, finbert_score)
            
            if self.provider == "openai" and self.openai_client:
                return self._interpret_openai(prompt)
            elif self.provider == "anthropic" and self.anthropic_client:
                return self._interpret_anthropic(prompt)
            else:
                logging.warning("No LLM client available, using fallback")
                return self._fallback_interpretation(text)
                
        except Exception as e:
            logging.error(f"LLM interpretation error: {e}")
            return self._empty_result()
    
    def _build_prompt(self, text: str, finbert_score: int) -> str:
        """Build prompt for LLM"""
        prompt = f"""Analyze this Indonesian stock market news:

News: {text}
FinBERT Score: {finbert_score} (-100 to +100)

Provide:
1. Brief interpretation (why this matters)
2. Affected sectors (Banking, Mining, Tech, etc.)
3. Affected IDX stock tickers (BBCA, BBRI, TLKM, etc.)
4. Overall impact (POSITIVE, NEGATIVE, NEUTRAL)
5. Confidence level (0-100)
6. Timeframe (short-term 1-5d, medium-term 1-4w, long-term 1-6m)
7. Risk assessment (low, medium, high)

Respond ONLY with valid JSON:
{{
    "interpretation": "Brief explanation of why this matters",
    "sectors": ["Banking", "..."],
    "tickers": ["BBCA", "..."],
    "impact": "POSITIVE",
    "confidence": 85,
    "timeframe": "short-term",
    "risk": "low"
}}"""
        return prompt
    
    def _interpret_openai(self, prompt: str) -> Dict:
        """Interpret using OpenAI GPT"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a financial analyst specializing in Indonesian stock market."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            # Parse JSON response
            import json
            result = json.loads(content)
            return result
            
        except Exception as e:
            logging.error(f"OpenAI error: {e}")
            return self._empty_result()
    
    def _interpret_anthropic(self, prompt: str) -> Dict:
        """Interpret using Anthropic Claude"""
        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = message.content[0].text
            # Parse JSON response
            import json
            result = json.loads(content)
            return result
            
        except Exception as e:
            logging.error(f"Anthropic error: {e}")
            return self._empty_result()
    
    def _fallback_interpretation(self, text: str) -> Dict:
        """Simple rule-based fallback when no LLM available"""
        # Simple keyword matching
        sectors = []
        tickers = []
        
        text_lower = text.lower()
        
        # Detect sectors
        if any(word in text_lower for word in ['bank', 'bca', 'bri', 'bni']):
            sectors.append('Banking')
        if any(word in text_lower for word in ['mining', 'coal', 'adro', 'itmg']):
            sectors.append('Mining')
        if any(word in text_lower for word in ['telecom', 'tlkm', 'isat']):
            sectors.append('Telecommunications')
        
        # Detect tickers (uppercase words 4 chars)
        import re
        potential_tickers = re.findall(r'\b[A-Z]{4}\b', text)
        tickers.extend(potential_tickers)
        
        # Determine impact based on keywords
        positive_words = ['naik', 'rally', 'gain', 'profit', 'growth', 'bullish']
        negative_words = ['turun', 'crash', 'loss', 'decline', 'bearish']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            impact = "POSITIVE"
        elif neg_count > pos_count:
            impact = "NEGATIVE"
        else:
            impact = "NEUTRAL"
        
        return {
            'interpretation': f"Rule-based analysis: {impact} sentiment detected",
            'sectors': sectors,
            'tickers': list(set(tickers)),
            'impact': impact,
            'confidence': 50
        }
    
    def _empty_result(self) -> Dict:
        """Return empty result"""
        return {
            'interpretation': '',
            'sectors': [],
            'tickers': [],
            'impact': 'NEUTRAL',
            'confidence': 0,
            'timeframe': 'short-term',
            'risk': 'low'
        }


# Test function
if __name__ == '__main__':
    interpreter = LLMInterpreter(provider="openai")
    
    text = "Bank BCA melaporkan laba bersih naik 15% di Q2 2024"
    result = interpreter.interpret(text)
    
    print("Interpretation:", result['interpretation'])
    print("Sectors:", result['sectors'])
    print("Tickers:", result['tickers'])
    print("Impact:", result['impact'])
