"""
Configuration centralisée du bot Aegis
"""
from dataclasses import dataclass
from typing import Dict, Any, List
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

@dataclass
class BotSettings:
    """Configuration principale du bot"""
    # Discord
    token: str = ""
    
    # Canaux et rôles
    alerts_channel_name: str = "agis-alerts"
    validator_role_name: str = "Validateur"
    
    # Limites
    quorum_percentage: int = 80
    max_reports_per_hour: int = 3
    max_evidence_length: int = 1900
    
    # Features
    supabase_enabled: bool = True
    test_mode_enabled: bool = False
    debug_enabled: bool = False
    
    def __post_init__(self):
        """Charger les valeurs depuis les variables d'environnement"""
        self.token = os.getenv('DISCORD_TOKEN', '')
        self.supabase_enabled = os.getenv('SUPABASE_ENABLED', 'true').lower() == 'true'
        self.test_mode_enabled = os.getenv('TEST_MODE_ENABLED', 'false').lower() == 'true'
        self.debug_enabled = os.getenv('DEBUG_ENABLED', 'false').lower() == 'true'


# Configuration des catégories de signalement
REPORT_CATEGORIES = {
    "harassment": {
        "label": "🚫 Harassment",
        "description": "Harassment, threats or intimidation",
        "severity": "high"
    },
    "inappropriate_content": {
        "label": "📵 Inappropriate Content", 
        "description": "Sexual, violent or disturbing content",
        "severity": "medium"
    },
    "suspicious_behavior": {
        "label": "🔍 Suspicious Behavior",
        "description": "Suspicious activity or manipulation",
        "severity": "medium"
    },
    "child_safety": {
        "label": "🛡️ Child Safety",
        "description": "Potential danger to minors",
        "severity": "critical"
    },
    "spam": {
        "label": "📢 Spam/Flood",
        "description": "Repetitive or unsolicited messages", 
        "severity": "low"
    },
    "scam": {
        "label": "💰 Scam/Phishing",
        "description": "Scam or phishing attempt",
        "severity": "high"
    },
    "threats": {
        "label": "⚔️ Threats",
        "description": "Threats of violence or harm",
        "severity": "critical"
    },
    "other": {
        "label": "❓ Other",
        "description": "Other reason for reporting",
        "severity": "low"
    }
}

# Messages d'erreur standardisés
ERROR_MESSAGES = {
    "guild_not_configured": "❌ This server is not configured to use Aegis.",
    "missing_permissions": "❌ You don't have the necessary permissions.",
    "rate_limited": "⏰ You must wait before making another report.",
    "invalid_input": "❌ The provided data is not valid.",
    "database_error": "❌ Database error. Please try again later.",
    "user_not_found": "❌ User not found or inaccessible.",
}

# Instance globale de configuration
bot_settings = BotSettings()

def validate_config() -> bool:
    """Valider la configuration du bot"""
    if not bot_settings.token:
        print("❌ DISCORD_TOKEN missing")
        return False
    
    if bot_settings.quorum_percentage < 1 or bot_settings.quorum_percentage > 100:
        print("❌ QUORUM_PERCENTAGE must be between 1 and 100")
        return False
        
    return True