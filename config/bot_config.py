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
        "label": "🚫 Harcèlement",
        "description": "Harcèlement, menaces ou intimidation",
        "severity": "high"
    },
    "inappropriate_content": {
        "label": "📵 Contenu inapproprié", 
        "description": "Contenu sexuel, violent ou dérangeant",
        "severity": "medium"
    },
    "suspicious_behavior": {
        "label": "🔍 Comportement suspect",
        "description": "Activité suspecte ou manipulation",
        "severity": "medium"
    },
    "child_safety": {
        "label": "🛡️ Sécurité des mineurs",
        "description": "Danger potentiel pour les mineurs",
        "severity": "critical"
    },
    "spam": {
        "label": "📢 Spam/Flood",
        "description": "Messages répétitifs ou non sollicités", 
        "severity": "low"
    },
    "scam": {
        "label": "💰 Arnaque/Phishing",
        "description": "Tentative d'arnaque ou de phishing",
        "severity": "high"
    },
    "threats": {
        "label": "⚔️ Menaces",
        "description": "Menaces de violence ou de mal",
        "severity": "critical"
    },
    "other": {
        "label": "❓ Autre",
        "description": "Autre motif de signalement",
        "severity": "low"
    }
}

# Messages d'erreur standardisés
ERROR_MESSAGES = {
    "guild_not_configured": "❌ Ce serveur n'est pas configuré pour utiliser Aegis.",
    "missing_permissions": "❌ Vous n'avez pas les permissions nécessaires.",
    "rate_limited": "⏰ Vous devez attendre avant de faire un nouveau signalement.",
    "invalid_input": "❌ Les données fournies ne sont pas valides.",
    "database_error": "❌ Erreur de base de données. Réessayez plus tard.",
    "user_not_found": "❌ Utilisateur non trouvé ou inaccessible.",
}

# Instance globale de configuration
bot_settings = BotSettings()

def validate_config() -> bool:
    """Valider la configuration du bot"""
    if not bot_settings.token:
        print("❌ DISCORD_TOKEN manquant")
        return False
    
    if bot_settings.quorum_percentage < 1 or bot_settings.quorum_percentage > 100:
        print("❌ QUORUM_PERCENTAGE doit être entre 1 et 100")
        return False
        
    return True