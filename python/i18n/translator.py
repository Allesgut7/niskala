# Niskala - Translator
# i18n translation engine

import json
import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Translator:
    """i18n translation engine"""
    
    def __init__(self, locales_path: Optional[str] = None, default_locale: str = 'en'):
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations: Dict[str, Dict] = {}
        
        if locales_path is None:
            locales_path = os.path.join(os.path.dirname(__file__), 'locales')
        
        self._load_all_locales(locales_path)
        logger.info(f"Translator initialized with {len(self.translations)} locales")
    
    def _load_all_locales(self, locales_path: str):
        """Load all locale files"""
        if not os.path.exists(locales_path):
            logger.warning(f"Locales path not found: {locales_path}")
            return
        
        for filename in os.listdir(locales_path):
            if filename.endswith('.json'):
                locale = filename.replace('.json', '')
                filepath = os.path.join(locales_path, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.translations[locale] = json.load(f)
                    logger.info(f"Loaded locale: {locale}")
                except Exception as e:
                    logger.error(f"Failed to load locale {filename}: {e}")
    
    def t(self, key: str, **kwargs) -> str:
        """Translate a key with optional formatting"""
        # Try current locale first
        locale_data = self.translations.get(self.current_locale, {})
        value = locale_data.get(key)
        
        # Fallback to default locale
        if value is None:
            locale_data = self.translations.get(self.default_locale, {})
            value = locale_data.get(key, key)
        
        # Format with kwargs
        if kwargs:
            try:
                value = value.format(**kwargs)
            except (KeyError, IndexError):
                pass
        
        return value
    
    def translate(self, key: str, locale: Optional[str] = None, **kwargs) -> str:
        """Translate with explicit locale"""
        old_locale = self.current_locale
        if locale:
            self.current_locale = locale
        
        result = self.t(key, **kwargs)
        self.current_locale = old_locale
        return result
    
    def set_locale(self, locale: str):
        """Set current locale"""
        if locale in self.translations:
            self.current_locale = locale
            logger.info(f"Locale set to: {locale}")
        else:
            logger.warning(f"Locale not found: {locale}")
    
    def get_locale(self) -> str:
        """Get current locale"""
        return self.current_locale
    
    def get_supported_locales(self) -> list:
        """Get list of supported locales"""
        locale_names = {
            'en': 'English',
            'id': 'Bahasa Indonesia',
            'ms': 'Bahasa Melayu',
            'th': 'ภาษาไทย',
            'vi': 'Tiếng Việt',
            'fil': 'Filipino',
            'zh': '简体中文',
        }
        
        return [
            {'code': code, 'name': locale_names.get(code, code)}
            for code in self.translations.keys()
        ]
    
    def has_key(self, key: str, locale: Optional[str] = None) -> bool:
        """Check if translation key exists"""
        locale = locale or self.current_locale
        locale_data = self.translations.get(locale, {})
        return key in locale_data
    
    def add_translation(self, locale: str, key: str, value: str):
        """Add or update a translation"""
        if locale not in self.translations:
            self.translations[locale] = {}
        self.translations[locale][key] = value
    
    def export_locale(self, locale: str) -> Dict:
        """Export locale translations"""
        return self.translations.get(locale, {})
    
    def import_locale(self, locale: str, translations: Dict):
        """Import translations for a locale"""
        if locale in self.translations:
            self.translations[locale].update(translations)
        else:
            self.translations[locale] = translations


# Singleton
_translator: Optional[Translator] = None


def get_translator() -> Translator:
    """Get global translator instance"""
    global _translator
    if _translator is None:
        _translator = Translator()
    return _translator
