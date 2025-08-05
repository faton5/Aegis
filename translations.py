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
        
        # Messages de configuration - erreur forum manquant
        "configuration_missing": "❌ Configuration manquante",
        "bot_not_configured_modal": "Le bot Agis n'est pas encore configuré sur ce serveur.",
        "solution": "🔧 Solution",
        "solution_description": "Un administrateur doit exécuter `/setup` pour créer :\n• Le forum `#{forum_name}`\n• Le rôle `@{role_name}`",
        "administrators": "👑 Administrateurs",
        "administrators_setup": "Utilisez `/setup` pour configurer le bot automatiquement.",
        "report_not_processed": "Votre signalement n'a pas pu être traité",
        
        # Messages de validation des boutons (suite)
        "validation_title": "✅ Signalement validé",
        "validated_by_user": "Validé par {user}",
        "rejection_title": "❌ Signalement rejeté", 
        "rejected_by_user": "Rejeté par {user}",
        "must_have_validator_role": "❌ Vous devez avoir le rôle '{role}' pour valider ce signalement.",
        "must_have_validator_role_reject": "❌ Vous devez avoir le rôle '{role}' pour rejeter ce signalement.",
        
        # Messages de demande de détails
        "must_have_validator_role_details": "❌ Vous devez avoir le rôle '{role}' ou être administrateur.",
        "report_not_in_window": "⚠️ Ce signalement n'est plus dans la fenêtre de collecte de preuves (>24h ou déjà anonymisé).",
        "details_request_title": "📩 Demande de détails supplémentaires",
        "details_request_description": "Un modérateur souhaite obtenir plus d'informations sur votre signalement **{report_id}**.",
        "requested_by": "👤 Demandé par",
        "requested_by_moderator": "Modérateur du serveur {guild_name}",
        "question": "💬 Question",
        "question_more_details": "Pouvez-vous fournir plus de détails ou de preuves concernant ce signalement ?",
        "how_to_respond": "📝 Comment répondre",
        "how_to_respond_description": "Répondez à ce message privé avec les informations supplémentaires. Vos preuves seront transférées anonymement.",
        "details_request_footer": "Signalement: {report_id} • Demande de détails",
        "details_request_sent": "✅ Demande de détails envoyée au rapporteur pour le signalement `{report_id}`.",
        "cannot_contact_reporter": "❌ Impossible de contacter le rapporteur (utilisateur introuvable).",
        "cannot_send_dm_reporter": "❌ Impossible d'envoyer un DM au rapporteur (paramètres de confidentialité).",
        "error_sending_details_request": "❌ Erreur lors de l'envoi de la demande de détails.",
        
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
        
        # Messages hardcodés supplémentaires
        "already_rejected_user": "⚠️ Vous avez déjà rejeté ce signalement.",
        "rejection_progress_title": "❌ Signalement rejeté",
        "rejected_by_display": "Rejeté par {user}",
        "rejection_progress": "Progression rejet",
        "must_have_validator_role_reject_details": "❌ Vous devez avoir le rôle '{role}' pour rejeter ce signalement.",
        "request_details_deprecated": "📩 Demander détails",
        
        # Messages des demandes de détails dans request_details_button
        "must_have_validator_admin_role": "❌ Vous devez avoir le rôle '{role}' ou être administrateur.",
        "report_not_in_collection_window": "⚠️ Ce signalement n'est plus dans la fenêtre de collecte de preuves (>24h ou déjà anonymisé).",
        "additional_details_request_title": "📩 Demande de détails supplémentaires",
        "moderator_wants_info": "Un modérateur souhaite obtenir plus d'informations sur votre signalement **{report_id}**.",
        "requested_by_field": "👤 Demandé par",
        "moderator_from_server": "Modérateur du serveur {guild_name}",
        "question_field": "💬 Question",
        "can_you_provide_details": "Pouvez-vous fournir plus de détails ou de preuves concernant ce signalement ?",
        "how_to_respond_field": "📝 Comment répondre",
        "respond_with_additional_info": "Répondez à ce message privé avec les informations supplémentaires. Vos preuves seront transférées anonymement.",
        "details_request_footer_text": "Signalement: {report_id} • Demande de détails",
        "details_request_sent_success": "✅ Demande de détails envoyée au rapporteur pour le signalement `{report_id}`.",
        "cannot_contact_reporter_not_found": "❌ Impossible de contacter le rapporteur (utilisateur introuvable).",
        "cannot_send_dm_privacy": "❌ Impossible d'envoyer un DM au rapporteur (paramètres de confidentialité).",
        "error_sending_details_req": "❌ Erreur lors de l'envoi de la demande de détails.",
        
        # Messages de finalisation de validation
        "report_validated_centralized": "🎉 Signalement validé et centralisé !",
        "quorum_reached_centralized": "Le quorum de validation a été atteint pour le signalement `{report_id}`.\nL'utilisateur signalé a été ajouté à la base de données centralisée.",
        "report_validated_not_centralized": "⚠️ Signalement validé mais non centralisé",
        "quorum_reached_not_centralized": "Le quorum de validation a été atteint pour le signalement `{report_id}`.\n⚠️ **L'utilisateur n'a pas pu être identifié** (utilisez @mention ou ID Discord pour la centralisation).",
        "statistics_field": "📈 Statistiques",
        "validators_rejectors": "Validateurs: {validators}\nRejeteurs: {rejectors}",
        "centralized_database_field": "🌐 Base centralisée",
        "centralized_success": "✅ Centralisé",
        "centralized_failed": "⚠️ Échec centralisation",
        
        # Messages de finalisation de rejet
        "report_rejected_community": "❌ Signalement rejeté par la communauté",
        "rejection_quorum_reached": "Le quorum de rejet a été atteint pour le signalement `{report_id}`.\nCe signalement a été rejeté par la communauté.",
        
        # Messages d'erreur agis_report
        "configuration_missing_title": "❌ Configuration manquante",
        
        # Messages de la commande anonymiser
        "admin_validator_only": "❌ Cette commande est réservée aux administrateurs et validateurs.",
        "report_anonymized_success": "✅ Signalement anonymisé",
        "anonymization_link_removed": "Le lien d'anonymat pour le signalement `{report_id}` a été supprimé.",
        "consequences_field": "🔒 Conséquences",
        "consequences_description": "• L'utilisateur ne peut plus envoyer de preuves\n• Le lien temporaire a été détruit\n• L'anonymat est maintenant permanent",
        "report_not_found_warning": "⚠️ Signalement non trouvé",
        "no_active_report_found": "Aucun signalement actif trouvé avec l'ID `{report_id}`.",
        "possible_causes_field": "💡 Possible causes",
        "possible_causes_description": "• Signalement déjà expiré (>24h)\n• ID incorrect\n• Déjà anonymisé",
        "no_active_reports": "📭 Aucun signalement actif",
        "no_reports_collecting": "Il n'y a actuellement aucun signalement en cours de collecte de preuves.",
        "active_reports_title": "📋 Signalements actifs",
        "active_reports_description": "**{count}** signalements en cours de collecte de preuves :",
        "reports_list_field": "🕐 Liste des signalements",
        "expires_in_hours": "• `{report_id}` - Expire dans {hours:.1f}h",
        "usage_field": "💡 Usage",
        "usage_description": "Utilisez `/anonymiser report_id:<ID>` pour anonymiser un signalement spécifique",
        
        # Commande categories
        "categories_title": "📂 Catégories de signalement Agis",
        "categories_description": "Voici les catégories disponibles pour vos signalements :",
        "use_category": "Utilisez : `{category}`",
        "advice_field": "💡 Conseil",
        "advice_description": "Copiez-collez la catégorie souhaitée dans le champ 'Catégorie du signalement' lors de l'utilisation de `/agis`",
        "footer_protection": "Protection • Vigilance • Communauté",
        
        # Commande validate
        "report_validation_title": "✅ Validation de signalement",
        "can_use_validation": "Vous pouvez utiliser cette commande pour valider un signalement.",
        "access_denied": "❌ Accès refusé",
        "need_validator_role": "Vous devez avoir le rôle '{role}' pour utiliser cette commande.",
        
        # Commande check
        "need_admin_validator": "Vous devez être administrateur ou avoir le rôle '{role}' pour utiliser cette commande.",
        "service_unavailable": "⚠️ Service indisponible",
        "centralized_check_disabled": "La vérification centralisée n'est pas activée.",
        "flagged_user_detected": "🚨 Utilisateur flagué détecté",
        "user_flagged_centralized": "L'utilisateur {user} est flagué dans la base centralisée",
        "user_field": "👤 Utilisateur",
        "flag_level_field": "🔴 Niveau de flag",
        "category_field_check": "📂 Catégorie",
        "reason_field_check": "⚠️ Raison",
        "flagged_by_field": "🏠 Flagué par",
        "unknown_server": "Serveur inconnu",
        "validations_field": "📊 Validations",
        "servers_count": "{count} serveur(s)",
        "flagged_date_field": "📅 Flagué le",
        "footer_manual_check": "Vérification manuelle • Base centralisée Aegis",
        
        # Messages pour utilisateur non flagué
        "user_verified": "✅ Utilisateur vérifié",
        "user_not_flagged": "L'utilisateur {user} n'est pas flagué dans la base centralisée",
        "status_field": "✅ Statut",
        "no_flag_found": "Aucun flag trouvé",
        "verification_field": "🔍 Vérification",
        "centralized_db_consulted": "Base centralisée consultée",
        
        # Messages test_commands.py
        "bug_detected_log": "🐛 BUG DÉTECTÉ - Test: {test_name} | Erreur: {error} | Contexte: {context}",
        "traceback_log": "🐛 TRACEBACK: {traceback}",
        "no_bugs_detected_summary": "✅ Aucun bug détecté lors des tests !",
        "bugs_detected_summary": "🐛 **{count} bug(s) détecté(s):**\n\n",
        "bug_entry_name": "**{i}.** `{test_name}`\n",
        "bug_entry_error": "   • Erreur: `{error_type}: {error_message}`\n",
        "bug_entry_context": "   • Contexte: {context}\n",
        "bug_entry_timestamp": "   • Horodatage: {timestamp}\n\n",
        "test_normal": "Test normal",
        "normal_user": "Utilisateur normal",
        "test_script": "Test script",
        "test_sql": "Test SQL",
        "test_length": "Test longueur",
        "test_special_chars": "Test caractères spéciaux",
        "special_chars_content": "Test avec émojis 🚨🔞",
        "test_valid_sanitized": "✅ {name}: Valide={is_valid}, Longueur sanitisée={length}",
        "test_error": "❌ {name}: ERREUR - {error}",
        "attempt_allowed": "✅ Tentative {attempt}: Autorisée",
        "rate_limit_premature": "❌ Tentative {attempt}: Rate limit prématuré",
        "attempt_blocked": "✅ Tentative {attempt}: Correctement bloquée",
        "should_be_blocked": "❌ Tentative {attempt}: Devrait être bloquée",
        "general_error": "❌ Erreur générale: {error}",
        "supabase_disabled_warning": "⚠️ Supabase désactivé dans la configuration",
        "supabase_connection_ok": "✅ Connexion Supabase: OK",
        "supabase_connection_fail": "❌ Connexion Supabase: ÉCHEC",
        "supabase_error": "❌ Erreur Supabase: {error}",
        "guilds_configured": "✅ Guildes configurées: {count}",
        "guild_config_ok": "✅ Guild {guild_id}: Configuration OK",
        "guild_config_empty": "❌ Guild {guild_id}: Configuration vide",
        "guild_config_error": "❌ Guild {guild_id}: Erreur - {error}",
        "guild_config_general_error": "❌ Erreur générale guild config: {error}",
        "test_mode_only": "❌ Cette commande n'est disponible qu'en mode test.\nPour l'activer, définissez la variable d'environnement `AEGIS_TEST_MODE=true`",
        "diagnostic_rapid_title": "🔧 Diagnostic Rapide - Système Aegis",
        "diagnostic_results": "Résultats des tests de base",
        "security_validator_field": "🔒 Validateur sécurité",
        "rate_limiter_field": "⏰ Rate limiter",
        "supabase_field": "🗄️ Supabase",
        "general_status_field": "📋 Statut général",
        "system_operational": "✅ Système opérationnel",
        "checks_needed": "⚠️ Vérifications nécessaires",
        "diagnostic_footer": "Diagnostic rapide terminé • Version simplifiée",
        "diagnostic_error": "❌ Erreur lors du diagnostic: {error}",
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
        
        # Configuration error messages - missing forum
        "configuration_missing": "❌ Configuration missing",
        "bot_not_configured_modal": "The Agis bot is not yet configured on this server.",
        "solution": "🔧 Solution",
        "solution_description": "An administrator must run `/setup` to create:\n• The forum `#{forum_name}`\n• The role `@{role_name}`",
        "administrators": "👑 Administrators",
        "administrators_setup": "Use `/setup` to configure the bot automatically.",
        "report_not_processed": "Your report could not be processed",
        
        # Button validation messages (continued)
        "validation_title": "✅ Report validated",
        "validated_by_user": "Validated by {user}",
        "rejection_title": "❌ Report rejected", 
        "rejected_by_user": "Rejected by {user}",
        "must_have_validator_role": "❌ You must have the '{role}' role to validate this report.",
        "must_have_validator_role_reject": "❌ You must have the '{role}' role to reject this report.",
        
        # Details request messages
        "must_have_validator_role_details": "❌ You must have the '{role}' role or be an administrator.",
        "report_not_in_window": "⚠️ This report is no longer in the evidence collection window (>24h or already anonymized).",
        "details_request_title": "📩 Request for additional details",
        "details_request_description": "A moderator wants more information about your report **{report_id}**.",
        "requested_by": "👤 Requested by",
        "requested_by_moderator": "Moderator from server {guild_name}",
        "question": "💬 Question",
        "question_more_details": "Can you provide more details or evidence regarding this report?",
        "how_to_respond": "📝 How to respond",
        "how_to_respond_description": "Reply to this private message with additional information. Your evidence will be transferred anonymously.",
        "details_request_footer": "Report: {report_id} • Details request",
        "details_request_sent": "✅ Details request sent to reporter for report `{report_id}`.",
        "cannot_contact_reporter": "❌ Unable to contact reporter (user not found).",
        "cannot_send_dm_reporter": "❌ Unable to send DM to reporter (privacy settings).",
        "error_sending_details_request": "❌ Error sending details request.",
        
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
        
        # Additional hardcoded messages
        "already_rejected_user": "⚠️ You have already rejected this report.",
        "rejection_progress_title": "❌ Report rejected",
        "rejected_by_display": "Rejected by {user}",
        "rejection_progress": "Rejection progress",
        "must_have_validator_role_reject_details": "❌ You must have the '{role}' role to reject this report.",
        "request_details_deprecated": "📩 Request details",
        
        # Details request messages in request_details_button
        "must_have_validator_admin_role": "❌ You must have the '{role}' role or be an administrator.",
        "report_not_in_collection_window": "⚠️ This report is no longer in the evidence collection window (>24h or already anonymized).",
        "additional_details_request_title": "📩 Request for additional details",
        "moderator_wants_info": "A moderator wants more information about your report **{report_id}**.",
        "requested_by_field": "👤 Requested by",
        "moderator_from_server": "Moderator from server {guild_name}",
        "question_field": "💬 Question",
        "can_you_provide_details": "Can you provide more details or evidence regarding this report?",
        "how_to_respond_field": "📝 How to respond",
        "respond_with_additional_info": "Reply to this private message with additional information. Your evidence will be transferred anonymously.",
        "details_request_footer_text": "Report: {report_id} • Details request",
        "details_request_sent_success": "✅ Details request sent to reporter for report `{report_id}`.",
        "cannot_contact_reporter_not_found": "❌ Unable to contact reporter (user not found).",
        "cannot_send_dm_privacy": "❌ Unable to send DM to reporter (privacy settings).",
        "error_sending_details_req": "❌ Error sending details request.",
        
        # Validation finalization messages
        "report_validated_centralized": "🎉 Report validated and centralized!",
        "quorum_reached_centralized": "The validation quorum has been reached for report `{report_id}`.\nThe reported user has been added to the centralized database.",
        "report_validated_not_centralized": "⚠️ Report validated but not centralized",
        "quorum_reached_not_centralized": "The validation quorum has been reached for report `{report_id}`.\n⚠️ **The user could not be identified** (use @mention or Discord ID for centralization).",
        "statistics_field": "📈 Statistics",
        "validators_rejectors": "Validators: {validators}\nRejectors: {rejectors}",
        "centralized_database_field": "🌐 Centralized database",
        "centralized_success": "✅ Centralized",
        "centralized_failed": "⚠️ Centralization failed",
        
        # Rejection finalization messages
        "report_rejected_community": "❌ Report rejected by community",
        "rejection_quorum_reached": "The rejection quorum has been reached for report `{report_id}`.\nThis report has been rejected by the community.",
        
        # Error messages agis_report
        "configuration_missing_title": "❌ Missing configuration",
        
        # Anonymize command messages
        "admin_validator_only": "❌ This command is reserved for administrators and validators.",
        "report_anonymized_success": "✅ Report anonymized",
        "anonymization_link_removed": "The anonymity link for report `{report_id}` has been removed.",
        "consequences_field": "🔒 Consequences",
        "consequences_description": "• User can no longer send evidence\n• Temporary link has been destroyed\n• Anonymity is now permanent",
        "report_not_found_warning": "⚠️ Report not found",
        "no_active_report_found": "No active report found with ID `{report_id}`.",
        "possible_causes_field": "💡 Possible causes",
        "possible_causes_description": "• Report already expired (>24h)\n• Incorrect ID\n• Already anonymized",
        "no_active_reports": "📭 No active reports",
        "no_reports_collecting": "There are currently no reports collecting evidence.",
        "active_reports_title": "📋 Active reports",
        "active_reports_description": "**{count}** reports currently collecting evidence:",
        "reports_list_field": "🕐 Reports list",
        "expires_in_hours": "• `{report_id}` - Expires in {hours:.1f}h",
        "usage_field": "💡 Usage",
        "usage_description": "Use `/anonymiser report_id:<ID>` to anonymize a specific report",
        
        # Categories command
        "categories_title": "📂 Agis Report Categories",
        "categories_description": "Here are the available categories for your reports:",
        "use_category": "Use: `{category}`",
        "advice_field": "💡 Advice",
        "advice_description": "Copy-paste the desired category in the 'Report Category' field when using `/agis`",
        "footer_protection": "Protection • Vigilance • Community",
        
        # Validate command
        "report_validation_title": "✅ Report validation",
        "can_use_validation": "You can use this command to validate a report.",
        "access_denied": "❌ Access denied",
        "need_validator_role": "You must have the '{role}' role to use this command.",
        
        # Check command
        "need_admin_validator": "You must be an administrator or have the '{role}' role to use this command.",
        "service_unavailable": "⚠️ Service unavailable",
        "centralized_check_disabled": "Centralized checking is not enabled.",
        "flagged_user_detected": "🚨 Flagged user detected",
        "user_flagged_centralized": "User {user} is flagged in the centralized database",
        "user_field": "👤 User",
        "flag_level_field": "🔴 Flag level",
        "category_field_check": "📂 Category",
        "reason_field_check": "⚠️ Reason",
        "flagged_by_field": "🏠 Flagged by",
        "unknown_server": "Unknown server",
        "validations_field": "📊 Validations",
        "servers_count": "{count} server(s)",
        "flagged_date_field": "📅 Flagged on",
        "footer_manual_check": "Manual check • Aegis centralized database",
        
        # Messages for non-flagged user
        "user_verified": "✅ User verified",
        "user_not_flagged": "User {user} is not flagged in the centralized database",
        "status_field": "✅ Status",
        "no_flag_found": "No flag found",
        "verification_field": "🔍 Verification",
        "centralized_db_consulted": "Centralized database consulted",
        
        # Messages test_commands.py
        "bug_detected_log": "🐛 BUG DETECTED - Test: {test_name} | Error: {error} | Context: {context}",
        "traceback_log": "🐛 TRACEBACK: {traceback}",
        "no_bugs_detected_summary": "✅ No bugs found during tests!",
        "bugs_detected_summary": "🐛 **{count} bug(s) detected:**\n\n",
        "bug_entry_name": "**{i}.** `{test_name}`\n",
        "bug_entry_error": "   • Error: `{error_type}: {error_message}`\n",
        "bug_entry_context": "   • Context: {context}\n",
        "bug_entry_timestamp": "   • Timestamp: {timestamp}\n\n",
        "test_normal": "Normal test",
        "normal_user": "Normal user",
        "test_script": "Script test",
        "test_sql": "SQL test",
        "test_length": "Length test",
        "test_special_chars": "Special characters test",
        "special_chars_content": "Test with emojis 🚨🔞",
        "test_valid_sanitized": "✅ {name}: Valid={is_valid}, Sanitized length={length}",
        "test_error": "❌ {name}: ERROR - {error}",
        "attempt_allowed": "✅ Attempt {attempt}: Allowed",
        "rate_limit_premature": "❌ Attempt {attempt}: Premature rate limit",
        "attempt_blocked": "✅ Attempt {attempt}: Correctly blocked",
        "should_be_blocked": "❌ Attempt {attempt}: Should be blocked",
        "general_error": "❌ General error: {error}",
        "supabase_disabled_warning": "⚠️ Supabase disabled in configuration",
        "supabase_connection_ok": "✅ Supabase connection: OK",
        "supabase_connection_fail": "❌ Supabase connection: FAILED",
        "supabase_error": "❌ Supabase error: {error}",
        "guilds_configured": "✅ Configured guilds: {count}",
        "guild_config_ok": "✅ Guild {guild_id}: Configuration OK",
        "guild_config_empty": "❌ Guild {guild_id}: Empty configuration",
        "guild_config_error": "❌ Guild {guild_id}: Error - {error}",
        "guild_config_general_error": "❌ General guild config error: {error}",
        "test_mode_only": "❌ This command is only available in test mode.\nTo enable it, set the environment variable `AEGIS_TEST_MODE=true`",
        "diagnostic_rapid_title": "🔧 Rapid Diagnostic - Aegis System",
        "diagnostic_results": "Basic test results",
        "security_validator_field": "🔒 Security validator",
        "rate_limiter_field": "⏰ Rate limiter",
        "supabase_field": "🗄️ Supabase",
        "general_status_field": "📋 General status",
        "system_operational": "✅ System operational",
        "checks_needed": "⚠️ Checks needed",
        "diagnostic_footer": "Rapid diagnostic completed • Simplified version",
        "diagnostic_error": "❌ Diagnostic error: {error}",
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