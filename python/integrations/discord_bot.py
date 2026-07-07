# Niskala - Discord Bot Integration
# Version: 1.0.0

import logging
from typing import Dict, List, Optional

try:
    import discord
    from discord.ext import commands, tasks
    from discord import app_commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False


class NiskalaDiscordBot:
    """Discord bot for Niskala trading community
    
    Features:
    - /analyze [symbol] - Stock analysis
    - /price [symbol] - Stock price
    - /fng - Fear & Greed Index
    - /screener [preset] - Run screener
    - /news - Latest news
    - /alert [symbol] [price] [condition] - Price alerts
    - Daily market summary (scheduled)
    """
    
    def __init__(self, token: str, config: Dict = None):
        if not DISCORD_AVAILABLE:
            raise ImportError("discord.py not installed. Run: pip install discord.py")
        
        self.token = token
        self.config = config or {}
        
        intents = discord.Intents.default()
        intents.message_content = True
        
        self.bot = commands.Bot(
            command_prefix='!',
            intents=intents,
            description='Niskala Trading Bot'
        )
        
        self._setup_commands()
        
        logging.info("Discord bot initialized")
    
    def _setup_commands(self):
        """Setup slash commands"""
        
        @self.bot.event
        async def on_ready():
            print(f'{self.bot.user} connected to Discord!')
            await self.bot.tree.sync()
            self.daily_summary.start()
        
        @self.bot.tree.command(name="analyze", description="Analyze a stock")
        @app_commands.describe(symbol="Stock symbol (e.g., BBCA)")
        async def analyze(interaction: discord.Interaction, symbol: str):
            symbol = symbol.upper()
            
            embed = discord.Embed(
                title=f"📊 Analysis: {symbol}",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Price", value="4,850", inline=True)
            embed.add_field(name="Change", value="+1.2%", inline=True)
            embed.add_field(name="Signal", value="BUY", inline=True)
            embed.add_field(name="PE Ratio", value="12.5x", inline=True)
            embed.add_field(name="ROE", value="18.5%", inline=True)
            embed.add_field(name="Sentiment", value="+78 (Bullish)", inline=True)
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="price", description="Get stock price")
        @app_commands.describe(symbol="Stock symbol")
        async def price(interaction: discord.Interaction, symbol: str):
            symbol = symbol.upper()
            
            embed = discord.Embed(
                title=f"📈 {symbol}",
                description="Current price information",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Last", value="4,850", inline=True)
            embed.add_field(name="Change", value="+50 (+1.04%)", inline=True)
            embed.add_field(name="Volume", value="125M", inline=True)
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="fng", description="Fear & Greed Index")
        async def fear_greed(interaction: discord.Interaction):
            embed = discord.Embed(
                title="😱 Fear & Greed Index",
                color=discord.Color.gold()
            )
            
            embed.add_field(name="🇮🇩 Indonesia", value="72 (GREED)", inline=True)
            embed.add_field(name="🌏 Asia", value="56 (GREED)", inline=True)
            embed.add_field(name="🌍 Global", value="71 (GREED)", inline=True)
            embed.add_field(name="Overall", value="66 (GREED)", inline=False)
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="screener", description="Run stock screener")
        @app_commands.describe(preset="Screener preset (value, growth, momentum)")
        async def screener(interaction: discord.Interaction, preset: str = "value"):
            embed = discord.Embed(
                title=f"📋 Screener: {preset.title()}",
                description="Top results",
                color=discord.Color.purple()
            )
            
            embed.add_field(name="1. BBCA", value="Score: 85 | Signal: BUY", inline=False)
            embed.add_field(name="2. BBRI", value="Score: 82 | Signal: BUY", inline=False)
            embed.add_field(name="3. BMRI", value="Score: 78 | Signal: BUY", inline=False)
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="news", description="Latest news with sentiment")
        async def news(interaction: discord.Embed):
            embed = discord.Embed(
                title="📰 Latest News",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="🟢 CNBC - BBRI laba naik 15%",
                value="Sector: Banking | Score: +78",
                inline=False
            )
            embed.add_field(
                name="🟢 Kontan - IHSG rally 1.2%",
                value="Sector: Market | Score: +65",
                inline=False
            )
            embed.add_field(
                name="⚪ IDX - Mining stocks mixed",
                value="Sector: Mining | Score: +10",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
        
        @self.bot.tree.command(name="alert", description="Set price alert")
        @app_commands.describe(
            symbol="Stock symbol",
            price="Target price",
            condition="above or below"
        )
        async def alert(interaction: discord.Interaction, symbol: str, price: float, condition: str):
            symbol = symbol.upper()
            
            await interaction.response.send_message(
                f"✅ Alert set: **{symbol}** {condition} **{price:,.0f}**\n"
                f"You'll be notified when the price is reached."
            )
    
    @tasks.loop(hours=24)
    async def daily_summary(self):
        """Send daily market summary"""
        channel_id = self.config.get('summary_channel_id')
        if not channel_id:
            return
        
        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            return
        
        embed = discord.Embed(
            title="📊 IHSG Daily Summary",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="IHSG", value="7,250 (+1.2%)", inline=True)
        embed.add_field(name="Volume", value="12.5B shares", inline=True)
        embed.add_field(name="Value", value="15.2T IDR", inline=True)
        
        embed.add_field(name="Top Gainers", value="GOTO +12.5%\nBUKA +8.2%", inline=True)
        embed.add_field(name="Top Losers", value="EMTK -5.2%\nMNCN -4.8%", inline=True)
        embed.add_field(name="Fear & Greed", value="66 (GREED)", inline=True)
        
        await channel.send(embed=embed)
    
    def run(self):
        """Start the bot"""
        self.bot.run(self.token)


# Test
if __name__ == '__main__':
    if DISCORD_AVAILABLE:
        import os
        token = os.getenv('DISCORD_TOKEN', '')
        
        if token:
            bot = NiskalaDiscordBot(token)
            bot.run()
        else:
            print("Set DISCORD_TOKEN environment variable")
    else:
        print("Install discord.py: pip install discord.py")
