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
        
        # Champ nom d'utilisateur cible (accepte @mentions, noms, IDs)
        self.target_input = TextInput(
            label=self.translator.t("report_modal_target_label", self.guild_id),
            placeholder=self.translator.t("report_modal_target_placeholder", self.guild_id),
            required=True,
            max_length=100,  # Augmenté pour les mentions
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
        
    
    async def on_submit(self, interaction: discord.Interaction):
        """Quand le modal est soumis"""
        try:
            logger.info(f"Signalement soumis par {interaction.user} dans {interaction.guild}")
            
            # Récupérer les valeurs et extraire l'utilisateur
            target_raw = self.target_input.value.strip()
            reason = self.reason_input.value.strip()
            evidence = ""  # Preuves via MP uniquement
            
            # Extraire les infos utilisateur (nom/ID)
            target_user_data = await self._extract_user_info(interaction, target_raw)
            if not target_user_data:
                await interaction.response.send_message(
                    f"❌ {self.translator.t('report_target_invalid', self.guild_id)}",
                    ephemeral=True
                )
                return
            
            target_username, target_user_id = target_user_data
            
            # Valider les données
            is_valid, error_msg = self.bot.security_validator.validate_report_data(
                target_username, reason, evidence
            )
            
            if not is_valid:
                await interaction.response.send_message(
                    f"❌ {error_msg}",
                    ephemeral=True
                )
                return
            
            # Créer le signalement via le service (avec user ID si disponible)
            report = await self.bot.report_service.create_report(
                user_id=interaction.user.id,
                guild_id=interaction.guild_id,
                target_username=target_username,
                target_user_id=target_user_id,  # Nouveau paramètre
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
            await self._send_confirmation(interaction, report, target_username)
            
            # Créer le post dans le forum si configuré
            await self._create_forum_post(interaction, report, target_username)
            
            # Note: Les preuves peuvent être ajoutées via MP ultérieurement (transférées automatiquement)
            
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
                value=f"**ID**: `{report.id}`\n**Statut**: {self.translator.t('report_status_pending', self.guild_id)}",
                inline=False
            )
            
            embed.set_footer(
                text=self.translator.t('report_footer_review', self.guild_id),
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
                    self.translator.t('error_report_processing', self.guild_id),
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
            
            # Note: Les preuves sont ajoutées via MP (transférées automatiquement)
            
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
            
            # Créer la vue avec boutons de validation
            from ui.views.validation_views import ReportValidationView
            validation_view = ReportValidationView(report.id, interaction.guild_id)
            
            # Créer le post dans le forum
            thread_with_message = await forum_channel.create_thread(
                name=f"AEGIS-{report.id}",
                embed=embed,
                view=validation_view,
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
    
    
    async def _extract_user_info(self, interaction: discord.Interaction, target_input: str):
        """Extraire les informations utilisateur depuis une mention, nom ou ID"""
        import re
        
        try:
            target_input = target_input.strip()
            
            # 1. Vérifier si c'est une mention (<@123456789> ou <@!123456789>)
            mention_match = re.match(r'<@!?(\d+)>', target_input)
            if mention_match:
                user_id = int(mention_match.group(1))
                try:
                    user = await interaction.client.fetch_user(user_id)
                    return (user.name, user_id)
                except:
                    return (f"Unknown#{user_id}", user_id)
            
            # 2. Vérifier si c'est un ID numérique pur
            if target_input.isdigit():
                user_id = int(target_input)
                try:
                    user = await interaction.client.fetch_user(user_id)
                    return (user.name, user_id)
                except:
                    return (f"Unknown#{user_id}", user_id)
            
            # 3. Chercher par nom dans le serveur
            if interaction.guild:
                # Chercher par nom exact
                for member in interaction.guild.members:
                    if member.name.lower() == target_input.lower() or member.display_name.lower() == target_input.lower():
                        return (member.name, member.id)
                
                # Chercher par nom partiel si pas trouvé
                for member in interaction.guild.members:
                    if target_input.lower() in member.name.lower() or target_input.lower() in member.display_name.lower():
                        return (member.name, member.id)
            
            # 4. Si aucune correspondance, traiter comme nom d'utilisateur (sans ID)
            if len(target_input) >= 2 and len(target_input) <= 32:
                return (target_input, None)
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur extraction utilisateur '{target_input}': {e}")
            return None