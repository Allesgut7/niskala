# Niskala - YFinance Data Provider
# Version: 1.0.0

import yfinance as yf
import pandas as pd
import json
import os
import logging
import warnings
from typing import Dict, List, Optional
from datetime import datetime

logging.getLogger("yfinance").setLevel(logging.ERROR)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")


class YFinanceClient:
    """Yahoo Finance data provider for IDX stocks"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 5  # seconds
        
    def get_stock(self, symbol: str) -> Dict:
        """Get stock data for IDX ticker
        
        Args:
            symbol: Stock symbol (e.g., 'BBCA', 'BBRI')
            
        Returns:
            Dict with price, change, volume, etc.
        """
        try:
            # Add .JK suffix for IDX stocks (not for index/forex/commodity symbols)
            if symbol.startswith('^') or symbol.endswith('=X') or '=F' in symbol:
                ticker_symbol = symbol  # Index, forex, or commodity - don't add suffix
            else:
                ticker_symbol = f"{symbol}.JK" if not symbol.endswith('.JK') else symbol
            ticker = yf.Ticker(ticker_symbol)
            
            # Get current info
            info = ticker.info
            
            # Get history for change calculation
            hist = ticker.history(period='2d')
            
            if hist.empty:
                return self._empty_stock_data(symbol)
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            change = current_price - prev_price
            change_pct = (change / prev_price * 100) if prev_price > 0 else 0.0
            
            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'price': float(current_price),
                'change': float(change),
                'changePct': float(change_pct),
                'volume': int(hist['Volume'].iloc[-1]),
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'pe_ratio': info.get('trailingPE', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return self._empty_stock_data(symbol)
    
    def get_stocks_batch(self, symbols: List[str]) -> List[Dict]:
        """Get multiple stocks at once
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            List of stock data dicts
        """
        return [self.get_stock(symbol) for symbol in symbols]
    
    def get_history(self, symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """Get historical data
        
        Args:
            symbol: Stock symbol
            period: Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            if symbol.startswith('^') or symbol.endswith('=X') or '=F' in symbol:
                ticker_symbol = symbol
            else:
                ticker_symbol = f"{symbol}.JK" if not symbol.endswith('.JK') else symbol
            ticker = yf.Ticker(ticker_symbol)
            return ticker.history(period=period, interval=interval)
        except Exception as e:
            print(f"Error fetching history for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_index(self, index_symbol: str) -> Dict:
        """Get index data (IHSG, S&P 500, etc.)
        
        Args:
            index_symbol: Index symbol (^JKSE for IHSG, ^GSPC for S&P 500)
            
        Returns:
            Dict with index data
        """
        try:
            ticker = yf.Ticker(index_symbol)
            hist = ticker.history(period='2d')
            
            if hist.empty:
                return self._empty_stock_data(index_symbol)
            
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
            
            change = current_price - prev_price
            change_pct = (change / prev_price * 100) if prev_price > 0 else 0.0
            
            return {
                'symbol': index_symbol,
                'name': self._get_index_name(index_symbol),
                'price': float(current_price),
                'change': float(change),
                'changePct': float(change_pct),
                'volume': int(hist['Volume'].iloc[-1]),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error fetching index {index_symbol}: {e}")
            return self._empty_stock_data(index_symbol)
    
    def get_commodity(self, commodity_symbol: str) -> Dict:
        """Get commodity price
        
        Args:
            commodity_symbol: Commodity symbol (GC=F for Gold, CL=F for Oil)
            
        Returns:
            Dict with commodity data
        """
        return self.get_index(commodity_symbol)
    
    def get_forex(self, forex_symbol: str) -> Dict:
        """Get forex rate
        
        Args:
            forex_symbol: Forex symbol (USDIDR=X, EURUSD=X)
            
        Returns:
            Dict with forex data
        """
        return self.get_index(forex_symbol)
    
    def _empty_stock_data(self, symbol: str) -> Dict:
        """Return empty stock data structure"""
        return {
            'symbol': symbol,
            'name': symbol,
            'price': 0.0,
            'change': 0.0,
            'changePct': 0.0,
            'volume': 0,
            'market_cap': 0,
            'sector': 'Unknown',
            'pe_ratio': 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def _get_index_name(self, symbol: str) -> str:
        """Get human-readable index name"""
        index_names = {
            '^JKSE': 'IHSG',
            '^GSPC': 'S&P 500',
            '^N225': 'Nikkei 225',
            '^HSI': 'Hang Seng',
            '^KS11': 'KOSPI',
            '^IXIC': 'NASDAQ',
            '^STI': 'STI',
            'GC=F': 'Gold',
            'CL=F': 'Crude Oil',
            'SI=F': 'Silver',
            'USDIDR=X': 'USD/IDR',
            'EURUSD=X': 'EUR/USD'
        }
        return index_names.get(symbol, symbol)
    
    def _load_idx_tickers(self) -> List[str]:
        """Load IDX ticker list from config/idx_tickers.json
        
        Auto-refreshes if file is missing or stale (>30 days).
        Falls back to 10 blue-chips if JSON unavailable.
        """
        json_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'config', 'idx_tickers.json'
        )
        json_path = os.path.normpath(json_path)

        needs_refresh = False
        tickers = []

        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                tickers = data.get('tickers', [])
                last_updated = data.get('last_updated', '')
                if last_updated:
                    age = (datetime.now() - datetime.strptime(last_updated, '%Y-%m-%d')).days
                    if age > 30:
                        needs_refresh = True
            except Exception:
                needs_refresh = True
        else:
            needs_refresh = True

        if needs_refresh:
            logging.info("IDX ticker list stale or missing — refreshing...")
            script = os.path.join(
                os.path.dirname(__file__), '..', 'scripts', 'generate_idx_tickers.py'
            )
            try:
                import subprocess, sys
                subprocess.run([sys.executable, script], timeout=60, capture_output=True)
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                    tickers = data.get('tickers', [])
            except Exception as e:
                logging.warning(f"Ticker refresh failed: {e}")

        if not tickers:
            logging.warning("No tickers loaded — using fallback blue-chips")
            tickers = [f"{t}.JK" for t in
                       ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'GOTO',
                        'ADRO', 'UNVR', 'ICBP', 'ASII', 'PGAS']]

        return tickers

    def get_market_breadth(self) -> Dict:
        """Get market breadth data (advancing/declining stocks)
        
        Downloads IDX tickers in batches of 50 to avoid yfinance overload.
        Falls back to per-ticker download per batch, then to 10 blue-chips + scaling.
        """
        BATCH_SIZE = 50

        tickers = self._load_idx_tickers()
        if not tickers:
            logging.warning("No tickers available — falling back to sample")
            return self._get_breadth_fallback()

        logging.info(f"Fetching breadth for {len(tickers)} tickers in {len(tickers)//BATCH_SIZE + 1} batches of {BATCH_SIZE}...")

        advancing = 0
        declining = 0
        unchanged = 0
        total_processed = 0

        for i in range(0, len(tickers), BATCH_SIZE):
            batch = tickers[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1

            try:
                data = yf.download(batch, period='5d', group_by='ticker',
                                   progress=False, threads=True)

                for ticker in batch:
                    try:
                        if len(batch) == 1:
                            closes = data['Close'].dropna()
                        else:
                            closes = data[ticker]['Close'].dropna()

                        if len(closes) >= 2:
                            total_processed += 1
                            if closes.iloc[-1] > closes.iloc[-2]:
                                advancing += 1
                            elif closes.iloc[-1] < closes.iloc[-2]:
                                declining += 1
                            else:
                                unchanged += 1
                    except Exception:
                        pass

            except Exception as e:
                logging.warning(f"Batch {batch_num} download failed ({len(batch)} tickers): {e} — trying per-ticker fallback")

                for ticker in batch:
                    try:
                        t = yf.Ticker(ticker)
                        hist = t.history(period='2d')
                        if len(hist) >= 2:
                            total_processed += 1
                            if hist['Close'].iloc[-1] > hist['Close'].iloc[-2]:
                                advancing += 1
                            elif hist['Close'].iloc[-1] < hist['Close'].iloc[-2]:
                                declining += 1
                            else:
                                unchanged += 1
                    except Exception:
                        pass

        if total_processed > 0:
            logging.info(f"Breadth: naik={advancing} turun={declining} stagnan={unchanged} (processed={total_processed})")
            return {
                'naik': advancing,
                'turun': declining,
                'stagnan': unchanged,
                'total': total_processed,
                'is_estimated': total_processed < len(tickers),
                'timestamp': datetime.now().isoformat()
            }

        logging.warning("All batches returned no data — falling back to sample")
        return self._get_breadth_fallback()

    def _get_breadth_fallback(self) -> Dict:
        """Fallback breadth from 10 blue-chips with scaling"""
        idx_stocks = ['BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'TLKM.JK', 'GOTO.JK',
                      'ADRO.JK', 'UNVR.JK', 'ICBP.JK', 'ASII.JK', 'PGAS.JK']

        advancing = declining = unchanged = 0

        for stock in idx_stocks:
            try:
                t = yf.Ticker(stock)
                hist = t.history(period='2d')
                if len(hist) >= 2:
                    if hist['Close'].iloc[-1] > hist['Close'].iloc[-2]:
                        advancing += 1
                    elif hist['Close'].iloc[-1] < hist['Close'].iloc[-2]:
                        declining += 1
                    else:
                        unchanged += 1
            except Exception:
                pass

        total_sampled = advancing + declining + unchanged
        if total_sampled > 0:
            scale_factor = 963 / total_sampled
            advancing = int(advancing * scale_factor)
            declining = int(declining * scale_factor)
            unchanged = int(unchanged * scale_factor)

        return {
            'naik': advancing,
            'turun': declining,
            'stagnan': unchanged,
            'total': advancing + declining + unchanged,
            'is_estimated': True,
            'timestamp': datetime.now().isoformat()
        }


# Test function
if __name__ == '__main__':
    client = YFinanceClient()
    
    # Test single stock
    print("Testing BBCA...")
    bbca = client.get_stock('BBCA')
    print(f"{bbca['symbol']}: {bbca['price']} ({bbca['change_pct']:.2f}%)")
    
    # Test batch
    print("\nTesting batch...")
    stocks = client.get_stocks_batch(['BBCA', 'BBRI', 'BMRI'])
    for stock in stocks:
        print(f"{stock['symbol']}: {stock['price']} ({stock['change_pct']:.2f}%)")
    
    # Test index
    print("\nTesting IHSG...")
    ihsg = client.get_index('^JKSE')
    print(f"{ihsg['name']}: {ihsg['price']} ({ihsg['change_pct']:.2f}%)")
