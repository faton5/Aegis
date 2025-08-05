# Configuration centralisée pour le bot Aegis
import os
from typing import Dict, Any

# Configuration du bot
BOT_CONFIG = {
    "ALERTS_CHANNEL_NAME": "agis-alerts",
    "VALIDATOR_ROLE_NAME": "Validateur", 
    "QUORUM_PERCENTAGE": 80,
    "MAX_REPORTS_PER_USER_PER_HOUR": 3,
    "VALIDATION_TIMEOUT_HOURS": 48,
    "AUTO_ARCHIVE_DURATION": 60,
    "MAX_REPORT_LENGTH": 1000,
    "MAX_EVIDENCE_LENGTH": 1000,
    "MAX_USERNAME_LENGTH": 100,
    # Configuration Supabase
    "SUPABASE_ENABLED": True,
    "AUTO_CHECK_NEW_MEMBERS": True,
    "FLAG_ALERT_CHANNEL": "agis-flags",  # Canal pour les alertes de flags centralisés
    "MINIMUM_VALIDATION_COUNT": 2,  # Nombre minimum de serveurs validateurs avant centralisation
    # Configuration de test et debug
    "TEST_MODE_ENABLED": os.getenv("AEGIS_TEST_MODE", "false").lower() in ["true", "1", "yes", "oui"]
}

# Catégories prédéfinies pour les signalements
REPORT_CATEGORIES = {
    "harassment": "🚨 Harcèlement",
    "inappropriate_content": "🔞 Contenu inapproprié", 
    "suspicious_behavior": "👁️ Comportement suspect",
    "child_safety": "🛡️ Sécurité des mineurs",
    "spam": "📢 Spam",
    "scam": "💰 Arnaque",
    "threats": "⚔️ Menaces",
    "other": "❓ Autre"
}

# Messages d'erreur standardisés
ERROR_MESSAGES = {
    "no_permission": "❌ Vous n'avez pas les permissions nécessaires.",
    "rate_limited": "⏰ Vous avez atteint la limite de signalements par heure. Réessayez plus tard.",
    "invalid_input": "❌ Données invalides détectées.",
    "forum_not_found": f"❌ Forum #{BOT_CONFIG['ALERTS_CHANNEL_NAME']} non trouvé.",
    "setup_required": "⚙️ Configuration requise. Utilisez /setup d'abord.",
    "validation_expired": "⏰ Délai de validation expiré."
}

# Configuration des logs
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "aegis_bot.log",
    "max_bytes": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

def validate_config() -> bool:
    """Valide la configuration du bot"""
    required_env = ["DISCORD_TOKEN"]
    
    # Ajouter les variables Supabase si activé
    if BOT_CONFIG["SUPABASE_ENABLED"]:
        required_env.extend(["SUPABASE_URL", "SUPABASE_KEY"])
    
    for env_var in required_env:
        if not os.getenv(env_var):
            print(f"[ERREUR] Variable d'environnement manquante: {env_var}")
            return False
    
    if BOT_CONFIG["QUORUM_PERCENTAGE"] < 1 or BOT_CONFIG["QUORUM_PERCENTAGE"] > 100:
        print("[ERREUR] QUORUM_PERCENTAGE doit être entre 1 et 100")
        return False
        
    return True