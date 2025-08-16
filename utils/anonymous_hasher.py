"""
Service de hachage anonyme pour les reporters
Assure l'anonymat complet tout en permettant la détection de doublons
"""
import hashlib
import hmac
from typing import Optional
from config.bot_config import bot_settings
from config.logging_config import get_logger

logger = get_logger('anonymous_hasher')


class AnonymousHasher:
    """Service pour générer des hash anonymes des reporters"""
    
    def __init__(self):
        self._salt_secret = None
        self._initialized = False
    
    def _initialize(self) -> bool:
        """Initialiser le service avec le salt secret"""
        if self._initialized:
            return True
            
        if not bot_settings.reporter_salt_secret:
            logger.error("❌ REPORTER_SALT_SECRET manquant - anonymat impossible")
            return False
        
        if len(bot_settings.reporter_salt_secret) < 32:
            logger.error("❌ REPORTER_SALT_SECRET trop court - risque de sécurité")
            return False
        
        self._salt_secret = bot_settings.reporter_salt_secret.encode('utf-8')
        self._initialized = True
        logger.info("✅ Service de hachage anonyme initialisé")
        return True
    
    def generate_reporter_hash(self, reporter_id: int, guild_id: int) -> Optional[str]:
        """
        Génère un hash anonyme pour un reporter dans un serveur donné
        
        Args:
            reporter_id: ID Discord du reporter
            guild_id: ID du serveur Discord
            
        Returns:
            Hash anonyme hexadécimal ou None si erreur
        """
        if not self._initialize():
            return None
        
        try:
            # Données à hasher: reporter_id + guild_id
            data = f"{reporter_id}:{guild_id}".encode('utf-8')
            
            # Utiliser HMAC-SHA256 avec le salt secret
            # Plus sécurisé qu'un simple SHA256 car résistant aux attaques par dictionnaire
            hash_obj = hmac.new(self._salt_secret, data, hashlib.sha256)
            anonymous_hash = hash_obj.hexdigest()
            
            logger.debug(f"Hash anonyme généré pour reporter dans guild {guild_id}")
            return anonymous_hash
            
        except Exception as e:
            logger.error(f"❌ Erreur génération hash anonyme: {e}")
            return None
    
    def generate_report_uniqueness_hash(self, reporter_id: int, guild_id: int, target_username: str) -> Optional[str]:
        """
        Génère un hash pour détecter les doublons de signalements
        
        Args:
            reporter_id: ID Discord du reporter  
            guild_id: ID du serveur Discord
            target_username: Nom d'utilisateur de la cible signalée
            
        Returns:
            Hash unique pour ce trio (reporter, serveur, cible) ou None si erreur
        """
        if not self._initialize():
            return None
        
        try:
            # Normaliser le nom d'utilisateur (minuscules, espaces supprimés)
            normalized_target = target_username.lower().strip()
            
            # Données à hasher: reporter_id + guild_id + target_username normalisé
            data = f"{reporter_id}:{guild_id}:{normalized_target}".encode('utf-8')
            
            # Utiliser HMAC-SHA256 avec le salt secret
            hash_obj = hmac.new(self._salt_secret, data, hashlib.sha256)
            uniqueness_hash = hash_obj.hexdigest()
            
            logger.debug(f"Hash d'unicité généré pour signalement dans guild {guild_id}")
            return uniqueness_hash
            
        except Exception as e:
            logger.error(f"❌ Erreur génération hash d'unicité: {e}")
            return None
    
    def is_configured(self) -> bool:
        """Vérifier si le service est correctement configuré"""
        return self._initialize()
    
    def get_security_info(self) -> dict:
        """Informations de sécurité pour le debug (sans exposer le salt)"""
        return {
            'initialized': self._initialized,
            'salt_configured': bool(bot_settings.reporter_salt_secret),
            'salt_length': len(bot_settings.reporter_salt_secret) if bot_settings.reporter_salt_secret else 0,
            'salt_sufficient': len(bot_settings.reporter_salt_secret) >= 32 if bot_settings.reporter_salt_secret else False
        }


# Instance globale
anonymous_hasher = AnonymousHasher()