"""
Utilitaires de sécurité et validation pour Aegis
"""
import re
from typing import Optional
from config.logging_config import get_logger

logger = get_logger('security')


class SecurityValidator:
    """Gestionnaire de validation et sécurité"""
    
    # Patterns de validation
    DISCORD_ID_PATTERN = re.compile(r'^\d{17,19}$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9._-]+$')
    MENTION_PATTERN = re.compile(r'<@[!&]?\d+>')
    CONTROL_CHARS_PATTERN = re.compile(r'[\x00-\x1f\x7f-\x9f]')
    
    def __init__(self):
        self.max_input_length = 2000
        self.banned_words = set()  # Mots interdits (à configurer)
    
    def validate_input(self, text: str, max_length: int = None) -> bool:
        """
        Valider une entrée utilisateur
        
        Args:
            text: Texte à valider
            max_length: Longueur maximale (optionnel)
            
        Returns:
            True si valide
        """
        if not isinstance(text, str):
            return False
            
        if not text.strip():
            return False
            
        max_len = max_length or self.max_input_length
        if len(text) > max_len:
            return False
            
        # Vérifier les mots interdits
        if self._contains_banned_words(text.lower()):
            logger.warning(f"Texte contenant des mots interdits détecté")
            return False
            
        return True
    
    def sanitize_input(self, text: str, max_length: int = None) -> str:
        """
        Nettoyer une entrée utilisateur
        
        Args:
            text: Texte à nettoyer
            max_length: Longueur maximale
            
        Returns:
            Texte nettoyé
        """
        if not isinstance(text, str):
            return ""
            
        # Supprimer les caractères de contrôle
        text = self.CONTROL_CHARS_PATTERN.sub('', text)
        
        # Supprimer les mentions Discord
        text = self.MENTION_PATTERN.sub('[mention supprimée]', text)
        
        # Limiter la longueur
        max_len = max_length or self.max_input_length
        if len(text) > max_len:
            text = text[:max_len-3] + "..."
            
        # Nettoyer les espaces
        text = ' '.join(text.split())
        
        return text.strip()
    
    def validate_discord_id(self, user_id: str) -> bool:
        """
        Valider un ID Discord
        
        Args:
            user_id: ID à valider
            
        Returns:
            True si valide
        """
        if not isinstance(user_id, str):
            user_id = str(user_id)
            
        return bool(self.DISCORD_ID_PATTERN.match(user_id))
    
    def validate_username(self, username: str) -> bool:
        """
        Valider un nom d'utilisateur Discord
        
        Args:
            username: Username à valider
            
        Returns:
            True si valide
        """
        if not isinstance(username, str):
            return False
            
        if not username.strip():
            return False
            
        if len(username) > 32:  # Limite Discord
            return False
            
        # Vérifier le format
        return bool(self.USERNAME_PATTERN.match(username))
    
    def _contains_banned_words(self, text: str) -> bool:
        """Vérifier si le texte contient des mots interdits"""
        if not self.banned_words:
            return False
            
        words = set(text.split())
        return bool(self.banned_words.intersection(words))
    
    def add_banned_word(self, word: str):
        """Ajouter un mot interdit"""
        self.banned_words.add(word.lower())
    
    def remove_banned_word(self, word: str):
        """Retirer un mot interdit"""
        self.banned_words.discard(word.lower())
    
    def validate_report_data(self, target: str, reason: str, evidence: str = "") -> tuple[bool, Optional[str]]:
        """
        Valider les données d'un signalement complet
        
        Args:
            target: Utilisateur cible
            reason: Raison du signalement
            evidence: Preuves (optionnel)
            
        Returns:
            (is_valid, error_message)
        """
        # Valider le nom d'utilisateur cible
        if not self.validate_username(target):
            return False, "Le nom d'utilisateur cible n'est pas valide"
        
        # Valider la raison
        if not self.validate_input(reason, max_length=500):
            return False, "La raison du signalement n'est pas valide ou trop longue"
        
        # Valider les preuves si fournies
        if evidence and not self.validate_input(evidence, max_length=1900):
            return False, "Les preuves fournies ne sont pas valides ou trop longues"
        
        return True, None