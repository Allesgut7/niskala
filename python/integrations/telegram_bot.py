# Niskala - Telegram Bot Integration
# Version: 1.0.0

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime

try:
    from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False


class NiskalaTelegramBot:
    """Telegram bot for Niskala trading terminal
    
    Features:
    - /price [symbol] - Get stock price
    - /analyze [symbol] - Full analysis with AI
    - /fng - Fear & Greed Index
    - /news - Latest news with sentiment
    - /screener [preset] - Run screener
    - /alert [symbol] [price] [above/below] - Set price alert
    - /summary - Daily market summary
    """
    
    def __init__(self, token: str, config: Dict = None):
        """Initialize Telegram bot
        
        Args:
            token: Bot token from BotFather
            config: Optional configuration
        """
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot not installed. Run: pip install python-telegram-bot")
        
        self.token = token
        self.config = config or {}
        self.app = None
        self.alerts: Dict[str, List[Dict]] = {}
        
        logging.info("Telegram bot initialized")
    
    def setup(self):
        """Setup bot handlers"""
        self.app = Application.builder().token(self.token).build()
        
        # Command handlers
        self.app.add_handler(CommandHandler("start", self._cmd_start))
        self.app.add_handler(CommandHandler("help", self._cmd_help))
        self.app.add_handler(CommandHandler("price", self._cmd_price))
        self.app.add_handler(CommandHandler("analyze", self._cmd_analyze))
        self.app.add_handler(CommandHandler("fng", self._cmd_fear_greed))
        self.app.add_handler(CommandHandler("news", self._cmd_news))
        self.app.add_handler(CommandHandler("screener", self._cmd_screener))
        self.app.add_handler(CommandHandler("alert", self._cmd_alert))
        self.app.add_handler(CommandHandler("summary", self._cmd_summary))
        
        # Callback handler for inline buttons
        self.app.add_handler(CallbackQueryHandler(self._callback_handler))
    
    def run(self):
        """Start bot polling"""
        if not self.app:
            self.setup()
        
        logging.info("Starting Telegram bot...")
        self.app.run_polling()
    
    # Command handlers
    async def _cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome message"""
        welcome = """
🇮🇩 *Niskala Trading Bot*

Selamat datang di Niskala Telegram Bot!

*Commands:*
/price [symbol] - Harga saham
/analyze [symbol] - Analisis lengkap
/fng - Fear & Greed Index
/news - Berita terbaru
/screener [preset] - Jalankan screener
/alert [symbol] [price] [above/below] - Set alert
/summary - Ringkasan pasar

