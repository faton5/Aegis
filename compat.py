"""
Fichier de compatibilité pour les anciens imports
Permet aux anciens scripts de continuer à fonctionner
"""

# Imports de compatibilité pour guild_config
from services.guild_service import guild_service as guild_config

# Imports de compatibilité pour translations
from locales.translation_manager import translator

# Imports de compatibilité pour utils
from utils.security import SecurityValidator
from utils.rate_limiter import RateLimiter

# Imports de compatibilité pour config
from config.bot_config import bot_settings as BOT_CONFIG, REPORT_CATEGORIES, ERROR_MESSAGES

# Fonction utilitaire commune
def create_secure_embed(title: str, description: str, color=None):
    """Fonction utilitaire pour créer des embeds sécurisés"""
    import discord
    
    validator = SecurityValidator()
    
    # Nettoyer les entrées
    safe_title = validator.sanitize_input(title, max_length=256)
    safe_description = validator.sanitize_input(description, max_length=4096)
    
    embed = discord.Embed(
        title=safe_title,
        description=safe_description,
        color=color or discord.Color.blue()
    )
    
    return embed

# Logger de compatibilité
from config.logging_config import get_logger
logger = get_logger('compat')