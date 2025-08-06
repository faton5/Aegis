"""
Modals Discord pour les signalements
"""
import discord
from discord.ui import Modal, TextInput
from typing import Optional

from config.logging_config import get_logger
from config.bot_config import REPORT_CATEGORIES

logger = get_logger('ui.report_modals')


class AgisReportModal(Modal):
    """Modal pour créer un signalement"""
    
    def __init__(self, category: str, guild_id: int, bot, translator):
        self.category = category
        self.guild_id = guild_id
        self.bot = bot
        self.translator = translator
        
        # Titre du modal traduit
        title = self.translator.t("report_modal_title", guild_id)
        super().__init__(title=title, timeout=600)  # 10 minutes
        
        self._create_inputs()
    
    def _create_inputs(self):
        """Créer les champs de saisie"""
        
        # Champ nom d'utilisateur cible
        self.target_input = TextInput(
            label=self.translator.t("report_modal_target_label", self.guild_id),
            placeholder=self.translator.t("report_modal_target_placeholder", self.guild_id),
            required=True,
            max_length=32,
            style=discord.TextStyle.short
        )
        self.add_item(self.target_input)
        
        # Champ raison
        self.reason_input = TextInput(
            label=self.translator.t("report_modal_reason_label", self.guild_id),
            placeholder=self.translator.t("report_modal_reason_placeholder", self.guild_id),
            required=True,
            max_length=500,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.reason_input)
        
        # Champ preuves (optionnel)
        self.evidence_input = TextInput(
            label=self.translator.t("report_modal_evidence_label", self.guild_id),
            placeholder=self.translator.t("report_modal_evidence_placeholder", self.guild_id),
            required=False,
            max_length=1900,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.evidence_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        """Quand le modal est soumis"""
        try:
            logger.info(f"Signalement soumis par {interaction.user} dans {interaction.guild}")
            
            # Récupérer les valeurs
            target = self.target_input.value.strip()
            reason = self.reason_input.value.strip()
            evidence = self.evidence_input.value.strip() if self.evidence_input.value else ""
            
            # Valider les données
            is_valid, error_msg = self.bot.security_validator.validate_report_data(
                target, reason, evidence
            )
            
            if not is_valid:
                await interaction.response.send_message(
                    f"❌ {error_msg}",
                    ephemeral=True
                )
                return
            
            # Créer le signalement via le service
            report = await self.bot.report_service.create_report(
                user_id=interaction.user.id,
                guild_id=interaction.guild_id,
                target_username=target,
                category=self.category,
                reason=reason,
                evidence=evidence
            )
            
            if not report:
                # Vérifier si c'est un problème de rate limiting
                remaining_time = self.bot.rate_limiter.get_remaining_time(
                    interaction.user.id, interaction.guild_id
                )
                
                if remaining_time > 0:
                    error_msg = self.translator.t(
                        "error_rate_limited", 
                        self.guild_id,
                        time=remaining_time // 60 + 1  # Minutes
                    )
                else:
                    error_msg = self.translator.t("error_database_error", self.guild_id)
                
                await interaction.response.send_message(
                    f"❌ {error_msg}",
                    ephemeral=True
                )
                return
            
            # Créer l'embed de confirmation
            await self._send_confirmation(interaction, report, target)
            
            # Créer le post dans le forum si configuré
            await self._create_forum_post(interaction, report, target)
            
            # Envoyer MP pour les preuves si nécessaire
            await self._send_evidence_dm(interaction, report)
            
            # Notifier les modérateurs
            await self._notify_moderators(report)
            
        except Exception as e:
            logger.error(f"Erreur lors de la soumission du signalement: {e}")
            
            try:
                error_msg = self.translator.t("error_database_error", self.guild_id)
                await interaction.response.send_message(
                    f"❌ {error_msg}",
                    ephemeral=True
                )
            except:
                pass  # Éviter les erreurs en cascade
    
    async def _send_confirmation(self, interaction: discord.Interaction, report, target: str):
        """Envoyer la confirmation du signalement"""
        try:
            # Obtenir le nom de la catégorie traduit
            category_label = REPORT_CATEGORIES[self.category]['label']
            
            # Créer l'embed
            embed = discord.Embed(
                title=self.translator.t("report_submitted_title", self.guild_id),
                description=self.translator.t(
                    "report_submitted_description",
                    self.guild_id,
                    report_id=report.id,
                    target=target,
                    category=category_label
                ),
                color=discord.Color.green(),
                timestamp=report.created_at
            )
            
            embed.add_field(
                name="📋 Informations",
                value=f"**ID**: `{report.id}`\n**Statut**: En attente de validation",
                inline=False
            )
            
            embed.set_footer(
                text="Les modérateurs examineront votre signalement sous peu.",
                icon_url=interaction.user.display_avatar.url
            )
            
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la confirmation: {e}")
    
    async def on_error(self, interaction: discord.Interaction, error: Exception):
        """Gestionnaire d'erreurs du modal"""
        logger.error(f"Erreur dans AgisReportModal: {error}")
        
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Une erreur s'est produite lors du traitement de votre signalement.",
                    ephemeral=True
                )
        except:
            pass
    
    async def _create_forum_post(self, interaction: discord.Interaction, report, target: str):
        """Créer un post dans le forum Discord pour le signalement"""
        try:
            # Récupérer la configuration du serveur
            from services.guild_service import guild_service
            config = guild_service.get_guild_config(interaction.guild_id)
            
            forum_channel_id = config.get('forum_channel_id')
            
            if not forum_channel_id:
                logger.warning(f"Aucun forum configuré pour guild {interaction.guild_id}")
                return
            
            # Récupérer le canal forum
            forum_channel = self.bot.get_channel(forum_channel_id)
            if not forum_channel or not isinstance(forum_channel, discord.ForumChannel):
                logger.error(f"Forum channel {forum_channel_id} non trouvé ou invalide")
                return
            
            # Obtenir le nom de la catégorie traduit
            category_info = REPORT_CATEGORIES.get(self.category, {})
            category_label = category_info.get('label', self.category)
            category_emoji = category_info.get('emoji', '⚠️')
            
            # Créer l'embed du signalement
            embed = discord.Embed(
                title=f"{category_emoji} Signalement #{report.id}",
                description=f"**Utilisateur signalé :** `{target}`\n**Catégorie :** {category_label}",
                color=category_info.get('color', discord.Color.orange()),
                timestamp=report.created_at
            )
            
            embed.add_field(
                name="📝 Raison",
                value=report.reason,
                inline=False
            )
            
            if report.evidence:
                embed.add_field(
                    name="🔍 Preuves",
                    value=report.evidence,
                    inline=False
                )
            
            embed.add_field(
                name="📊 Statut",
                value="🔄 En attente de validation",
                inline=True
            )
            
            embed.add_field(
                name="👥 Validations",
                value="0 / 2",
                inline=True
            )
            
            embed.set_footer(
                text=f"Signalé par un utilisateur • ID: {report.id}",
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None
            )
            
            # Créer le post dans le forum
            thread_with_message = await forum_channel.create_thread(
                name=f"AEGIS-{report.id}",
                embed=embed,
                reason=f"Signalement automatique #{report.id}"
            )
            
            # Récupérer le thread créé
            thread = thread_with_message.thread
            
            # Sauvegarder l'ID du thread
            report.thread_id = thread.id
            
            logger.info(f"Post forum créé: {thread.id} pour signalement {report.id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du post forum: {e}")
    
    async def _notify_moderators(self, report):
        """Notifier les modérateurs du nouveau signalement"""
        try:
            from services.guild_service import guild_service
            config = guild_service.get_guild_config(report.guild_id)
            
            validator_role_id = config.get('validator_role_id')
            
            if validator_role_id and report.thread_id:
                # Récupérer le thread du forum
                thread = self.bot.get_channel(report.thread_id)
                if thread:
                    # Ping le rôle validateur
                    await thread.send(
                        f"<@&{validator_role_id}> Nouveau signalement à examiner !"
                    )
                    logger.info(f"Modérateurs notifiés pour signalement {report.id}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la notification des modérateurs: {e}")
    
    async def _send_evidence_dm(self, interaction: discord.Interaction, report):
        """Envoyer un MP à l'utilisateur pour demander des preuves supplémentaires si nécessaire"""
        try:
            # Vérifier si des preuves ont été fournies
            if report.evidence and len(report.evidence.strip()) > 10:
                return  # Des preuves suffisantes ont été fournies
            
            # Créer l'embed du MP
            embed = discord.Embed(
                title="🔍 Preuves Supplémentaires",
                description=f"Merci pour votre signalement **#{report.id}**.\n\nPour nous aider à traiter votre signalement plus efficacement, vous pouvez nous envoyer des **preuves supplémentaires** :",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📋 Types de preuves utiles",
                value="• Captures d'écran\n• Liens vers des messages\n• Historique de conversation\n• Autres éléments pertinents",
                inline=False
            )
            
            embed.add_field(
                name="📬 Comment procéder",
                value=f"Répondez simplement à ce message avec vos preuves.\n\n**Votre signalement sera traité même sans preuves supplémentaires.**",
                inline=False
            )
            
            embed.set_footer(
                text=f"Signalement #{report.id} • Aegis Bot",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            
            # Envoyer le MP
            await interaction.user.send(embed=embed)
            logger.info(f"MP pour preuves envoyé à {interaction.user} pour signalement {report.id}")
            
        except discord.Forbidden:
            logger.warning(f"Impossible d'envoyer un MP à {interaction.user} (DM fermés)")
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du MP pour preuves: {e}")