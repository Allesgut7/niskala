# Niskala - ASCII Chart Engine
# Version: 1.0.0
# Terminal-based candlestick and line chart rendering

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pandas as pd
import numpy as np
import logging


class ChartType(Enum):
    CANDLE = "candle"
    LINE = "line"
    AREA = "area"
    BAR = "bar"


class Timeframe(Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    D1 = "1d"
    W1 = "1w"


@dataclass
class ChartConfig:
    """Chart configuration"""
    width: int = 80
    height: int = 24
    chart_type: ChartType = ChartType.CANDLE
    timeframe: Timeframe = Timeframe.D1
    show_volume: bool = True
    show_ma: bool = True
    ma_periods: List[int] = None
    show_rsi: bool = False
    show_macd: bool = False
    show_bollinger: bool = False
    
    def __post_init__(self):
        if self.ma_periods is None:
            self.ma_periods = [20, 50]


class ASCIIChart:
    """ASCII-based chart renderer for terminal"""
    
    # Unicode box-drawing characters
    BOX_CHARS = {
        'candle_up': '█',      # Bullish candle body
        'candle_down': '░',    # Bearish candle body
        'wick': '│',           # Candle wick
        'hline': '─',          # Horizontal line
        'vline': '│',          # Vertical line
        'cross': '┼',          # Cross
        'tee_up': '┴',         # Tee up
        'tee_down': '┬',       # Tee down
        'tee_left': '┤',       # Tee left
        'tee_right': '├',      # Tee right
        'corner_tl': '┌',      # Top-left corner
        'corner_tr': '┐',      # Top-right corner
        'corner_bl': '└',      # Bottom-left corner
        'corner_br': '┘',      # Bottom-right corner
        'arrow_up': '▲',       # Up arrow
        'arrow_down': '▼',     # Down arrow
        'dot': '·',            # Dot
        'block': '█',          # Full block
        'shade_light': '░',    # Light shade
        'shade_medium': '▒',   # Medium shade
        'shade_dark': '▓',     # Dark shade
    }
    
    def __init__(self, config: Optional[ChartConfig] = None):
        self.config = config or ChartConfig()
        logging.info("ASCII chart engine initialized")
    
    def render_candlestick(self, df: pd.DataFrame, title: str = '') -> str:
        """Render candlestick chart
        
        Args:
            df: DataFrame with OHLCV columns
            title: Chart title
            
        Returns:
            ASCII art string
        """
        if df.empty or len(df) < 2:
            return "Insufficient data for chart"
        
        width = self.config.width
        height = self.config.height
        
        # Calculate price range
        high_max = df['high'].max()
        low_min = df['low'].min()
        price_range = high_max - low_min
        
        if price_range == 0:
            return "No price variation"
        
        # Scale to chart height
        def price_to_row(price):
            return int((price - low_min) / price_range * (height - 1))
        
        # Build chart grid
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Determine bar width
        n_bars = min(len(df), width - 10)  # Leave space for price axis
        bar_width = max(1, (width - 10) // n_bars)
        
        # Render candles
        for i in range(n_bars):
            if i >= len(df):
                break
            
            row = df.iloc[i]
            col_start = i * bar_width + 5
            
            open_price = row['open']
            close_price = row['close']
            high_price = row['high']
            low_price = row['low']
            
            open_row = price_to_row(open_price)
            close_row = price_to_row(close_price)
            high_row = price_to_row(high_price)
            low_row = price_to_row(low_price)
            
            # Determine bullish/bearish
            bullish = close_price >= open_price
            body_char = self.BOX_CHARS['candle_up'] if bullish else self.BOX_CHARS['shade_light']
            
            # Draw wick (high to low)
            for r in range(low_row, high_row + 1):
                if 0 <= r < height and 0 <= col_start < width:
                    grid[r][col_start] = self.BOX_CHARS['wick']
            
            # Draw body
            body_top = min(open_row, close_row)
            body_bottom = max(open_row, close_row)
            
            for r in range(body_top, body_bottom + 1):
                if 0 <= r < height:
                    for c in range(bar_width):
                        col = col_start + c
                        if 0 <= col < width:
                            grid[r][col] = body_char
        
        # Build output
        lines = []
        
        # Title
        if title:
            lines.append(f" {title}")
            lines.append("")
        
        # Price axis + chart
        for r in range(height - 1, -1, -1):
            price = low_min + (r / (height - 1)) * price_range
            
            # Price label (every 4 rows)
            if r % 4 == 0:
                price_label = f"{price:>8.0f} │"
            else:
                price_label = "         │"
            
            row_str = ''.join(grid[r])
            lines.append(f"{price_label}{row_str}")
        
        # Time axis
        lines.append("         └" + self.BOX_CHARS['hline'] * (width - 10))
        
        # Volume (if enabled)
        if self.config.show_volume and 'volume' in df.columns:
            lines.append("")
            vol_lines = self._render_volume(df, width, n_bars=6)
            lines.extend(vol_lines)
        
        # MA legend
        if self.config.show_ma:
            ma_text = "  MA: "
            for period in self.config.ma_periods:
                ma_val = df['close'].rolling(period).mean().iloc[-1]
                if not np.isnan(ma_val):
                    ma_text += f"MA{period}={ma_val:.0f}  "
            lines.append(ma_text)
        
        return '\n'.join(lines)
    
    def render_line(self, df: pd.DataFrame, title: str = '') -> str:
        """Render line chart
        
        Args:
            df: DataFrame with 'close' column
            title: Chart title
            
        Returns:
            ASCII art string
        """
        if df.empty:
            return "No data"
        
        width = self.config.width
        height = self.config.height
        
        close = df['close'].values
        n_points = min(len(close), width - 10)
        
        # Resample to fit width
        if len(close) > n_points:
            indices = np.linspace(0, len(close) - 1, n_points).astype(int)
            close = close[indices]
        
        price_min = close.min()
        price_max = close.max()
        price_range = price_max - price_min
        
        if price_range == 0:
            return "No price variation"
        
        def price_to_row(price):
            return int((price - price_min) / price_range * (height - 1))
        
        # Build grid
        grid = [[' ' for _ in range(width)] for _ in range(height)]
        
        # Plot line
        for i in range(len(close)):
            col = i + 5
            row = price_to_row(close[i])
            
            if 0 <= row < height and 0 <= col < width:
                grid[row][col] = '●'
                
                # Connect to previous point
                if i > 0:
                    prev_row = price_to_row(close[i-1])
                    prev_col = col - 1
                    
                    # Draw connecting line
                    if prev_row != row:
                        step = 1 if row > prev_row else -1
                        for r in range(prev_row, row, step):
                            if 0 <= r < height and 0 <= prev_col < width:
                                grid[r][prev_col] = '│'
        
        # Build output
        lines = []
        
        if title:
            lines.append(f" {title}")
            lines.append("")
        
        for r in range(height - 1, -1, -1):
            price = price_min + (r / (height - 1)) * price_range
            
            if r % 4 == 0:
                price_label = f"{price:>8.0f} │"
            else:
                price_label = "         │"
            
            row_str = ''.join(grid[r])
            lines.append(f"{price_label}{row_str}")
        
        lines.append("         └" + self.BOX_CHARS['hline'] * (width - 10))
        
        return '\n'.join(lines)
    
    def render_multi_timeframe(
        self,
        data_dict: Dict[str, pd.DataFrame],
        symbol: str = '',
        layout: str = '2x2'
    ) -> str:
        """Render multi-timeframe chart layout
        
        Args:
            data_dict: Dict mapping timeframe -> DataFrame
            symbol: Stock symbol
            layout: '2x2', '1x4', '4x1'
            
        Returns:
            ASCII art string with multiple charts
        """
        charts = []
        
        for tf_name, df in data_dict.items():
            chart = self.render_candlestick(df, title=f"{symbol} {tf_name}")
            charts.append(chart)
        
        if layout == '2x2' and len(charts) >= 4:
            return self._layout_2x2(charts[:4])
        elif layout == '1x4' and len(charts) >= 4:
            return self._layout_1x4(charts[:4])
        elif layout == '4x1' and len(charts) >= 4:
            return self._layout_4x1(charts[:4])
        else:
            return '\n\n'.join(charts)
    
    def _render_volume(self, df: pd.DataFrame, width: int, n_bars: int = 6) -> List[str]:
        """Render volume bars"""
        if 'volume' not in df.columns:
            return []
        
        volumes = df['volume'].values[-n_bars:]
        vol_max = volumes.max() if volumes.max() > 0 else 1
        
        bar_width = max(1, (width - 10) // n_bars)
        vol_height = 4
        
        grid = [[' ' for _ in range(width)] for _ in range(vol_height)]
        
        for i, vol in enumerate(volumes):
            col_start = i * bar_width + 5
            bar_height = int(vol / vol_max * vol_height)
            
            for r in range(vol_height - bar_height, vol_height):
                for c in range(bar_width):
                    col = col_start + c
                    if 0 <= col < width:
                        grid[r][col] = self.BOX_CHARS['shade_medium']
        
        lines = ["  Volume │"]
        for r in range(vol_height):
            lines.append(f"         │{''.join(grid[r])}")
        
        return lines
    
    def _layout_2x2(self, charts: List[str]) -> str:
        """Arrange 4 charts in 2x2 grid"""
        # Split each chart into lines
        chart_lines = [c.split('\n') for c in charts]
        
        # Find max height for each row
        row1_height = max(len(chart_lines[0]), len(chart_lines[1]))
        row2_height = max(len(chart_lines[2]), len(chart_lines[3]))
        
        # Pad charts to same height
        for i in range(2):
            while len(chart_lines[i]) < row1_height:
                chart_lines[i].append('')
        for i in range(2, 4):
            while len(chart_lines[i]) < row2_height:
                chart_lines[i].append('')
        
        # Combine horizontally
        lines = []
        for r in range(row1_height):
            left = chart_lines[0][r][:40].ljust(40)
            right = chart_lines[1][r][:40].ljust(40)
            lines.append(f"{left} │ {right}")
        
        lines.append("─" * 82)
        
        for r in range(row2_height):
            left = chart_lines[2][r][:40].ljust(40)
            right = chart_lines[3][r][:40].ljust(40)
            lines.append(f"{left} │ {right}")
        
        return '\n'.join(lines)
    
    def _layout_1x4(self, charts: List[str]) -> str:
        """Arrange 4 charts in 1 row"""
        chart_lines = [c.split('\n') for c in charts]
        max_height = max(len(c) for c in chart_lines)
        
        for i in range(4):
            while len(chart_lines[i]) < max_height:
                chart_lines[i].append('')
        
        lines = []
        for r in range(max_height):
            parts = [chart_lines[i][r][:20].ljust(20) for i in range(4)]
            lines.append(" │ ".join(parts))
        
        return '\n'.join(lines)
    
    def _layout_4x1(self, charts: List[str]) -> str:
        """Stack 4 charts vertically"""
        return '\n' + ('─' * 82 + '\n').join(charts)


class TechnicalIndicators:
    """Calculate and render technical indicators"""
    
    @staticmethod
    def moving_average(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(period).mean()
    
    @staticmethod
    def exponential_ma(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=period).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = data.diff()
        gain = delta.where(delta > 0, 0).rolling(period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def macd(data: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD (line, signal, histogram)"""
        ema12 = data.ewm(span=12).mean()
        ema26 = data.ewm(span=26).mean()
        macd_line = ema12 - ema26
        signal = macd_line.ewm(span=9).mean()
        histogram = macd_line - signal
        return macd_line, signal, histogram
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands (upper, middle, lower)"""
        middle = data.rolling(period).mean()
        std = data.rolling(period).std()
        upper = middle + std_dev * std
        lower = middle - std_dev * std
        return upper, middle, lower
    
    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(period).mean()
    
    @staticmethod
    def render_indicator_panel(df: pd.DataFrame) -> str:
        """Render indicator values panel"""
        close = df['close']
        
        lines = []
        lines.append(" Technical Indicators:")
        lines.append("─" * 40)
        
        # Moving Averages
        for period in [20, 50, 200]:
            ma = close.rolling(period).mean().iloc[-1]
            if not np.isnan(ma):
                vs_price = ((close.iloc[-1] - ma) / ma) * 100
                signal = "▲" if vs_price > 0 else "▼"
                lines.append(f"  MA{period:>3d}: {ma:>8.0f}  ({vs_price:+.1f}% {signal})")
        
        # RSI
        rsi_val = TechnicalIndicators.rsi(close).iloc[-1]
        if not np.isnan(rsi_val):
            rsi_label = "Overbought" if rsi_val > 70 else "Oversold" if rsi_val < 30 else "Neutral"
            lines.append(f"  RSI14: {rsi_val:>6.1f}  ({rsi_label})")
        
        # MACD
        macd_line, signal, hist = TechnicalIndicators.macd(close)
        if not np.isnan(macd_line.iloc[-1]):
            lines.append(f"  MACD:  {macd_line.iloc[-1]:>+8.1f}  (Signal: {signal.iloc[-1]:+.1f})")
        
        # Bollinger Bands
        upper, middle, lower = TechnicalIndicators.bollinger_bands(close)
        if not np.isnan(upper.iloc[-1]):
            lines.append(f"  BB:    Upper={upper.iloc[-1]:.0f} Mid={middle.iloc[-1]:.0f} Lower={lower.iloc[-1]:.0f}")
        
        return '\n'.join(lines)


# Test
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Generate sample data
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=50, freq='D')
    close = 4500 + np.cumsum(np.random.randn(50) * 30)
    
    df = pd.DataFrame({
        'open': close * (1 + np.random.randn(50) * 0.005),
        'high': close * (1 + abs(np.random.randn(50) * 0.01)),
        'low': close * (1 - abs(np.random.randn(50) * 0.01)),
        'close': close,
        'volume': np.random.randint(1000000, 5000000, 50)
    }, index=dates)
    
    # Render candlestick chart
    chart = ASCIIChart(ChartConfig(width=80, height=20, show_volume=True))
    print(chart.render_candlestick(df, title="BBRI - Daily"))
    
    # Render indicator panel
    print()
    print(TechnicalIndicators.render_indicator_panel(df))
