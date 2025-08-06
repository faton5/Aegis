"""
Gestionnaire de traductions modulaire pour Aegis
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional

from config.logging_config import get_logger

logger = get_logger('translations')


class TranslationManager:
    """Gestionnaire centralisé des traductions"""
    
    def __init__(self, locales_dir: str = "locales"):
        self.locales_dir = Path(locales_dir)
        self.translations: Dict[str, Dict[str, str]] = {}
        self.default_language = "en"
        self.available_languages = []
        
        # Charger toutes les traductions
        self._load_all_translations()
    
    def _load_all_translations(self):
        """Charger toutes les traductions depuis les fichiers JSON"""
        try:
            if not self.locales_dir.exists():
                logger.error(f"Dossier de traductions non trouvé: {self.locales_dir}")
                return
            
            # Scanner tous les fichiers .json
            for json_file in self.locales_dir.glob("*.json"):
                language_code = json_file.stem
                
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        translations = json.load(f)
                        self.translations[language_code] = translations
                        self.available_languages.append(language_code)
                        logger.info(f"Traductions chargées pour: {language_code} ({len(translations)} clés)")
                        
                except Exception as e:
                    logger.error(f"Erreur lors du chargement de {json_file}: {e}")
            
            if not self.translations:
                logger.error("Aucune traduction chargée !")
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement des traductions: {e}")
    
    def t(self, key: str, guild_id: int = None, language: str = None, fallback: str = None, **kwargs) -> str:
        """
        Traduire une clé
        
        Args:
            key: Clé de traduction
            guild_id: ID du serveur (pour déterminer la langue)
            language: Langue forcée (optionnel)
            fallback: Texte par défaut si traduction introuvable
            **kwargs: Variables pour formatage
            
        Returns:
            Texte traduit
        """
        try:
            # Déterminer la langue à utiliser
            target_language = language or self._get_guild_language(guild_id) or self.default_language
            
            # Récupérer la traduction
            if target_language in self.translations:
                translation = self.translations[target_language].get(key)
                if translation:
                    # Formater avec les variables fournies
                    if kwargs:
                        try:
                            return translation.format(**kwargs)
                        except KeyError as e:
                            logger.warning(f"Variable manquante dans traduction '{key}': {e}")
                            return translation
                    return translation
            
            # Fallback vers la langue par défaut
            if target_language != self.default_language and self.default_language in self.translations:
                translation = self.translations[self.default_language].get(key)
                if translation:
                    if kwargs:
                        try:
                            return translation.format(**kwargs)
                        except KeyError:
                            return translation
                    return translation
            
            # Utiliser le fallback fourni
            if fallback:
                return fallback
                
            # En dernier recours, retourner la clé
            logger.warning(f"Traduction non trouvée: {key} (langue: {target_language})")
            return key
            
        except Exception as e:
            logger.error(f"Erreur lors de la traduction de '{key}': {e}")
            return fallback or key
    
    def _get_guild_language(self, guild_id: int) -> Optional[str]:
        """
        Obtenir la langue configurée pour un serveur
        
        Args:
            guild_id: ID du serveur
            
        Returns:
            Code de langue ou None
        """
        if not guild_id:
            return None
            
        try:
            # Import dynamique pour éviter les dépendances circulaires
            from services.guild_service import guild_service
            
            config = guild_service.get_guild_config(guild_id)
            return config.get('language', self.default_language)
            
        except Exception as e:
            logger.debug(f"Impossible de récupérer la langue pour guild {guild_id}: {e}")
            return None
    
    def get_available_languages(self) -> Dict[str, str]:
        """
        Obtenir la liste des langues disponibles
        
        Returns:
            Dict {code: nom_langue}
        """
        language_names = {
            'fr': '🇫🇷 Français',
            'en': '🇺🇸 English'
        }
        
        return {lang: language_names.get(lang, lang.upper()) 
                for lang in self.available_languages}
    
    def add_translation(self, language: str, key: str, value: str):
        """
        Ajouter une traduction dynamiquement
        
        Args:
            language: Code de langue
            key: Clé de traduction
            value: Valeur traduite
        """
        if language not in self.translations:
            self.translations[language] = {}
            
        self.translations[language][key] = value
        logger.debug(f"Traduction ajoutée: {language}.{key}")
    
    def reload_translations(self):
        """Recharger toutes les traductions"""
        self.translations.clear()
        self.available_languages.clear()
        self._load_all_translations()
        logger.info("Traductions rechargées")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques des traductions"""
        stats = {
            'languages': len(self.available_languages),
            'total_keys': sum(len(translations) for translations in self.translations.values()),
            'languages_loaded': list(self.available_languages)
        }
        
        for lang in self.available_languages:
            stats[f'{lang}_keys'] = len(self.translations[lang])
            
        return stats


# Instance globale du gestionnaire de traductions
translator = TranslationManager()