*Contoh:*
/price BBCA
/analyze BBRI
/screener value
        """
        await update.message.reply_text(welcome, parse_mode='Markdown')
    
    async def _cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help message"""
        help_text = """
📖 *Niskala Bot Commands*

*Market Data:*
/price [symbol] - Harga terkini
/summary - Ringkasan IHSG harian

*Analysis:*
/analyze [symbol] - Analisis AI lengkap
/fng - Fear & Greed Index
/news - Berita dengan sentimen

*Screening:*
/screener [preset] - Filter saham
Presets: value, growth, momentum, quality, dividend

*Alerts:*
/alert [symbol] [price] [above/below]
Contoh: /alert BBCA 9500 above
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def _cmd_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get stock price"""
        if not context.args:
            await update.message.reply_text("Gunakan: /price [symbol]\nContoh: /price BBCA")
            return
        
        symbol = context.args[0].upper()
        
        # Mock data (replace with real data fetch)
        price_data = {
            'price': 9100,
            'change': 50,
            'change_pct': 0.55,
            'volume': 12500000,
            'high': 9150,
            'low': 9000
        }
        
        emoji = "🟢" if price_data['change'] >= 0 else "🔴"
        
        message = f"""
{emoji} *{symbol}*
Harga: {price_data['price']:,.0f}
Change: {price_data['change']:+.0f} ({price_data['change_pct']:+.2f}%)
Volume: {price_data['volume']:,.0f}
High: {price_data['high']:,.0f}
Low: {price_data['low']:,.0f}
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def _cmd_analyze(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Full stock analysis"""
        if not context.args:
            await update.message.reply_text("Gunakan: /analyze [symbol]\nContoh: /analyze BBCA")
            return
        
        symbol = context.args[0].upper()
        
        # Mock analysis (replace with real analysis)
        analysis = {
            'price': 9100,
            'change': 0.55,
            'pe': 18.5,
            'pb': 3.2,
            'roe': 18.5,
            'dividend': 2.1,
            'rsi': 58,
            'signal': 'BUY',
            'sentiment': 'POSITIVE',
            'score': 72
        }
        
        message = f"""
📊 *Analisis {symbol}*

*Harga:* {analysis['price']:,.0f} ({analysis['change']:+.1f}%)
*Signal:* {analysis['signal']} ({analysis['score']}/100)
*Sentiment:* {analysis['sentiment']}

*Fundamental:*
• PE: {analysis['pe']:.1f}x
• PB: {analysis['pb']:.1f}x
• ROE: {analysis['roe']:.1f}%
• Dividend: {analysis['dividend']:.1f}%

*Technical:*
• RSI: {analysis['rsi']:.0f}
        """
        
        # Add action buttons
        keyboard = [
            [
                InlineKeyboardButton("📰 News", callback_data=f"news_{symbol}"),
                InlineKeyboardButton("🔔 Alert", callback_data=f"alert_{symbol}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            message, parse_mode='Markdown', reply_markup=reply_markup
        )
    
    async def _cmd_fear_greed(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Fear & Greed Index"""
        # Mock data (replace with real calculation)
        fng = {
            'indonesia': {'score': 72, 'status': 'GREED'},
            'asia': {'score': 56, 'status': 'GREED'},
            'global': {'score': 71, 'status': 'GREED'},
            'overall': {'score': 66, 'status': 'GREED'}
        }
        
        def get_emoji(score):
            if score >= 75: return "🟢🟢🟢"
            elif score >= 55: return "🟢🟢"
            elif score >= 45: return "🟡"
            elif score >= 25: return "🔴"
            else: return "🔴🔴🔴"
        
        message = f"""
😱 *Fear & Greed Index*

🇮🇩 Indonesia: {fng['indonesia']['score']} {get_emoji(fng['indonesia']['score'])} ({fng['indonesia']['status']})
🌏 Asia: {fng['asia']['score']} {get_emoji(fng['asia']['score'])} ({fng['asia']['status']})
🌍 Global: {fng['global']['score']} {get_emoji(fng['global']['score'])} ({fng['global']['status']})

*Overall:* {fng['overall']['score']} ({fng['overall']['status']})
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def _cmd_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Latest news with sentiment"""
        # Mock news (replace with real news fetch)
        news_items = [
            {'source': 'CNBC', 'title': 'BBRI laba naik 15% Q2', 'sentiment': 78, 'sector': 'Banking'},
            {'source': 'Kontan', 'title': 'IHSG rally 1.2%', 'sentiment': 65, 'sector': 'Market'},
            {'source': 'IDX', 'title': 'Mining stocks mixed', 'sentiment': 10, 'sector': 'Mining'},
        ]
        
        message = "📰 *Berita Terbaru*\n\n"
        
        for item in news_items:
            emoji = "🟢" if item['sentiment'] > 30 else "🔴" if item['sentiment'] < -30 else "⚪"
            message += f"{emoji} *{item['source']}*\n"
            message += f"{item['title']}\n"
            message += f"Sector: {item['sector']} | Score: {item['sentiment']:+d}\n\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def _cmd_screener(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Run stock screener"""
        preset = context.args[0] if context.args else 'value'
        
        # Mock results (replace with real screener)
        results = [
            {'symbol': 'BBCA', 'score': 85, 'pe': 12.5, 'div': 4.2},
            {'symbol': 'BBRI', 'score': 82, 'pe': 10.2, 'div': 5.1},
            {'symbol': 'BMRI', 'score': 78, 'pe': 8.5, 'div': 3.8},
        ]
        
        message = f"📋 *Screener: {preset.title()}*\n\n"
        
        for i, stock in enumerate(results, 1):
            message += f"{i}. *{stock['symbol']}* - Score: {stock['score']}\n"
            message += f"   PE: {stock['pe']:.1f}x | Div: {stock['div']:.1f}%\n"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def _cmd_alert(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set price alert"""
        if len(context.args) < 3:
            await update.message.reply_text(
                "Gunakan: /alert [symbol] [price] [above/below]\n"
                "Contoh: /alert BBCA 9500 above"
            )
            return
        
        symbol = context.args[0].upper()
        price = float(context.args[1])
        condition = context.args[2].lower()
        
        if condition not in ['above', 'below']:
            await update.message.reply_text("Condition harus 'above' atau 'below'")
            return
        
        user_id = str(update.effective_user.id)
        
        if user_id not in self.alerts:
            self.alerts[user_id] = []
        
        self.alerts[user_id].append({
            'symbol': symbol,
            'price': price,
            'condition': condition,
            'created_at': datetime.now().isoformat()
        })
        
        await update.message.reply_text(
            f"✅ Alert diset: {symbol} {condition} {price:,.0f}\n"
            f"Kami akan notifikasi saat harga tercapai."
        )
    
    async def _cmd_summary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Daily market summary"""
        # Mock summary (replace with real data)
        summary = {
            'ihsg': 7250.5,
            'change': 1.2,
            'volume': 12500000000,
            'value': 15200000000000,
            'gainers': [
                {'symbol': 'GOTO', 'change': 12.5},
                {'symbol': 'BUKA', 'change': 8.2},
            ],
            'losers': [
                {'symbol': 'EMTK', 'change': -5.2},
                {'symbol': 'MNCN', 'change': -4.8},
            ]
        }
        
        gainers = "\n".join([f"• {g['symbol']} +{g['change']:.1f}%" for g in summary['gainers']])
        losers = "\n".join([f"• {l['symbol']} {l['change']:.1f}%" for l in summary['losers']])
        
        message = f"""
📊 *IHSG Daily Summary*

*IHSG:* {summary['ihsg']:,.2f} ({summary['change']:+.1f}%)
*Volume:* {summary['volume']/1e9:.1f}B shares
*Value:* {summary['value']/1e12:.1f}T IDR

*Top Gainers:*
{gainers}

*Top Losers:*
{losers}
        """
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def _callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith('news_'):
            symbol = data[5:]
            await query.edit_message_text(f"📰 Loading news for {symbol}...")
        elif data.startswith('alert_'):
            symbol = data[6:]
            await query.edit_message_text(f"🔔 Set alert for {symbol}...")
    
    async def send_trade_alert(self, chat_id: str, alert: Dict):
        """Send trade alert to channel
        
        Args:
            chat_id: Telegram chat ID
            alert: Alert dict with symbol, action, price, etc.
        """
        if not self.app:
            return
        
        emoji = "🟢" if alert['action'] == 'BUY' else "🔴"
        
        message = f"""
{emoji} *Trade Alert: {alert['symbol']}*

*Action:* {alert['action']}
*Price:* {alert['price']:,.0f}
*Target:* {alert.get('target', 'N/A')}
*Stop Loss:* {alert.get('stop_loss', 'N/A')}
*Confidence:* {alert.get('confidence', 0)}%

*Reason:* {alert.get('reason', 'N/A')}
        """
        
        await self.app.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='Markdown'
        )


# Test
if __name__ == '__main__':
    if TELEGRAM_AVAILABLE:
        # Set TELEGRAM_TOKEN environment variable
        import os
        token = os.getenv('TELEGRAM_TOKEN', 'YOUR_TOKEN_HERE')
        
        if token != 'YOUR_TOKEN_HERE':
            bot = NiskalaTelegramBot(token)
            bot.run()
        else:
            print("Set TELEGRAM_TOKEN environment variable to test")
    else:
        print("Install python-telegram-bot: pip install python-telegram-bot")
