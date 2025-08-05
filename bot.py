import discord 
from discord import app_commands
import dotenv 
import os
from datetime import datetime, timedelta
import asyncio

# Charger les variables d'environnement AVANT d'importer config
dotenv.load_dotenv()

from config import BOT_CONFIG, REPORT_CATEGORIES, ERROR_MESSAGES, validate_config
from utils import (
    SecurityValidator, RateLimiter, ReportTracker, AuditLogger,
    create_secure_embed, format_report_id, logger
)
from commands import show_stats, export_reports, purge_forum_reports
from supabase_client import supabase_client
from setup_views import SetupMainView
from guild_config import guild_config
from debug_tools import debug_system, test_supabase_manual, setup_debug_logging
from test_commands import register_test_commands
# Anciens décorateurs supprimés - interaction directe maintenant

# Activer le debug avancé
setup_debug_logging()

# Validation de la configuration au démarrage
if not validate_config():
    print("[ERREUR] Erreur de configuration. Arrêt du bot.")
    exit(1)

TOKEN = os.getenv("DISCORD_TOKEN")

# Paramètres du bot 
intents = discord.Intents.default()
intents.message_content = True  # Nécessaire pour lire le contenu des DM
intents.guilds = True
intents.members = True  # Nécessaire pour détecter les nouveaux membres
intents.dm_messages = True  # Nécessaire pour écouter les DM
client = discord.Client(intents=intents)

# Instances des systèmes de sécurité
rate_limiter = RateLimiter()
report_tracker = ReportTracker()
security_validator = SecurityValidator()
audit_logger = AuditLogger()

# Système de mapping temporaire utilisateur -> thread (conforme RGPD)
# Stockage temporaire en mémoire, sans persistance
class EvidenceCollector:
    def __init__(self):
        self.user_thread_mapping = {}  # user_id -> (thread_id, report_id, expiry_timestamp)
        self.cleanup_interval = 3600  # Nettoyage automatique toutes les heures
        self.evidence_timeout = 24 * 3600  # 24h pour envoyer des preuves
    
    def register_user_thread(self, user_id: int, thread_id: int, report_id: str):
        """Enregistre temporairement la liaison utilisateur/thread"""
        expiry = datetime.now().timestamp() + self.evidence_timeout
        self.user_thread_mapping[user_id] = (thread_id, report_id, expiry)
        logger.info(f"Evidence collector: Registered user {user_id} for thread {thread_id}")
    
    def get_user_thread(self, user_id: int):
        """Récupère les informations du thread pour un utilisateur"""
        if user_id in self.user_thread_mapping:
            thread_id, report_id, expiry = self.user_thread_mapping[user_id]
            if datetime.now().timestamp() < expiry:
                return thread_id, report_id
            else:
                # Expiry automatique
                del self.user_thread_mapping[user_id]
                logger.info(f"Evidence collector: Expired mapping for user {user_id}")
        return None, None
    
    def remove_user_mapping(self, user_id: int):
        """Supprime manuellement une liaison utilisateur/thread"""
        if user_id in self.user_thread_mapping:
            del self.user_thread_mapping[user_id]
            logger.info(f"Evidence collector: Removed mapping for user {user_id}")
    
    def cleanup_expired(self):
        """Nettoie les mappings expirés (appelé périodiquement)"""
        current_time = datetime.now().timestamp()
        expired_users = [
            user_id for user_id, (_, _, expiry) in self.user_thread_mapping.items() 
            if current_time >= expiry
        ]
        for user_id in expired_users:
            del self.user_thread_mapping[user_id]
        if expired_users:
            logger.info(f"Evidence collector: Cleaned up {len(expired_users)} expired mappings")

evidence_collector = EvidenceCollector()

# View pour sélectionner la catégorie avant le modal
class CategorySelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.selected_category = None

    @discord.ui.select(
        placeholder="Sélectionnez une catégorie de signalement...",
        options=[
            discord.SelectOption(label="🚨 Harcèlement", value="harassment", description="Comportement de harcèlement"),
            discord.SelectOption(label="🔞 Contenu inapproprié", value="inappropriate_content", description="Contenu NSFW ou inapproprié"),
            discord.SelectOption(label="👁️ Comportement suspect", value="suspicious_behavior", description="Activité suspecte"),
            discord.SelectOption(label="🛡️ Sécurité des mineurs", value="child_safety", description="Risques pour les mineurs"),
            discord.SelectOption(label="📢 Spam", value="spam", description="Messages répétitifs ou indésirables"),
            discord.SelectOption(label="💰 Arnaque", value="scam", description="Tentative d'escroquerie"),
            discord.SelectOption(label="⚔️ Menaces", value="threats", description="Menaces ou violence"),
            discord.SelectOption(label="❓ Autre", value="other", description="Autre type de problème")
        ]
    )
    async def category_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.selected_category = select.values[0]
        # Passer à la sélection de preuve
        embed = create_secure_embed(
            "🛡️ Signalement Agis - Étape 2", 
            f"**Catégorie sélectionnée :** {REPORT_CATEGORIES[self.selected_category]}\n\nVotre rapport repose-t-il sur une preuve ?",
            discord.Color.blue()
        )
        view = ProofSelectView(self.selected_category)
        await interaction.response.edit_message(embed=embed, view=view)

# View pour sélectionner si on a des preuves
class ProofSelectView(discord.ui.View):
    def __init__(self, category: str):
        super().__init__(timeout=300)
        self.selected_category = category
        self.has_proof = None

    @discord.ui.select(
        placeholder="Votre rapport repose-t-il sur une preuve ?",
        options=[
            discord.SelectOption(label="✅ Oui", value="oui", description="J'ai des preuves (captures, liens, etc.)"),
            discord.SelectOption(label="❌ Non", value="non", description="Pas de preuve directe disponible")
        ]
    )
    async def proof_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.has_proof = select.values[0]
        # Ouvrir le modal avec toutes les données
        modal = AgisReportModal(self.selected_category, self.has_proof)
        await interaction.response.send_modal(modal)

