import re
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Set, Optional
from collections import defaultdict, deque
import discord

# Configuration du système de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aegis_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('AegisBot')

class SecurityValidator:
    """Classe pour valider et sécuriser les entrées utilisateur"""
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Nettoie et sécurise une entrée texte"""
        if not text:
            return ""
        
        # Limiter la longueur
        text = text[:max_length]
        
        # Supprimer les caractères de contrôle dangereux
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Échapper les mentions @everyone et @here
        text = text.replace('@everyone', '@\u200beveryone')
        text = text.replace('@here', '@\u200bhere')
        
        return text.strip()
    
    @staticmethod
    def validate_discord_id(user_id: str) -> bool:
        """Valide un ID Discord"""
        return re.match(r'^\d{17,19}$', user_id) is not None
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Valide un nom d'utilisateur Discord"""
        if not username or len(username) > 100:
            return False
        
        # Vérifier s'il s'agit d'un ID Discord
        if SecurityValidator.validate_discord_id(username):
            return True
            
        # Valider le format nom d'utilisateur
        return re.match(r'^[a-zA-Z0-9._]{2,32}$', username.replace('#', '')) is not None

class RateLimiter:
    """Système de limitation de taux pour éviter le spam"""
    
    def __init__(self):
        self.user_requests: Dict[int, deque] = defaultdict(deque)
        self.cleanup_interval = timedelta(hours=1)
        self.last_cleanup = datetime.now()
    
    def is_rate_limited(self, user_id: int, max_requests: int = 3, window_hours: int = 1) -> bool:
        """Vérifie si l'utilisateur a dépassé la limite de taux"""
        now = datetime.now()
        
        # Nettoyage périodique
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_requests()
            self.last_cleanup = now
        
        user_requests = self.user_requests[user_id]
        window_start = now - timedelta(hours=window_hours)
        
        # Supprimer les requêtes anciennes
        while user_requests and user_requests[0] < window_start:
            user_requests.popleft()
        
        # Vérifier la limite
        if len(user_requests) >= max_requests:
            logger.warning(f"Rate limit atteint pour l'utilisateur {user_id}")
            return True
        
        # Ajouter la nouvelle requête
        user_requests.append(now)
        return False
    
    def _cleanup_old_requests(self):
        """Nettoie les anciennes requêtes pour libérer la mémoire"""
        cutoff = datetime.now() - timedelta(hours=24)
        users_to_remove = []
        
        for user_id, requests in self.user_requests.items():
            while requests and requests[0] < cutoff:
                requests.popleft()
            
            if not requests:
                users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            del self.user_requests[user_id]

class ReportTracker:
    """Suivi des signalements pour éviter les doublons"""
    
    def __init__(self):
        self.report_hashes: Set[str] = set()
        self.cleanup_interval = timedelta(days=7)
        self.last_cleanup = datetime.now()
    
    def is_duplicate_report(self, reporter_id: int, target_username: str, reason: str) -> bool:
        """Vérifie si c'est un signalement en double"""
        now = datetime.now()
        
        # Nettoyage périodique
        if now - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_hashes()
            self.last_cleanup = now
        
        # Créer un hash unique pour ce signalement
        report_data = f"{reporter_id}:{target_username}:{reason[:100]}"
        report_hash = hashlib.sha256(report_data.encode()).hexdigest()
        
        if report_hash in self.report_hashes:
            logger.warning(f"Signalement en double détecté: {report_hash[:8]}...")
            return True
        
        self.report_hashes.add(report_hash)
        return False
    
    def _cleanup_old_hashes(self):
        """Nettoie les anciens hashes (simplifié - en production, utiliser une base de données)"""
        # En production, il faudrait stocker les timestamps et nettoyer selon l'âge
        if len(self.report_hashes) > 10000:  # Limite arbitraire
            self.report_hashes.clear()

class AuditLogger:
    """Système de logs d'audit pour traçabilité"""
    
    @staticmethod
    def log_report_submitted(user_id: int, target_username: str, guild_id: int):
        """Log d'un nouveau signalement"""
        logger.info(f"REPORT_SUBMITTED - User: {user_id}, Target: {target_username}, Guild: {guild_id}")
    
    @staticmethod
    def log_validation_action(validator_id: int, action: str, report_id: str, guild_id: int):
        """Log d'une action de validation"""
        logger.info(f"VALIDATION_{action.upper()} - Validator: {validator_id}, Report: {report_id}, Guild: {guild_id}")
    
    @staticmethod
    def log_security_event(event_type: str, details: str, user_id: Optional[int] = None):
        """Log d'un événement de sécurité"""
        logger.warning(f"SECURITY_EVENT - Type: {event_type}, Details: {details}, User: {user_id}")
    
    @staticmethod
    def log_error(error_type: str, error_details: str, user_id: Optional[int] = None):
        """Log d'une erreur"""
        logger.error(f"ERROR - Type: {error_type}, Details: {error_details}, User: {user_id}")

def create_secure_embed(title: str, description: str, color: discord.Color) -> discord.Embed:
    """Crée un embed sécurisé avec validation"""
    # Nettoyer les entrées
    title = SecurityValidator.sanitize_input(title, 256)
    description = SecurityValidator.sanitize_input(description, 4096)
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=discord.utils.utcnow()
    )
    
    return embed

def format_report_id(guild_id: int, timestamp: datetime) -> str:
    """Génère un ID unique pour un signalement"""
    timestamp_str = timestamp.strftime("%Y%m%d%H%M%S")
    return f"AGIS-{guild_id}-{timestamp_str}"