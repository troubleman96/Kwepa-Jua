import json
import os
from typing import Dict, Any

class LanguageService:
    def __init__(self):
        self.translations = {}
        self.load_translations()
    
    def load_translations(self):
        """Load all translation files"""
        locales_dir = os.path.join(os.path.dirname(__file__), '..', 'locales')
        
        for filename in ['en.json', 'sw.json']:
            filepath = os.path.join(locales_dir, filename)
            if os.path.exists(filepath):
                lang_code = filename.split('.')[0]
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
    
    def get_translations(self, lang: str = 'en') -> Dict[str, Any]:
        """Get translations for a specific language"""
        return self.translations.get(lang, self.translations.get('en', {}))
    
    def translate(self, key: str, lang: str = 'en') -> str:
        """Get a specific translation"""
        translations = self.get_translations(lang)
        return translations.get(key, key)

# Global instance
language_service = LanguageService()