# Modal pour la commande /agis
class AgisReportModal(discord.ui.Modal, title="Signalement Agis - Rapport anonyme"):
    def __init__(self, category: str = None, has_proof: str = None):
        super().__init__()
        self.selected_category = category
        self.has_proof = has_proof
    # Nom d'utilisateur à signaler
    target_username = discord.ui.TextInput(
        label="Nom d'utilisateur à signaler",
        placeholder="@utilisateur, pseudo, ou ID Discord (ex: 123456789012345678)...",
        required=True,
        max_length=BOT_CONFIG["MAX_USERNAME_LENGTH"]
    )
    
    
    # Motif du signalement
    report_reason = discord.ui.TextInput(
        label="Motif du signalement",
        placeholder="Explication factuelle du comportement ou contenu concerné...",
        required=True,
        style=discord.TextStyle.paragraph,
        max_length=BOT_CONFIG["MAX_REPORT_LENGTH"]
    )
    
    # Liens et éléments complémentaires (combinés)
    additional_evidence = discord.ui.TextInput(
        label="Liens et preuves (optionnel)",
        placeholder="Liens de messages, screenshots, logs, autres preuves...",
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=BOT_CONFIG["MAX_EVIDENCE_LENGTH"]
    )
    
    
    async def on_submit(self, interaction: discord.Interaction):
        # Différer immédiatement pour éviter l'expiration
        await interaction.response.defer(ephemeral=True)
        
        # Vérification du rate limiting
        if rate_limiter.is_rate_limited(
            interaction.user.id, 
            BOT_CONFIG["MAX_REPORTS_PER_USER_PER_HOUR"]
        ):
            await interaction.followup.send(
                ERROR_MESSAGES["rate_limited"],
                ephemeral=True
            )
            audit_logger.log_security_event(
                "RATE_LIMITED", 
                f"User {interaction.user.id} hit rate limit",
                interaction.user.id
            )
            return
        
        # Validation des entrées
        target_username = security_validator.sanitize_input(
            self.target_username.value, BOT_CONFIG["MAX_USERNAME_LENGTH"]
        )
        report_reason = security_validator.sanitize_input(
            self.report_reason.value, BOT_CONFIG["MAX_REPORT_LENGTH"]
        )
        
        if not security_validator.validate_username(target_username):
            await interaction.followup.send(
                ERROR_MESSAGES["invalid_input"] + " Nom d'utilisateur invalide.",
                ephemeral=True
            )
            return
        
        # Vérification des doublons
        if report_tracker.is_duplicate_report(
            interaction.user.id, target_username, report_reason
        ):
            await interaction.followup.send(
                "⚠️ Signalement similaire déjà soumis récemment.",
                ephemeral=True
            )
            return
        
        # Générer un ID unique pour le signalement
        report_id = format_report_id(interaction.guild.id, datetime.now())
        
        # Créer un embed sécurisé
        embed = create_secure_embed(
            "🛡️ Nouveau signalement Agis",
            "Un nouveau signalement anonyme a été reçu",
            discord.Color.orange()
        )
        
        embed.add_field(name="🆔 ID Signalement", value=f"`{report_id}`", inline=False)
        embed.add_field(name="👤 Utilisateur signalé", value=target_username, inline=False)
        # Utiliser la catégorie sélectionnée
        category_display = REPORT_CATEGORIES.get(self.selected_category, "❓ Autre") if self.selected_category else "❓ Autre"
        embed.add_field(name="📂 Catégorie", value=category_display, inline=False)
        embed.add_field(name="📝 Motif", value=report_reason, inline=False)
        
        if self.additional_evidence.value:
            evidence = security_validator.sanitize_input(
                self.additional_evidence.value, BOT_CONFIG["MAX_EVIDENCE_LENGTH"]
            )
            embed.add_field(name="🔗 Liens et preuves", value=evidence, inline=False)
        
        proof_display = "✅ Oui" if self.has_proof == "oui" else "❌ Non"
        embed.add_field(name="✅ Preuve disponible", value=proof_display, inline=True)
        embed.add_field(name="🕐 Date du signalement", value=datetime.now().strftime("%d/%m/%Y %H:%M"), inline=True)
        
        embed.set_footer(text="Signalement anonyme • En attente de validation")
        
        # Log du signalement
        audit_logger.log_report_submitted(
            interaction.user.id, target_username, interaction.guild.id
        )
        
        # Trouver le forum d'alertes
        alerts_forum = discord.utils.get(interaction.guild.channels, name=BOT_CONFIG["ALERTS_CHANNEL_NAME"])
        
        if alerts_forum and isinstance(alerts_forum, discord.ForumChannel):
            # Créer un post dans le forum avec le nouveau format
            # Format: 🕵️ Signalement #[ID] - [Catégorie]
            category_for_title = REPORT_CATEGORIES.get(self.selected_category, "❓ Autre") if self.selected_category else "❓ Autre"
            post_title = f"🕵️ Signalement #{report_id} - {category_for_title}"
            
            # Créer le post dans le forum avec l'embed directement
            thread_with_message = await alerts_forum.create_thread(
                name=post_title,
                embed=embed,  # Utiliser l'embed directement
                auto_archive_duration=BOT_CONFIG["AUTO_ARCHIVE_DURATION"],
                reason=f"Nouveau signalement Agis - {report_id}"
            )
            
            # Récupérer le thread réel depuis ThreadWithMessage
            thread = thread_with_message.thread
            
            # Ajouter les boutons de validation avec les données du signalement
            view = ValidationView(
                report_id, 
                interaction.guild.id,
                target_username,
                category_display,
                report_reason,
                interaction.guild.name
            )
            await thread.send("**Validation du signalement :**", view=view)
            
            # Enregistrer la liaison utilisateur/thread pour la collecte de preuves
            evidence_collector.register_user_thread(
                interaction.user.id, 
                thread.id,  # ID du thread créé (maintenant c'est le bon objet thread)
                report_id
            )
            
            # Envoyer un DM à l'utilisateur pour la collecte de preuves
            try:
                dm_embed = create_secure_embed(
                    "📨 Signalement Agis - Preuves supplémentaires",
                    f"Votre signalement **{report_id}** a été soumis avec succès.",
                    discord.Color.blue()
                )
                dm_embed.add_field(
                    name="💡 Vous pouvez maintenant envoyer des preuves",
                    value="Répondez à ce message privé avec :\n"
                          "• Captures d'écran\n"
                          "• Messages copiés\n"
                          "• Liens vers des preuves\n"
                          "• Tout autre élément pertinent\n\n"
                          "⏰ **Vous avez 24h** pour envoyer vos preuves.\n"
                          "🔒 **Votre anonymat** est préservé - les preuves seront transférées sans révéler votre identité.",
                    inline=False
                )
                dm_embed.add_field(
                    name="🚫 Pour arrêter",
                    value="Envoyez simplement le mot `STOP` pour ne plus recevoir de demandes de preuves.",
                    inline=False
                )
                dm_embed.set_footer(text=f"ID: {report_id} • Expire dans 24h")
                
                await interaction.user.send(embed=dm_embed)
                
                await interaction.followup.send(
                    "✅ Votre signalement anonyme a été envoyé avec succès !\n"
                    "📨 Un message privé vous a été envoyé pour collecter d'éventuelles preuves supplémentaires.",
                    ephemeral=True
                )
                
            except discord.Forbidden:
                # L'utilisateur n'accepte pas les DM
                await interaction.followup.send(
                    "✅ Votre signalement anonyme a été envoyé avec succès !\n"
                    "⚠️ Impossible d'envoyer un DM - vérifiez vos paramètres de confidentialité si vous souhaitez envoyer des preuves supplémentaires.",
                    ephemeral=True
                )
        else:
            audit_logger.log_error(
                "FORUM_NOT_FOUND", 
                f"Forum {BOT_CONFIG['ALERTS_CHANNEL_NAME']} non trouvé",
                interaction.user.id
            )
            
            # Message d'erreur plus détaillé avec instructions
            error_embed = create_secure_embed(
                "❌ Configuration manquante",
                "Le bot Agis n'est pas encore configuré sur ce serveur.",
                discord.Color.red()
            )
            error_embed.add_field(
                name="🔧 Solution",
                value=f"Un administrateur doit exécuter `/setup` pour créer :\n"
                      f"• Le forum `#{BOT_CONFIG['ALERTS_CHANNEL_NAME']}`\n"
                      f"• Le rôle `@{BOT_CONFIG['VALIDATOR_ROLE_NAME']}`",
                inline=False
            )
            error_embed.add_field(
                name="👑 Administrateurs",
                value="Utilisez `/setup` pour configurer le bot automatiquement.",
                inline=False
            )
            error_embed.set_footer(text="Votre signalement n'a pas pu être traité")
            
            await interaction.followup.send(embed=error_embed, ephemeral=True)

