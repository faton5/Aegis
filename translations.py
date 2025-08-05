# Système de traduction pour Aegis Bot
from typing import Dict, Any
from guild_config import guild_config

# Dictionnaires de traduction
TRANSLATIONS = {
    "fr": {
        # Messages généraux
        "report_submitted": "Signalement soumis avec succès",
        "validation_required": "Validation requise par la communauté",
        "permission_denied": "Vous n'avez pas les permissions nécessaires",
        "rate_limited": "Vous avez atteint la limite de signalements par heure",
        "invalid_input": "Données invalides détectées",
        "forum_not_found": "Forum d'alertes non trouvé",
        "setup_required": "Configuration requise. Utilisez /setup d'abord",
        
        # Catégories de signalement
        "harassment": "Harcèlement",
        "inappropriate_content": "Contenu inapproprié",
        "suspicious_behavior": "Comportement suspect", 
        "child_safety": "Sécurité des mineurs",
        "spam": "Spam",
        "scam": "Arnaque",
        "threats": "Menaces",
        "other": "Autre",
        
        # Interface utilisateur
        "report_modal_title": "Signalement Agis - Rapport anonyme",
        "username_label": "Nom d'utilisateur à signaler",
        "username_placeholder": "@utilisateur, pseudo, ou ID Discord (ex: 123456789012345678)...",
        "reason_label": "Motif du signalement",
        "reason_placeholder": "Décrivez les faits observés de manière factuelle...",
        "evidence_label": "Liens et preuves (optionnel)",
        "evidence_placeholder": "Liens de messages, screenshots, logs, autres preuves...",
        "report_button": "Faire un signalement",
        "validate_button": "Valider",
        "reject_button": "Rejeter",
        "details_button": "Demander détails",
        "anonymous_button": "Anonymiser",
        
        # Configuration
        "basic_setup": "Configuration de base",
        "auto_actions": "Actions automatiques", 
        "notifications": "Notifications",
        "thresholds": "Seuils & Limites",
        "quarantine": "Quarantaine",
        "language_selection": "Sélection de langue",
        
        # Statistiques
        "total_reports": "Signalements totaux",
        "validated_reports": "Signalements validés",
        "pending_reports": "En attente",
        "validation_rate": "Taux de validation",
        "active_validators": "Validateurs actifs",
        
        # Diagnostic
        "test_diagnostics": "Tests de diagnostic",
        "security_validator": "Validateur de sécurité",
        "rate_limiter": "Limiteur de taux",
        "supabase_connection": "Connexion Supabase",
        "guild_configuration": "Configuration de guilde",
        "no_bugs_found": "Aucun bug détecté lors des tests !",
        "bugs_detected": "bug(s) détecté(s)",
    },
    
    "en": {
        # General messages
        "report_submitted": "Report submitted successfully",
        "validation_required": "Community validation required",
        "permission_denied": "You don't have the necessary permissions",
        "rate_limited": "You have reached the hourly report limit",
        "invalid_input": "Invalid data detected",
        "forum_not_found": "Alerts forum not found",
        "setup_required": "Configuration required. Use /setup first",
        
        # Report categories
        "harassment": "Harassment",
        "inappropriate_content": "Inappropriate content",
        "suspicious_behavior": "Suspicious behavior",
        "child_safety": "Child safety",
        "spam": "Spam",
        "scam": "Scam",
        "threats": "Threats",
        "other": "Other",
        
        # User interface
        "report_modal_title": "Agis Report - Anonymous Report",
        "username_label": "Username to report",
        "username_placeholder": "@username, display name, or Discord ID (e.g., 123456789012345678)...",
        "reason_label": "Report reason",
        "reason_placeholder": "Describe the observed facts objectively...",
        "evidence_label": "Links and evidence (optional)",
        "evidence_placeholder": "Message links, screenshots, logs, other evidence...",
        "report_button": "Make a report",
        "validate_button": "Validate",
        "reject_button": "Reject",
        "details_button": "Request details",
        "anonymous_button": "Anonymize",
        
        # Configuration
        "basic_setup": "Basic setup",
        "auto_actions": "Automatic actions",
        "notifications": "Notifications", 
        "thresholds": "Thresholds & Limits",
        "quarantine": "Quarantine",
        "language_selection": "Language selection",
        
        # Statistics
        "total_reports": "Total reports",
        "validated_reports": "Validated reports", 
        "pending_reports": "Pending",
        "validation_rate": "Validation rate",
        "active_validators": "Active validators",
        
        # Diagnostics
        "test_diagnostics": "Diagnostic tests",
        "security_validator": "Security validator",
        "rate_limiter": "Rate limiter",
        "supabase_connection": "Supabase connection",
        "guild_configuration": "Guild configuration",
        "no_bugs_found": "No bugs found during tests!",
        "bugs_detected": "bug(s) detected",
    }
}

class TranslationManager:
    """Gestionnaire de traductions pour le bot"""
    
    def __init__(self):
        self.default_language = "fr"
    
    def get_guild_language(self, guild_id: int) -> str:
        """Récupère la langue configurée pour une guilde"""
        config = guild_config.get_guild_config(guild_id)
        return config.get('language', self.default_language)
    
    def set_guild_language(self, guild_id: int, language: str) -> bool:
        """Définit la langue pour une guilde"""
        if language not in TRANSLATIONS:
            return False
        
        guild_config.update_guild_config(guild_id, {'language': language})
        return True
    
    def t(self, key: str, guild_id: int = None, language: str = None, fallback: str = None) -> str:
        """
        Traduit une clé selon la langue de la guilde
        
        Args:
            key: Clé de traduction
            guild_id: ID de la guilde (optionnel)
            language: Langue forcée (optionnel)
        
        Returns:
            Texte traduit ou clé si non trouvée
        """
        if language:
            lang = language
        elif guild_id:
            lang = self.get_guild_language(guild_id)
        else:
            lang = self.default_language
        
        if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
            return TRANSLATIONS[lang][key]
        
        # Fallback vers français puis anglais
        for fallback_lang in ['fr', 'en']:
            if fallback_lang in TRANSLATIONS and key in TRANSLATIONS[fallback_lang]:
                return TRANSLATIONS[fallback_lang][key]
        
        # Retourne le fallback ou la clé si aucune traduction trouvée
        return fallback if fallback else key
    
    def get_available_languages(self) -> Dict[str, str]:
        """Retourne la liste des langues disponibles"""
        return {
            "fr": "🇫🇷 Français",
            "en": "🇬🇧 English"
        }
    
    def get_categories_translated(self, guild_id: int) -> Dict[str, str]:
        """Retourne les catégories traduites pour une guilde"""
        categories = {}
        for key in ["harassment", "inappropriate_content", "suspicious_behavior", 
                   "child_safety", "spam", "scam", "threats", "other"]:
            # Emoji + traduction
            emoji_map = {
                "harassment": "🚨",
                "inappropriate_content": "🔞", 
                "suspicious_behavior": "👁️",
                "child_safety": "🛡️",
                "spam": "📢",
                "scam": "💰",
                "threats": "⚔️",
                "other": "❓"
            }
            emoji = emoji_map.get(key, "")
            translation = self.t(key, guild_id)
            categories[key] = f"{emoji} {translation}"
        
        return categories

# Instance globale du gestionnaire de traductions
translator = TranslationManager()