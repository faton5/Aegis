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
        "select_category_placeholder": "Sélectionnez une catégorie de signalement...",
        "select_proof_placeholder": "Votre rapport repose-t-il sur une preuve ?",
        "proof_yes": "Oui",
        "proof_yes_desc": "J'ai des preuves (captures, liens, etc.)",
        "proof_no": "Non", 
        "proof_no_desc": "Pas de preuve directe disponible",
        "report_modal_title": "Signalement Agis - Rapport anonyme",
        "username_label": "Nom d'utilisateur à signaler",
        "username_placeholder": "@utilisateur, pseudo, ou ID Discord (ex: 123456789012345678)...",
        "reason_label": "Motif du signalement",
        "reason_placeholder": "Décrivez les faits observés de manière factuelle...",
        "evidence_label": "Liens et preuves (optionnel)",
        "evidence_placeholder": "Liens de messages, screenshots, logs, autres preuves...",
        "report_title": "🛡️ Signalement Agis",
        "select_category_description": "Sélectionnez la catégorie de votre signalement :",
        "report_step2_title": "🛡️ Signalement Agis - Étape 2",
        "category_selected": "Catégorie sélectionnée",
        "proof_question": "Votre rapport repose-t-il sur une preuve ?",
        
        # Descriptions des catégories
        "harassment_desc": "Comportement de harcèlement",
        "inappropriate_content_desc": "Contenu NSFW ou inapproprié",
        "suspicious_behavior_desc": "Activité suspecte",
        "child_safety_desc": "Risques pour les mineurs",
        "spam_desc": "Messages répétitifs ou indésirables",
        "scam_desc": "Tentative d'escroquerie",
        "threats_desc": "Menaces ou violence",
        "other_desc": "Autre type de problème",
        
        # Messages d'erreur pour /aegis
        "bot_not_configured": "Le bot Agis n'est pas encore configuré sur ce serveur.",
        "missing_elements": "🔧 Éléments manquants",
        "for_admins": "👑 Pour les administrateurs",
        "use_setup": "Utilisez `/setup` pour configurer automatiquement le bot.",
        "what_does_setup": "💡 Que fait /setup ?",
        "setup_description": "• Crée le forum pour les signalements\n• Crée le rôle pour les validateurs\n• Configure les permissions",
        "config_required": "Configuration requise avant utilisation",
        "invalid_username": "Nom d'utilisateur invalide",
        "duplicate_report": "Signalement similaire déjà soumis récemment",
        "report_submitted_success": "a été soumis avec succès",
        "additional_evidence_title": "📨 Signalement Agis - Preuves supplémentaires",
        "send_evidence_prompt": "💡 Vous pouvez maintenant envoyer des preuves", 
        
        # Embeds de signalement du forum
        "new_report_title": "🛡️ Nouveau signalement Agis",
        "new_report_description": "Un nouveau signalement anonyme a été reçu",
        "report_id_field": "🆔 ID Signalement",
        "reported_user_field": "👤 Utilisateur signalé", 
        "category_field": "📂 Catégorie",
        "reason_field": "📝 Motif",
        "links_evidence_field": "🔗 Liens et preuves",
        "proof_available_field": "✅ Preuve disponible",
        "report_date_field": "🕐 Date du signalement",
        "report_footer": "Signalement anonyme • En attente de validation",
        "yes": "Oui",
        "no": "Non",
        
        # Messages DM preuves
        "report_submitted_dm": "Votre signalement **{report_id}** a été soumis avec succès.",
        "evidence_instructions": "Répondez à ce message privé avec :\n• Captures d'écran\n• Liens de messages Discord\n• Fichiers texte ou logs\n• Toute autre preuve pertinente",
        "evidence_timeout": "⏰ Délai: Vous avez 24h pour envoyer vos preuves",
        "anonymity_preserved": "🔒 **Votre anonymat** est préservé - les preuves seront transférées sans révéler votre identité.",
        "stop_evidence": "🚫 Pour arrêter",
        "stop_evidence_instructions": "Envoyez simplement le mot `STOP` pour ne plus recevoir de demandes de preuves.",
        "evidence_footer": "ID: {report_id} • Expire dans 24h",
        
        # Messages de succès
        "report_success_with_dm": "✅ **Signalement soumis avec succès !**\n\n📨 Un message privé vous a été envoyé pour collecter d'éventuelles preuves supplémentaires.\n\n🆔 **ID de votre signalement :** `{report_id}`",
        "report_success_no_dm": "✅ **Signalement soumis avec succès !**\n\n❌ Impossible d'envoyer un message privé (DM fermés).\n\n🆔 **ID de votre signalement :** `{report_id}`",
        
        # Messages de validation/rejet
        "validate_button": "✅ Valider",
        "reject_button": "❌ Rejeter", 
        "request_details_button": "📩 Demander détails",
        "anonymize_button": "🔒 Anonymiser",
        "already_finalized": "ℹ️ Ce signalement a déjà été finalisé.",
        "already_validated": "⚠️ Vous avez déjà validé ce signalement.",
        "already_rejected": "⚠️ Vous avez déjà rejeté ce signalement.",
        "report_validated": "✅ Signalement validé",
        "validated_by": "Validé par {validator}",
        "report_rejected": "❌ Signalement rejeté",
        "rejected_by": "Rejeté par {validator}",
        "progress": "Progression",
        "reject_progress": "Progression rejet",
        
        "report_button": "Faire un signalement",
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
        "select_category_placeholder": "Select a report category...",
        "select_proof_placeholder": "Is your report based on evidence?",
        "proof_yes": "Yes",
        "proof_yes_desc": "I have evidence (screenshots, links, etc.)",
        "proof_no": "No",
        "proof_no_desc": "No direct evidence available",
        "report_modal_title": "Agis Report - Anonymous Report",
        "username_label": "Username to report",
        "username_placeholder": "@username, display name, or Discord ID (e.g., 123456789012345678)...",
        "reason_label": "Report reason",
        "reason_placeholder": "Describe the observed facts objectively...",
        "evidence_label": "Links and evidence (optional)",
        "evidence_placeholder": "Message links, screenshots, logs, other evidence...",
        "report_title": "🛡️ Agis Report",
        "select_category_description": "Select the category for your report:",
        "report_step2_title": "🛡️ Agis Report - Step 2",
        "category_selected": "Selected category",
        "proof_question": "Is your report based on evidence?",
        
        # Category descriptions
        "harassment_desc": "Harassment behavior",
        "inappropriate_content_desc": "NSFW or inappropriate content",
        "suspicious_behavior_desc": "Suspicious activity",
        "child_safety_desc": "Risks to minors",
        "spam_desc": "Repetitive or unwanted messages",
        "scam_desc": "Fraud attempt",
        "threats_desc": "Threats or violence",
        "other_desc": "Other type of problem",
        
        # Error messages for /aegis
        "bot_not_configured": "The Agis bot is not yet configured on this server.",
        "missing_elements": "🔧 Missing elements",
        "for_admins": "👑 For administrators",
        "use_setup": "Use `/setup` to automatically configure the bot.",
        "what_does_setup": "💡 What does /setup do?",
        "setup_description": "• Creates the forum for reports\n• Creates the role for validators\n• Configures permissions",
        "config_required": "Configuration required before use",
        "invalid_username": "Invalid username",
        "duplicate_report": "Similar report already submitted recently",
        "report_submitted_success": "has been submitted successfully",
        "additional_evidence_title": "📨 Agis Report - Additional Evidence",
        "send_evidence_prompt": "💡 You can now send evidence",
        
        # Forum report embeds
        "new_report_title": "🛡️ New Agis Report",
        "new_report_description": "A new anonymous report has been received",
        "report_id_field": "🆔 Report ID",
        "reported_user_field": "👤 Reported user", 
        "category_field": "📂 Category",
        "reason_field": "📝 Reason",
        "links_evidence_field": "🔗 Links and evidence",
        "proof_available_field": "✅ Evidence available",
        "report_date_field": "🕐 Report date",
        "report_footer": "Anonymous report • Awaiting validation",
        "yes": "Yes",
        "no": "No",
        
        # DM evidence messages
        "report_submitted_dm": "Your report **{report_id}** has been submitted successfully.",
        "evidence_instructions": "Reply to this private message with:\n• Screenshots\n• Discord message links\n• Text files or logs\n• Any other relevant evidence",
        "evidence_timeout": "⏰ Deadline: You have 24h to send your evidence",
        "anonymity_preserved": "🔒 **Your anonymity** is preserved - evidence will be transferred without revealing your identity.",
        "stop_evidence": "🚫 To stop",
        "stop_evidence_instructions": "Simply send the word `STOP` to stop receiving evidence requests.",
        "evidence_footer": "ID: {report_id} • Expires in 24h",
        
        # Success messages
        "report_success_with_dm": "✅ **Report submitted successfully!**\n\n📨 A private message has been sent to collect any additional evidence.\n\n🆔 **Your report ID:** `{report_id}`",
        "report_success_no_dm": "✅ **Report submitted successfully!**\n\n❌ Unable to send private message (DMs closed).\n\n🆔 **Your report ID:** `{report_id}`",
        
        # Validation/rejection messages
        "validate_button": "✅ Validate",
        "reject_button": "❌ Reject", 
        "request_details_button": "📩 Request details",
        "anonymize_button": "🔒 Anonymize",
        "already_finalized": "ℹ️ This report has already been finalized.",
        "already_validated": "⚠️ You have already validated this report.",
        "already_rejected": "⚠️ You have already rejected this report.",
        "report_validated": "✅ Report validated",
        "validated_by": "Validated by {validator}",
        "report_rejected": "❌ Report rejected",
        "rejected_by": "Rejected by {validator}",
        "progress": "Progress",
        "reject_progress": "Rejection progress",
        
        "report_button": "Make a report",
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