# Vue pour les boutons de validation
class ValidationView(discord.ui.View):
    def __init__(self, report_id: str, guild_id: int, target_username: str = None, 
                 category: str = None, reason: str = None, guild_name: str = None):
        super().__init__(timeout=BOT_CONFIG["VALIDATION_TIMEOUT_HOURS"] * 3600)  # timeout en secondes
        self.validators = set()
        self.rejectors = set()
        self.report_id = report_id
        self.guild_id = guild_id
        self.is_finalized = False
        # Données pour la centralisation
        self.target_username = target_username
        self.category = category
        self.reason = reason
        self.guild_name = guild_name
    
    @discord.ui.button(label="✅ Valider", style=discord.ButtonStyle.green, custom_id="validate_report")
    async def validate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.InteractionResponded:
            # L'interaction a déjà été répondue
            pass
        except Exception:
            # Interaction expirée, ne rien faire
            return
            
        if self.is_finalized:
            await interaction.followup.send(
                "ℹ️ Ce signalement a déjà été finalisé.", ephemeral=True
            )
            return
            
        # Vérifier si l'utilisateur a le rôle Validateur
        validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
        
        if validator_role and validator_role in interaction.user.roles:
            # Empêcher la double validation par le même utilisateur
            if interaction.user.id in self.validators:
                await interaction.followup.send(
                    "⚠️ Vous avez déjà validé ce signalement.", ephemeral=True
                )
                return
                
            # Retirer de rejectors si l'utilisateur change d'avis
            self.rejectors.discard(interaction.user.id)
            self.validators.add(interaction.user.id)
            
            # Log de l'action
            audit_logger.log_validation_action(
                interaction.user.id, "VALIDATE", self.report_id, self.guild_id
            )
            
            # Calculer le pourcentage de validation
            total_validators = len([member for member in interaction.guild.members if validator_role in member.roles])
            validation_percentage = (len(self.validators) / total_validators) * 100 if total_validators > 0 else 0
            
            embed = create_secure_embed(
                "✅ Signalement validé",
                f"Validé par {interaction.user.display_name}",
                discord.Color.green()
            )
            embed.add_field(
                name="Progression", 
                value=f"{validation_percentage:.1f}% ({len(self.validators)}/{total_validators})", 
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Si le quorum est atteint
            if validation_percentage >= BOT_CONFIG["QUORUM_PERCENTAGE"]:
                await self.finalize_validation(interaction)
        else:
            await interaction.followup.send(
                f"❌ Vous devez avoir le rôle '{BOT_CONFIG['VALIDATOR_ROLE_NAME']}' pour valider ce signalement.",
                ephemeral=True
            )
    
    @discord.ui.button(label="❌ Rejeter", style=discord.ButtonStyle.red, custom_id="reject_report")
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.InteractionResponded:
            pass
        except Exception:
            return
            
        if self.is_finalized:
            await interaction.followup.send(
                "ℹ️ Ce signalement a déjà été finalisé.", ephemeral=True
            )
            return
            
        validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
        
        if validator_role and validator_role in interaction.user.roles:
            # Empêcher le double rejet par le même utilisateur
            if interaction.user.id in self.rejectors:
                await interaction.followup.send(
                    "⚠️ Vous avez déjà rejeté ce signalement.", ephemeral=True
                )
                return
                
            # Retirer de validators si l'utilisateur change d'avis
            self.validators.discard(interaction.user.id)
            self.rejectors.add(interaction.user.id)
            
            # Log de l'action
            audit_logger.log_validation_action(
                interaction.user.id, "REJECT", self.report_id, self.guild_id
            )
            
            # Calculer le pourcentage de rejet
            total_validators = len([member for member in interaction.guild.members if validator_role in member.roles])
            rejection_percentage = (len(self.rejectors) / total_validators) * 100 if total_validators > 0 else 0
            
            embed = create_secure_embed(
                "❌ Signalement rejeté",
                f"Rejeté par {interaction.user.display_name}",
                discord.Color.red()
            )
            embed.add_field(
                name="Progression rejet", 
                value=f"{rejection_percentage:.1f}% ({len(self.rejectors)}/{total_validators})", 
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Si le quorum de rejet est atteint (même seuil que validation)
            if rejection_percentage >= BOT_CONFIG["QUORUM_PERCENTAGE"]:
                await self.finalize_rejection(interaction)
        else:
            await interaction.followup.send(
                f"❌ Vous devez avoir le rôle '{BOT_CONFIG['VALIDATOR_ROLE_NAME']}' pour rejeter ce signalement.",
                ephemeral=True
            )
    
    @discord.ui.button(label="📩 Demander détails", style=discord.ButtonStyle.gray, custom_id="request_details")
    async def request_details_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Permet aux modérateurs de demander plus de détails au rapporteur"""
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.InteractionResponded:
            pass
        except Exception:
            return
            
        # Vérifier si l'utilisateur a le rôle Validateur ou est admin
        validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
        if not (interaction.user.guild_permissions.administrator or 
                (validator_role and validator_role in interaction.user.roles)):
            await interaction.followup.send(
                f"❌ Vous devez avoir le rôle '{BOT_CONFIG['VALIDATOR_ROLE_NAME']}' ou être administrateur.",
                ephemeral=True
            )
            return
        
        # Vérifier si le signalement est encore dans la fenêtre de collecte
        user_id = None
        for uid, (thread_id, stored_report_id, expiry) in evidence_collector.user_thread_mapping.items():
            if stored_report_id == self.report_id:
                user_id = uid
                break
        
        if not user_id:
            await interaction.followup.send(
                "⚠️ Ce signalement n'est plus dans la fenêtre de collecte de preuves (>24h ou déjà anonymisé).",
                ephemeral=True
            )
            return
        
        # Demander des détails via message direct au rapporteur
        try:
            user = interaction.client.get_user(user_id)
            if user:
                embed = create_secure_embed(
                    "📩 Demande de détails supplémentaires",
                    f"Un modérateur souhaite obtenir plus d'informations sur votre signalement **{self.report_id}**.",
                    discord.Color.blue()
                )
                embed.add_field(
                    name="👤 Demandé par",
                    value=f"Modérateur du serveur {interaction.guild.name}",
                    inline=False
                )
                embed.add_field(
                    name="💬 Question",
                    value="Pouvez-vous fournir plus de détails ou de preuves concernant ce signalement ?",
                    inline=False
                )
                embed.add_field(
                    name="📝 Comment répondre",
                    value="Répondez à ce message privé avec les informations supplémentaires. Vos preuves seront transférées anonymement.",
                    inline=False
                )
                embed.set_footer(text=f"Signalement: {self.report_id} • Demande de détails")
                
                await user.send(embed=embed)
                
                # Confirmer au modérateur
                await interaction.followup.send(
                    f"✅ Demande de détails envoyée au rapporteur pour le signalement `{self.report_id}`.",
                    ephemeral=True
                )
                
                # Log de l'action
                audit_logger.log_security_event(
                    "DETAILS_REQUESTED",
                    f"Details requested for report {self.report_id} by moderator {interaction.user.id}",
                    interaction.user.id
                )
                
            else:
                await interaction.followup.send(
                    "❌ Impossible de contacter le rapporteur (utilisateur introuvable).",
                    ephemeral=True
                )
                
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ Impossible d'envoyer un DM au rapporteur (paramètres de confidentialité).",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi demande détails: {e}")
            await interaction.followup.send(
                "❌ Erreur lors de l'envoi de la demande de détails.",
                ephemeral=True
            )
    
    async def finalize_validation(self, interaction: discord.Interaction):
        self.is_finalized = True
        
        # Désactiver les boutons
        for item in self.children:
            item.disabled = True
        
        # Centraliser le signalement validé vers Supabase
        centralization_success = False
        centralization_attempted = False
        user_id_found = False
        
        if BOT_CONFIG["SUPABASE_ENABLED"] and self.target_username:
            try:
                # Déterminer le niveau de flag basé sur la catégorie
                flag_level = self.determine_flag_level(self.category)
                
                # Extraire l'ID utilisateur du target_username s'il contient un ID
                target_user_id = self.extract_user_id(self.target_username)
                
                if target_user_id:
                    user_id_found = True
                    centralization_attempted = True
                    centralization_success = await supabase_client.add_validated_report(
                        user_id=target_user_id,
                        username=self.target_username,
                        flag_level=flag_level,
                        reason=self.reason,
                        category=self.category,
                        guild_id=self.guild_id,
                        guild_name=self.guild_name
                    )
                    
                    if centralization_success:
                        logger.info(f"✅ Signalement {self.report_id} centralisé avec succès")
                    else:
                        logger.warning(f"⚠️ Échec de centralisation pour {self.report_id}")
                        
            except Exception as e:
                logger.error(f"Erreur lors de la centralisation: {e}")
        
        # Message différent selon si l'utilisateur a été trouvé ou pas
        if user_id_found:
            embed = create_secure_embed(
                "🎉 Signalement validé et centralisé !",
                f"Le quorum de validation a été atteint pour le signalement `{self.report_id}`.\nL'utilisateur signalé a été ajouté à la base de données centralisée.",
                discord.Color.green()
            )
        else:
            embed = create_secure_embed(
                "⚠️ Signalement validé mais non centralisé",
                f"Le quorum de validation a été atteint pour le signalement `{self.report_id}`.\n⚠️ **L'utilisateur n'a pas pu être identifié** (utilisez @mention ou ID Discord pour la centralisation).",
                discord.Color.orange()
            )
        
        embed.add_field(
            name="📈 Statistiques",
            value=f"Validateurs: {len(self.validators)}\nRejeteurs: {len(self.rejectors)}",
            inline=True
        )
        
        # Ajouter info de centralisation
        if BOT_CONFIG["SUPABASE_ENABLED"]:
            centralization_status = "✅ Centralisé" if centralization_success else "⚠️ Échec centralisation"
            embed.add_field(
                name="🌐 Base centralisée",
                value=centralization_status,
                inline=True
            )
        
        # Log de la finalisation
        audit_logger.log_validation_action(
            interaction.user.id, "FINALIZED", self.report_id, self.guild_id
        )
        
        await interaction.channel.send(embed=embed)
        
        # Mettre à jour le message avec les boutons désactivés
        try:
            # Trouver le message avec les boutons de validation
            async for message in interaction.channel.history(limit=10):
                if message.author == interaction.client.user and message.components:
                    await message.edit(view=self)
                    break
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des boutons: {e}")
    
    async def finalize_rejection(self, interaction: discord.Interaction):
        """Finaliser le rejet du signalement"""
        self.is_finalized = True
        
        # Désactiver les boutons
        for item in self.children:
            item.disabled = True
        
        embed = create_secure_embed(
            "❌ Signalement rejeté par la communauté",
            f"Le quorum de rejet a été atteint pour le signalement `{self.report_id}`.\nCe signalement a été rejeté par la communauté.",
            discord.Color.red()
        )
        
        # Log de finalisation
        audit_logger.log_validation_action(
            interaction.user.id, "REJECTED_FINAL", self.report_id, self.guild_id
        )
        
        await interaction.channel.send(embed=embed)
        
        # Mettre à jour le message avec les boutons désactivés
        try:
            async for message in interaction.channel.history(limit=10):
                if message.author == interaction.client.user and message.components:
                    await message.edit(view=self)
                    break
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des boutons: {e}")
    
    def determine_flag_level(self, category: str) -> str:
        """Déterminer le niveau de flag basé sur la catégorie"""
        critical_categories = ["🛡️ Sécurité des mineurs", "⚔️ Menaces"]
        high_categories = ["🚨 Harcèlement", "🔞 Contenu inapproprié", "💰 Arnaque"]
        
        if any(cat in category for cat in critical_categories):
            return "critical"
        elif any(cat in category for cat in high_categories):
            return "high"
        else:
            return "medium"
    
    def extract_user_id(self, username_input: str) -> int:
        """Extraire l'ID utilisateur du input (mention @, pseudo ou ID)"""
        import re
        
        # 1. Chercher une mention Discord <@123456789> ou <@!123456789>
        mention_match = re.search(r'<@!?(\d{15,20})>', username_input)
        if mention_match:
            return int(mention_match.group(1))
        
        # 2. Chercher un ID Discord brut (série de chiffres 15-20 chiffres)
        id_match = re.search(r'\b(\d{15,20})\b', username_input)
        if id_match:
            return int(id_match.group(1))
        
        # Si pas d'ID trouvé, retourner None (on ne peut pas centraliser sans ID)
        logger.warning(f"Impossible d'extraire l'ID utilisateur de: {username_input}")
        return None
    
    async def on_timeout(self):
        """Gère l'expiration du délai de validation"""
        if not self.is_finalized:
            logger.info(f"Timeout de validation pour le signalement {self.report_id}")
            # En production, vous pourriez vouloir notifier les administrateurs

# Commande slash /agis
@app_commands.command(name="agis", description="Signaler anonymement un comportement à risque")
async def agis_report(interaction: discord.Interaction):
    """Affiche un sélecteur de catégorie puis un modal pour signaler"""
    # Vérifier si le bot est configuré
    alerts_forum = discord.utils.get(interaction.guild.channels, name=BOT_CONFIG["ALERTS_CHANNEL_NAME"])
    validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
    
    if not alerts_forum or not validator_role:
        # Message d'erreur détaillé avec instructions claires
        error_embed = create_secure_embed(
            "❌ Configuration manquante",
            "Le bot Agis n'est pas encore configuré sur ce serveur.",
            discord.Color.red()
        )
        
        missing_items = []
        if not alerts_forum:
            missing_items.append(f"• Forum `#{BOT_CONFIG['ALERTS_CHANNEL_NAME']}`")
        if not validator_role:
            missing_items.append(f"• Rôle `@{BOT_CONFIG['VALIDATOR_ROLE_NAME']}`")
        
        error_embed.add_field(
            name="🔧 Éléments manquants",
            value="\n".join(missing_items),
            inline=False
        )
        error_embed.add_field(
            name="👑 Pour les administrateurs",
            value="Utilisez `/setup` pour configurer automatiquement le bot.",
            inline=False
        )
        error_embed.add_field(
            name="💡 Que fait /setup ?",
            value="• Crée le forum pour les signalements\n• Crée le rôle pour les validateurs\n• Configure les permissions",
            inline=False
        )
        error_embed.set_footer(text="Configuration requise avant utilisation")
        
        await interaction.response.send_message(embed=error_embed, ephemeral=True)
        return
    
    # Envoyer le sélecteur de catégorie
    embed = create_secure_embed(
        "🛡️ Signalement Agis", 
        "Sélectionnez la catégorie de votre signalement :",
        discord.Color.blue()
    )
    view = CategorySelectView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# Commande slash /categories (pour voir les catégories disponibles)
@app_commands.command(name="anonymiser", description="Supprimer manuellement le lien d'anonymat d'un signalement")
@app_commands.describe(report_id="ID du signalement à anonymiser")
async def anonymise_report(interaction: discord.Interaction, report_id: str = None):
    """Permet de supprimer manuellement le mapping utilisateur/thread avant 24h"""
    
    # Vérifier les permissions (admin ou validateur)
    validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
    if not (interaction.user.guild_permissions.administrator or 
            (validator_role and validator_role in interaction.user.roles)):
        await interaction.response.send_message(
            "❌ Cette commande est réservée aux administrateurs et validateurs.",
            ephemeral=True
        )
        return
    
    await interaction.response.defer(ephemeral=True)
    
    if report_id:
        # Anonymiser un signalement spécifique
        removed = False
        for user_id, (thread_id, stored_report_id, expiry) in list(evidence_collector.user_thread_mapping.items()):
            if stored_report_id == report_id:
                evidence_collector.remove_user_mapping(user_id)
                removed = True
                break
        
        if removed:
            embed = create_secure_embed(
                "✅ Signalement anonymisé",
                f"Le lien d'anonymat pour le signalement `{report_id}` a été supprimé.",
                discord.Color.green()
            )
            embed.add_field(
                name="🔒 Conséquences",
                value="• L'utilisateur ne peut plus envoyer de preuves\n• Le lien temporaire a été détruit\n• L'anonymat est maintenant permanent",
                inline=False
            )
        else:
            embed = create_secure_embed(
                "⚠️ Signalement non trouvé",
                f"Aucun signalement actif trouvé avec l'ID `{report_id}`.",
                discord.Color.orange()
            )
            embed.add_field(
                name="💡 Possible causes",
                value="• Signalement déjà expiré (>24h)\n• ID incorrect\n• Déjà anonymisé",
                inline=False
            )
    else:
        # Afficher les signalements actifs
        if not evidence_collector.user_thread_mapping:
            embed = create_secure_embed(
                "📭 Aucun signalement actif",
                "Il n'y a actuellement aucun signalement en cours de collecte de preuves.",
                discord.Color.blue()
            )
        else:
            embed = create_secure_embed(
                "📋 Signalements actifs",
                f"**{len(evidence_collector.user_thread_mapping)}** signalements en cours de collecte de preuves :",
                discord.Color.blue()
            )
            
            active_reports = []
            for user_id, (thread_id, stored_report_id, expiry) in evidence_collector.user_thread_mapping.items():
                # Calculer temps restant
                remaining_hours = max(0, (expiry - datetime.now().timestamp()) / 3600)
                active_reports.append(f"• `{stored_report_id}` - Expire dans {remaining_hours:.1f}h")
            
            embed.add_field(
                name="🕐 Liste des signalements",
                value="\n".join(active_reports[:10]),  # Limiter à 10 pour éviter embed trop long
                inline=False
            )
            embed.add_field(
                name="💡 Usage",
                value="Utilisez `/anonymiser report_id:<ID>` pour anonymiser un signalement spécifique",
                inline=False
            )
    
    # Log de l'action
    audit_logger.log_security_event(
        "MANUAL_ANONYMISATION",
        f"Manual anonymisation request for report {report_id or 'list'} by user {interaction.user.id}",
        interaction.user.id
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@app_commands.command(name="categories", description="Afficher les catégories de signalement disponibles")
async def show_categories(interaction: discord.Interaction):
    """Affiche les catégories de signalement disponibles"""
    embed = discord.Embed(
        title="📂 Catégories de signalement Agis",
        description="Voici les catégories disponibles pour vos signalements :",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    
    for key, value in REPORT_CATEGORIES.items():
        embed.add_field(name=value, value=f"Utilisez : `{value}`", inline=False)
    
    embed.add_field(
        name="💡 Conseil", 
        value="Copiez-collez la catégorie souhaitée dans le champ 'Catégorie du signalement' lors de l'utilisation de `/agis`",
        inline=False
    )
    
    embed.set_footer(text="Protection • Vigilance • Communauté")
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Commande slash /validate (pour les modérateurs)
@app_commands.command(name="validate", description="Valider un signalement (Modérateurs uniquement)")
async def validate_report(interaction: discord.Interaction):
    """Commande pour valider un signalement (réservée aux modérateurs)"""
    validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
    
    if validator_role and validator_role in interaction.user.roles:
        embed = create_secure_embed(
            "✅ Validation de signalement",
            "Vous pouvez utiliser cette commande pour valider un signalement.",
            discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = create_secure_embed(
            "❌ Accès refusé",
            f"Vous devez avoir le rôle '{BOT_CONFIG['VALIDATOR_ROLE_NAME']}' pour utiliser cette commande.",
            discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Commande slash /check (pour vérifier manuellement un utilisateur)
@app_commands.command(name="check", description="Vérifier si un utilisateur est flagué globalement")
@app_commands.describe(user="L'utilisateur à vérifier")
async def check_user(interaction: discord.Interaction, user: discord.Member):
    """Vérifier si un utilisateur est flagué dans la base centralisée"""
    
    # DEFER IMMÉDIATEMENT pour éviter le timeout
    await interaction.response.defer(ephemeral=True)
    
    # Vérifier les permissions (validateurs et administrateurs)
    validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
    
    if not (interaction.user.guild_permissions.administrator or 
            (validator_role and validator_role in interaction.user.roles)):
        embed = create_secure_embed(
            "❌ Accès refusé",
            f"Vous devez être administrateur ou avoir le rôle '{BOT_CONFIG['VALIDATOR_ROLE_NAME']}' pour utiliser cette commande.",
            discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    if not BOT_CONFIG["SUPABASE_ENABLED"]:
        embed = create_secure_embed(
            "⚠️ Service indisponible",
            "La vérification centralisée n'est pas activée.",
            discord.Color.orange()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    try:
        # Vérifier dans la base centralisée
        flag_data = await supabase_client.check_user_flag(
            user.id,
            interaction.guild.id,
            interaction.guild.name
        )
        
        if flag_data:
            # Utilisateur flagué trouvé
            embed = create_secure_embed(
                "🚨 Utilisateur flagué détecté",
                f"L'utilisateur {user.display_name} est flagué dans la base centralisée",
                discord.Color.red()
            )
            
            embed.add_field(name="👤 Utilisateur", value=f"{user.mention} ({user.display_name})", inline=False)
            embed.add_field(name="🔴 Niveau de flag", value=flag_data["flag_level"].upper(), inline=True)
            embed.add_field(name="📂 Catégorie", value=flag_data["flag_category"], inline=True)
            embed.add_field(name="⚠️ Raison", value=flag_data["flag_reason"], inline=False)
            embed.add_field(name="🏠 Flagué par", value=flag_data["flagged_by_guild_name"] or "Serveur inconnu", inline=True)
            embed.add_field(name="📊 Validations", value=f"{flag_data['validation_count']} serveur(s)", inline=True)
            embed.add_field(name="📅 Flagué le", value=flag_data["flagged_date"].strftime("%d/%m/%Y"), inline=True)
            
            embed.set_footer(text="Vérification manuelle • Base centralisée Aegis")
            
        else:
            # Utilisateur non flagué
            embed = create_secure_embed(
                "✅ Utilisateur vérifié",
                f"L'utilisateur {user.display_name} n'est pas flagué dans la base centralisée",
                discord.Color.green()
            )
            
            embed.add_field(name="👤 Utilisateur", value=f"{user.mention} ({user.display_name})", inline=False)
            embed.add_field(name="✅ Statut", value="Aucun flag trouvé", inline=True)
            embed.add_field(name="🔍 Vérification", value="Base centralisée consultée", inline=True)
            
            embed.set_footer(text="Vérification manuelle • Base centralisée Aegis")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Log de la vérification manuelle
        audit_logger.log_security_event(
            "MANUAL_CHECK",
            f"Vérification manuelle de {user.id} par {interaction.user.id}",
            interaction.user.id
        )
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de {user.display_name}: {e}")
        
        embed = create_secure_embed(
            "❌ Erreur de vérification",
            "Une erreur s'est produite lors de la vérification. Contactez un administrateur.",
            discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

# Commande slash /setup (pour les administrateurs)
@app_commands.command(name="setup", description="Configuration avancée du bot Agis")
@app_commands.describe(mode="Type de configuration à effectuer")
@app_commands.choices(mode=[
    app_commands.Choice(name="🔧 Configuration de base", value="basic"),
    app_commands.Choice(name="⚙️ Configuration avancée", value="advanced")
])
async def setup_agis(interaction: discord.Interaction, mode: str = "basic"):
    """Configuration du bot Agis - de base ou avancée"""
    
    try:
        # Vérifier si l'utilisateur est administrateur
        if not interaction.user.guild_permissions.administrator:
            embed = create_secure_embed(
                "❌ Accès refusé",
                "Vous devez être administrateur pour utiliser cette commande.",
                discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            audit_logger.log_security_event(
                "UNAUTHORIZED_SETUP", 
                f"User {interaction.user.id} attempted setup without admin",
                interaction.user.id
            )
            return
        
        # Vérifier si le forum existe déjà
        alerts_forum = discord.utils.get(interaction.guild.channels, name=BOT_CONFIG["ALERTS_CHANNEL_NAME"])
        validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
        
        if mode == "advanced":
            # Interface avancée avec boutons - PAS DE DEFER ICI
            from setup_views import SetupMainView
            
            view = SetupMainView(interaction.guild.id)
            embed = discord.Embed(
                title="⚙️ Configuration Avancée - Aegis",
                description="Choisissez les éléments à configurer :",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📢 Forum alertes", 
                value="✅ Configuré" if alerts_forum else "❌ Manquant", 
                inline=True
            )
            embed.add_field(
                name="👤 Rôle validateur", 
                value="✅ Configuré" if validator_role else "❌ Manquant", 
                inline=True
            )
            embed.add_field(
                name="🗄️ Supabase", 
                value="✅ Activé" if BOT_CONFIG["SUPABASE_ENABLED"] else "❌ Désactivé", 
                inline=True
            )
            
            embed.add_field(
                name="🎛️ Options disponibles",
                value="• **🔧 Configuration de base** - Forum et rôles\n"
                      "• **⚔️ Actions automatiques** - Ban/Kick selon niveau\n" 
                      "• **🔔 Notifications** - Mentions et alertes\n"
                      "• **📊 Seuils & Limites** - Rate limiting\n"
                      "• **🛡️ Quarantaine** - Isolation automatique",
                inline=False
            )
            
            embed.set_footer(text="Utilisez les boutons ci-dessous pour configurer • Expire dans 5 minutes")
            
            # Répondre directement sans defer
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            return  # Arrêter ici pour le mode avancé
            
        # Configuration de base - mode par défaut
        await interaction.response.defer(ephemeral=True)
        
        # Configuration de base - créer les éléments manquants
        # Créer le rôle Validateur s'il n'existe pas
        validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
        if not validator_role:
            validator_role = await interaction.guild.create_role(
                name=BOT_CONFIG["VALIDATOR_ROLE_NAME"],
                color=discord.Color.green(),
                reason="Configuration du bot Agis"
            )
            role_created = True
        else:
            role_created = False
        
        # Créer le forum d'alertes s'il n'existe pas
        alerts_forum = discord.utils.get(interaction.guild.channels, name=BOT_CONFIG["ALERTS_CHANNEL_NAME"])
        if not alerts_forum:
            # Permissions pour le forum d'alertes
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, create_public_threads=True),
                validator_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            
            # Ajouter les administrateurs
            for role in interaction.guild.roles:
                if role.permissions.administrator:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, create_public_threads=True)
            
            try:
                alerts_forum = await interaction.guild.create_forum(
                    name=BOT_CONFIG["ALERTS_CHANNEL_NAME"],
                    overwrites=overwrites,
                    reason="Configuration du bot Agis"
                )
                channel_created = True
            except discord.HTTPException as e:
                # Si c'est un canal qui existe déjà avec le même nom
                if "already exists" in str(e).lower() or e.code == 30013:
                    alerts_forum = discord.utils.get(interaction.guild.channels, name=BOT_CONFIG["ALERTS_CHANNEL_NAME"])
                    channel_created = False
                else:
                    raise e
        elif isinstance(alerts_forum, discord.ForumChannel):
            channel_created = False
        else:
            # Canal existant mais pas un forum, créer un nouveau forum avec un nom légèrement différent
            try:
                alerts_forum = await interaction.guild.create_forum(
                    name=f"{BOT_CONFIG['ALERTS_CHANNEL_NAME']}-forum",
                    overwrites=overwrites,
                    reason="Configuration du bot Agis - canal existant renommé"
                )
                channel_created = True
            except Exception as e:
                # Fallback: utiliser le canal existant même si ce n'est pas un forum
                channel_created = False
        
        # Créer un embed de confirmation
        embed = create_secure_embed(
            "✅ Configuration de base terminée",
            "Le bot Agis a été configuré avec succès !",
            discord.Color.green()
        )
        
        if role_created:
            embed.add_field(name="🆕 Rôle créé", value=f"@{BOT_CONFIG['VALIDATOR_ROLE_NAME']}", inline=True)
        else:
            embed.add_field(name="✅ Rôle existant", value=f"@{BOT_CONFIG['VALIDATOR_ROLE_NAME']}", inline=True)
        
        if channel_created:
            embed.add_field(name="🆕 Forum créé", value=f"#{BOT_CONFIG['ALERTS_CHANNEL_NAME']}", inline=True)
        else:
            embed.add_field(name="✅ Forum existant", value=f"#{BOT_CONFIG['ALERTS_CHANNEL_NAME']}", inline=True)
        
        embed.add_field(name="🔒 Visibilité", value="Seuls les administrateurs et validateurs peuvent voir ce forum", inline=False)
        embed.add_field(name="📋 Prochaines étapes", value=f"1. Attribuer le rôle @{BOT_CONFIG['VALIDATOR_ROLE_NAME']} aux modérateurs\n2. Utiliser /agis pour tester", inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
            
    except Exception as e:
        audit_logger = AuditLogger()
        audit_logger.log_error(
            "SETUP_ERROR", 
            f"Erreur lors de la configuration: {str(e)}",
            interaction.user.id
        )
        embed = create_secure_embed(
            "❌ Erreur de configuration",
            f"Une erreur s'est produite : {str(e)}",
            discord.Color.red()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)


@client.event
async def on_ready():
    print(f'{client.user} est connecté à Discord!')
    logger.info(f"Bot connecté en tant que {client.user} (ID: {client.user.id})")
    
    # Connexion à Supabase
    if BOT_CONFIG["SUPABASE_ENABLED"]:
        logger.info("Tentative de connexion à Supabase...")
        try:
            connection_result = await supabase_client.connect()
            logger.info(f"Résultat connexion Supabase: {connection_result}")
        except Exception as e:
            logger.error(f"Erreur connexion Supabase: {e}")
    else:
        logger.info("Supabase désactivé dans la configuration")
    
    # Synchroniser les commandes slash
    try:
        logger.info("Synchronisation des commandes slash...")
        synced = await tree.sync()
        print(f"Synchronisé {len(synced)} commande(s) slash")
        logger.info(f"Commandes synchronisées: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"Erreur lors de la synchronisation: {e}")
        logger.error(f"Erreur synchronisation: {e}")
    
    logger.info("=== BOT AGIS PRÊT ===")
    logger.info("Commandes disponibles:")
    logger.info("- /setup (configuration)")
    logger.info("- /agis (signalement anonyme)")
    logger.info("- /categories (voir les catégories)")
    logger.info("- /validate (validation modérateurs)")
    logger.info("- /check (vérification utilisateur)")
    logger.info("- /debug (diagnostics système)")
    logger.info("- /test-supabase (test de Supabase)")
    logger.info("- !agis (commande de test)")
    logger.info(f"Configuration: Forum=#{BOT_CONFIG['ALERTS_CHANNEL_NAME']}, Rôle=@{BOT_CONFIG['VALIDATOR_ROLE_NAME']}")
    logger.info("=== DÉMARRAGE TERMINÉ ===")
    print("[DEBUG] ✅ Bot prêt ! Utilisez /debug pour diagnostiquer les problèmes")

@client.event
async def on_member_join(member):
    """Vérifier automatiquement les nouveaux membres contre la base centralisée"""
    if not BOT_CONFIG["AUTO_CHECK_NEW_MEMBERS"] or not BOT_CONFIG["SUPABASE_ENABLED"]:
        return
    
    try:
        # Vérifier si l'utilisateur est flagué
        flag_data = await supabase_client.check_user_flag(
            member.id, 
            member.guild.id, 
            member.guild.name
        )
        
        if flag_data:
            # Utilisateur flagué détecté
            await handle_flagged_user_join(member, flag_data)
            
    except Exception as e:
        logger.error(f"Erreur lors de la vérification de {member.display_name}: {e}")

@client.event
async def on_message(message):
    """Écouter les messages DM pour collecter les preuves et commande de test"""
    # Ignorer les messages du bot lui-même
    if message.author == client.user:
        return
    
    # Commande de test !agis
    if message.content.startswith('!agis'):
        embed = create_secure_embed(
            "🛡️ Agis Bot - Test",
            "Le bot Agis est opérationnel !",
            discord.Color.blue()
        )
        embed.add_field(name="Status", value="✅ Bot connecté et fonctionnel", inline=False)
        embed.add_field(name="Commande principale", value="/agis", inline=False)
        embed.add_field(name="Description", value="Anonymous Discord reporting bot to combat risky behaviors", inline=False)
        embed.set_footer(text="Protection • Vigilance • Communauté")
        
        await message.channel.send(embed=embed)
        return
    
    # Vérifier si c'est un DM (pas dans un serveur)
    if message.guild is None:
        await handle_dm_evidence(message)
    
    # Nettoyage périodique des mappings expirés (toutes les 100 messages environ)
    import random
    if random.randint(1, 100) == 1:
        evidence_collector.cleanup_expired()

async def handle_dm_evidence(message):
    """Traite les preuves reçues par DM"""
    user_id = message.author.id
    
    # Vérifier si l'utilisateur a un signalement en cours
    thread_id, report_id = evidence_collector.get_user_thread(user_id)
    if thread_id is None:
        # Pas de signalement en cours, ignorer
        return
    
    # Vérifier si l'utilisateur veut arrêter la collecte
    if message.content.strip().lower() == "valider":
        evidence_collector.remove_user_mapping(user_id)
        try:
            embed = create_secure_embed(
                "✅ Collecte de preuves validée",
                "Vos preuves ont été validées. Vous ne recevrez plus de demandes pour ce signalement.",
                discord.Color.orange()
            )
            await message.author.send(embed=embed)
        except discord.Forbidden:
            pass  # Ignore si on ne peut pas envoyer de DM
        return
    
    try:
        # Récupérer le thread correspondant
        thread = client.get_channel(thread_id)
        if thread is None:
            # Thread introuvable, supprimer le mapping
            evidence_collector.remove_user_mapping(user_id)
            return
        
        # Créer un embed pour les preuves anonymes
        evidence_embed = create_secure_embed(
            "📎 Preuve supplémentaire",
            f"**Signalement:** {report_id}\n**Source:** Rapporteur anonyme",
            discord.Color.green()
        )
        
        # Traiter le contenu du message
        if message.content.strip():
            # Nettoyer et valider le contenu
            clean_content = security_validator.sanitize_input(message.content, 2000)
            evidence_embed.add_field(
                name="📝 Contenu",
                value=clean_content,
                inline=False
            )
        
        # Traiter les pièces jointes de manière élégante
        attachments_info = []
        image_url = None
        files_to_send = []
        
        for attachment in message.attachments:
            # Vérifier la taille (Discord limite à 8MB pour les bots gratuits)
            if attachment.size > 8 * 1024 * 1024:  # 8MB
                attachments_info.append(f"❌ {attachment.filename} (trop volumineux)")
                continue
            
            attachments_info.append(f"📎 {attachment.filename} ({attachment.size} bytes)")
            
            # Si c'est une image, l'afficher dans l'embed
            if attachment.content_type and attachment.content_type.startswith('image/') and image_url is None:
                image_url = attachment.url
            else:
                # Pour les fichiers non-image, les préparer pour envoi séparé
                try:
                    file = await attachment.to_file()
                    files_to_send.append(file)
                except Exception as e:
                    logger.error(f"Erreur lors du transfert de pièce jointe: {e}")
        
        # Ajouter les infos des pièces jointes à l'embed
        if attachments_info:
            evidence_embed.add_field(
                name="📎 Pièces jointes",
                value="\n".join(attachments_info),
                inline=False
            )
        
        # Ajouter l'image à l'embed si c'est une image
        if image_url:
            evidence_embed.set_image(url=image_url)
        
        evidence_embed.add_field(
            name="🕐 Reçu le",
            value=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            inline=True
        )
        
        # Envoyer l'embed avec l'image intégrée
        await thread.send(embed=evidence_embed)
        
        # Envoyer les fichiers non-image séparément (seulement si nécessaire)
        if files_to_send:
            await thread.send(f"📎 **Fichiers joints ({report_id}):**", files=files_to_send)
        
        # Confirmer à l'utilisateur
        try:
            confirm_embed = create_secure_embed(
                "✅ Preuve transférée",
                f"Votre preuve a été ajoutée au signalement **{report_id}**.",
                discord.Color.green()
            )
            confirm_embed.add_field(
                name="💡 Continuez",
                value="Vous pouvez envoyer d'autres preuves ou taper `valider` pour terminer.",
                inline=False
            )
            await message.author.send(embed=confirm_embed)
        except discord.Forbidden:
            pass  # Ignore si on ne peut pas envoyer de DM
        
        # Log de l'action
        audit_logger.log_security_event(
            "EVIDENCE_RECEIVED",
            f"Evidence received for report {report_id}",
            user_id
        )
        
    except Exception as e:
        logger.error(f"Erreur lors du traitement de preuve DM: {e}")
        try:
            error_embed = create_secure_embed(
                "❌ Erreur",
                "Une erreur est survenue lors du transfert de votre preuve. Veuillez réessayer.",
                discord.Color.red()
            )
            await message.author.send(embed=error_embed)
        except discord.Forbidden:
            pass

async def handle_flagged_user_join(member, flag_data):
    """Gérer l'arrivée d'un utilisateur flagué"""
    guild_settings = guild_config.get_guild_config(member.guild.id)
    flag_level = flag_data["flag_level"]
    
    # Vérifier si l'utilisateur a un rôle d'exemption
    bypass_roles = guild_settings["permissions"]["bypass_auto_actions"]
    user_roles = [role.name for role in member.roles]
    
    if any(role in user_roles for role in bypass_roles):
        logger.info(f"Utilisateur {member.id} flagué mais exempté par rôle")
        return
    
    # Exécuter l'action automatique configurée
    auto_action = guild_settings["auto_actions"].get(flag_level, "alert")
    min_validations = guild_settings["thresholds"]["auto_action_min_validations"]
    
    # Vérifier si assez de validations pour auto-action
    if flag_data["validation_count"] >= min_validations:
        await execute_auto_action(member, auto_action, flag_data, guild_settings)
    
    # Envoyer l'alerte dans tous les cas
    await send_flag_alert(member, flag_data, guild_settings, auto_action)

async def execute_auto_action(member, action, flag_data, guild_settings):
    """Exécuter l'action automatique configurée"""
    try:
        if action == "ban":
            if guild_settings["thresholds"]["require_manual_review_for_ban"]:
                # Log pour review manuelle
                logger.warning(f"Ban automatique de {member.id} nécessite une review manuelle")
                return
            
            reason = f"Auto-ban Aegis: {flag_data['flag_reason']} (Niveau: {flag_data['flag_level']})"
            await member.ban(reason=reason)
            logger.info(f"Auto-ban exécuté pour {member.id}")
            
        elif action == "kick":
            reason = f"Auto-kick Aegis: {flag_data['flag_reason']} (Niveau: {flag_data['flag_level']})"
            await member.kick(reason=reason)
            logger.info(f"Auto-kick exécuté pour {member.id}")
            
        elif action == "quarantine":
            await apply_quarantine(member, guild_settings)
            logger.info(f"Quarantaine appliquée pour {member.id}")
            
    except Exception as e:
        logger.error(f"Erreur lors de l'auto-action {action} pour {member.id}: {e}")

async def apply_quarantine(member, guild_settings):
    """Appliquer la quarantaine à un membre"""
    quarantine_config = guild_settings["quarantine"]
    
    if not quarantine_config["enabled"]:
        return
    
    # Créer ou trouver le rôle de quarantaine
    quarantine_role = discord.utils.get(
        member.guild.roles, 
        name=quarantine_config["role_name"]
    )
    
    if not quarantine_role:
        # Créer le rôle de quarantaine avec permissions restrictives
        quarantine_role = await member.guild.create_role(
            name=quarantine_config["role_name"],
            color=discord.Color.orange(),
            reason="Rôle de quarantaine Aegis",
            permissions=discord.Permissions(
                view_channel=True,
                send_messages=False,
                add_reactions=False,
                connect=False
            )
        )
    
    # Sauvegarder les rôles actuels si configuré
    if quarantine_config["remove_roles"]:
        # Note: Dans un vrai bot, sauvegarder les rôles dans la DB
        await member.edit(roles=[quarantine_role], reason="Quarantaine Aegis")
    else:
        await member.add_roles(quarantine_role, reason="Quarantaine Aegis")

async def send_flag_alert(member, flag_data, guild_settings, executed_action):
    """Envoyer l'alerte de flag"""
    # Trouver le canal d'alertes de flags
    flag_channel = discord.utils.get(
        member.guild.channels, 
        name=BOT_CONFIG["FLAG_ALERT_CHANNEL"]
    )
    
    # Si pas de canal spécifique, utiliser le forum principal
    if not flag_channel:
        flag_channel = discord.utils.get(
            member.guild.channels, 
            name=BOT_CONFIG["ALERTS_CHANNEL_NAME"]
        )
    
    if flag_channel:
        embed = create_secure_embed(
            "🚨 Utilisateur flagué détecté",
            f"Un utilisateur flagué globalement vient de rejoindre le serveur",
            discord.Color.red()
        )
        
        embed.add_field(name="👤 Utilisateur", value=f"{member.mention} ({member.display_name})", inline=False)
        embed.add_field(name="🔴 Niveau de flag", value=flag_data["flag_level"].upper(), inline=True)
        embed.add_field(name="📂 Catégorie", value=flag_data["flag_category"], inline=True)
        embed.add_field(name="⚠️ Raison", value=flag_data["flag_reason"], inline=False)
        embed.add_field(name="🏠 Flagué par", value=flag_data["flagged_by_guild_name"] or "Serveur inconnu", inline=True)
        embed.add_field(name="📊 Validations", value=f"{flag_data['validation_count']} serveur(s)", inline=True)
        embed.add_field(name="📅 Flagué le", value=flag_data["flagged_date"].strftime("%d/%m/%Y"), inline=True)
        
        # Ajouter info sur l'action exécutée
        if executed_action != "alert":
            action_text = {
                "ban": "🚫 **BANNI AUTOMATIQUEMENT**",
                "kick": "👢 **EXPULSÉ AUTOMATIQUEMENT**", 
                "quarantine": "🔒 **MIS EN QUARANTAINE**",
                "none": "ℹ️ Aucune action automatique"
            }.get(executed_action, executed_action)
            
            embed.add_field(name="⚡ Action automatique", value=action_text, inline=False)
        
        embed.set_footer(text="Système de protection Aegis • Vérification automatique")
        
        # Mentionner les validateurs selon le niveau de flag
        mention_text = ""
        if flag_data["flag_level"] in ["high", "critical"]:
            validator_role = discord.utils.get(member.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
            if validator_role:
                mention_text = f"{validator_role.mention} - Attention requise !"
        
        if isinstance(flag_channel, discord.ForumChannel):
            # Créer un post dans le forum
            thread_title = f"🚨 FLAG: {member.display_name} ({flag_data['flag_level']})"
            thread = await flag_channel.create_thread(
                name=thread_title,
                content=mention_text,
                auto_archive_duration=BOT_CONFIG["AUTO_ARCHIVE_DURATION"]
            )
            await thread.send(embed=embed)
        else:
            # Envoyer dans un canal normal
            if mention_text:
                await flag_channel.send(mention_text)
            await flag_channel.send(embed=embed)
        
        # Log l'événement
        audit_logger.log_security_event(
            "FLAGGED_USER_JOIN",
            f"Utilisateur flagué {member.id} a rejoint {member.guild.id}",
            member.id
        )

# Créer un arbre de commandes et ajouter les commandes
tree = app_commands.CommandTree(client)
tree.add_command(agis_report)
tree.add_command(show_categories)
tree.add_command(validate_report)
tree.add_command(check_user)
tree.add_command(setup_agis)
# Ajouter les nouvelles commandes
tree.add_command(show_stats)
tree.add_command(export_reports)
tree.add_command(purge_forum_reports)
# Commandes de debug
tree.add_command(debug_system)
tree.add_command(test_supabase_manual)
# Commandes de test (conditionnelles selon TEST_MODE_ENABLED)
register_test_commands(tree)
# Commande anonymisation
tree.add_command(anonymise_report)

# Démarrage sécurisé du bot
if __name__ == "__main__":
    try:
        logger.info("Démarrage du bot Agis...")
        client.run(TOKEN)
    except Exception as e:
        logger.critical(f"Erreur critique lors du démarrage: {e}")
        exit(1)