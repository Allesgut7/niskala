# Niskala - Locale Manager
# User locale preferences

import sqlite3
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class LocaleManager:
    """Manage user locale preferences"""
    
    def __init__(self, db_path: str = 'data/niskala.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                locale TEXT DEFAULT 'en',
                market TEXT DEFAULT 'IDX',
                currency TEXT DEFAULT 'IDR',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_user_locale(self, user_id: str) -> str:
        """Get user's locale preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT locale FROM user_preferences WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else 'en'
    
    def set_user_locale(self, user_id: str, locale: str):
        """Set user's locale preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, locale, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, locale))
        
        conn.commit()
        conn.close()
    
    def get_user_market(self, user_id: str) -> str:
        """Get user's market preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT market FROM user_preferences WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else 'IDX'
    
    def set_user_market(self, user_id: str, market: str):
        """Set user's market preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, market, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, market))
        
        conn.commit()
        conn.close()
    
    def get_user_currency(self, user_id: str) -> str:
        """Get user's currency preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT currency FROM user_preferences WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else 'IDR'
    
    def set_user_currency(self, user_id: str, currency: str):
        """Set user's currency preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO user_preferences (user_id, currency, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, currency))
        
        conn.commit()
        conn.close()
    
    def get_all_preferences(self, user_id: str) -> Dict:
        """Get all user preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'user_id': row[0],
                'locale': row[1],
                'market': row[2],
                'currency': row[3],
            }
        
        return {
            'user_id': user_id,
            'locale': 'en',
            'market': 'IDX',
            'currency': 'IDR',
        }
    
    def detect_locale(self, accept_language: str) -> str:
        """Detect locale from Accept-Language header"""
        lang_map = {
            'en': 'en',
            'id': 'id',
            'ms': 'ms',
            'th': 'th',
            'vi': 'vi',
            'fil': 'fil',
            'tl': 'fil',
            'zh': 'zh',
            'zh-cn': 'zh',
            'zh-tw': 'zh',
        }
        
        for lang in accept_language.split(','):
            lang = lang.strip().split(';')[0].lower()
            if lang in lang_map:
                return lang_map[lang]
        
        return 'en'
