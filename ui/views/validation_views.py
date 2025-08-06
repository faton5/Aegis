"""
Vues Discord pour la validation des signalements
"""
import discord
from discord.ui import View, Button
from typing import Optional

from config.logging_config import get_logger
from locales.translation_manager import translator

logger = get_logger('ui.validation_views')


class ReportValidationView(View):
    """Vue avec boutons de validation pour les signalements"""
    
    def __init__(self, report_id: str, guild_id: int, timeout: float = None):
        super().__init__(timeout=timeout)
        self.report_id = report_id
        self.guild_id = guild_id
    
    @discord.ui.button(
        label="✅ Valider", 
        style=discord.ButtonStyle.green, 
        custom_id="validate_report"
    )
    async def validate_report(self, interaction: discord.Interaction, button: Button):
        """Valider le signalement"""
        try:
            # Vérifier les permissions
            if not self._check_validator_permissions(interaction):
                await interaction.response.send_message(
                    "❌ Vous n'avez pas la permission de valider les signalements.",
                    ephemeral=True
                )
                return
            
            # Récupérer le signalement
            if hasattr(interaction.client, 'report_service'):
                report = await interaction.client.report_service.get_report(self.report_id)
                
                if not report:
                    await interaction.response.send_message(
                        "❌ Signalement non trouvé.",
                        ephemeral=True
                    )
                    return
                
                # Valider le signalement
                success = await interaction.client.report_service.update_report_status(
                    self.report_id, 
                    "validated", 
                    validator_id=interaction.user.id
                )
                
                if success:
                    # Sauvegarder dans Supabase si connecté
                    if hasattr(interaction.client.report_service, 'db') and interaction.client.report_service.db:
                        try:
                            # Déterminer le niveau basé sur le nombre de signalements validés du user
                            user_reports = [r for r in interaction.client.report_service.active_reports.values() 
                                          if r.target_username.lower() in [report.target_username.lower()] and r.status == "validated"]
                            validated_count = len(user_reports)
                            
                            if validated_count >= 3:
                                flag_level = "critical"
                            elif validated_count >= 2:
                                flag_level = "high"  
                            elif validated_count >= 1:
                                flag_level = "medium"
                            else:
                                flag_level = "low"
                            
                            # Ajouter à Supabase
                            await interaction.client.report_service.db.add_validated_report(
                                user_id=0,  # On n'a pas l'ID, seulement le username
                                username=report.target_username,
                                flag_level=flag_level,
                                reason=report.reason,
                                category=report.category,
                                guild_id=interaction.guild_id,
                                guild_name=interaction.guild.name
                            )
                            logger.info(f"Signalement {self.report_id} sauvé dans Supabase (niveau: {flag_level})")
                        except Exception as e:
                            logger.error(f"Erreur sauvegarde Supabase: {e}")
                    
                    # Envoyer feedback à l'utilisateur
                    await self._send_validation_feedback(interaction, report, "validated")
                    
                    # Créer l'embed de validation
                    embed = discord.Embed(
                        title="✅ Signalement Validé",
                        description=f"Signalement **#{self.report_id}** validé par {interaction.user.mention}",
                        color=discord.Color.green()
                    )
                    
                    embed.add_field(
                        name="🏷️ Statut",
                        value="Validé ✅",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="👤 Validé par",
                        value=interaction.user.mention,
                        inline=True
                    )
                    
                    embed.set_timestamp()
                    
                    # Désactiver les boutons
                    for item in self.children:
                        item.disabled = True
                    
                    # Modifier le message original
                    await interaction.response.edit_message(
                        embed=embed,
                        view=self
                    )
                    
                    logger.info(f"Signalement {self.report_id} validé par {interaction.user}")
                    
                    # TODO: Appliquer les actions automatiques selon la configuration
                    
                else:
                    await interaction.response.send_message(
                        "❌ Erreur lors de la validation.",
                        ephemeral=True
                    )
            
        except Exception as e:
            logger.error(f"Erreur validation signalement {self.report_id}: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la validation.",
                ephemeral=True
            )
    
    @discord.ui.button(
        label="❌ Refuser", 
        style=discord.ButtonStyle.red, 
        custom_id="reject_report"
    )
    async def reject_report(self, interaction: discord.Interaction, button: Button):
        """Refuser le signalement"""
        try:
            # Vérifier les permissions
            if not self._check_validator_permissions(interaction):
                await interaction.response.send_message(
                    "❌ Vous n'avez pas la permission de refuser les signalements.",
                    ephemeral=True
                )
                return
            
            # Récupérer le signalement
            if hasattr(interaction.client, 'report_service'):
                report = await interaction.client.report_service.get_report(self.report_id)
                
                if not report:
                    await interaction.response.send_message(
                        "❌ Signalement non trouvé.",
                        ephemeral=True
                    )
                    return
                
                # Refuser le signalement
                success = await interaction.client.report_service.update_report_status(
                    self.report_id, 
                    "rejected", 
                    validator_id=interaction.user.id
                )
                
                if success:
                    # Envoyer feedback à l'utilisateur
                    await self._send_validation_feedback(interaction, report, "rejected")
                    
                    # Créer l'embed de rejet
                    embed = discord.Embed(
                        title="❌ Signalement Refusé",
                        description=f"Signalement **#{self.report_id}** refusé par {interaction.user.mention}",
                        color=discord.Color.red()
                    )
                    
                    embed.add_field(
                        name="🏷️ Statut",
                        value="Refusé ❌",
                        inline=True
                    )
                    
                    embed.add_field(
                        name="👤 Refusé par",
                        value=interaction.user.mention,
                        inline=True
                    )
                    
                    embed.set_timestamp()
                    
                    # Désactiver les boutons
                    for item in self.children:
                        item.disabled = True
                    
                    # Modifier le message original
                    await interaction.response.edit_message(
                        embed=embed,
                        view=self
                    )
                    
                    logger.info(f"Signalement {self.report_id} refusé par {interaction.user}")
                    
                else:
                    await interaction.response.send_message(
                        "❌ Erreur lors du refus.",
                        ephemeral=True
                    )
            
        except Exception as e:
            logger.error(f"Erreur refus signalement {self.report_id}: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors du refus.",
                ephemeral=True
            )
    
    @discord.ui.button(
        label="📋 Plus d'infos", 
        style=discord.ButtonStyle.secondary, 
        custom_id="request_more_info"
    )
    async def request_more_info(self, interaction: discord.Interaction, button: Button):
        """Demander plus d'informations"""
        try:
            # Vérifier les permissions
            if not self._check_validator_permissions(interaction):
                await interaction.response.send_message(
                    "❌ Vous n'avez pas la permission de demander plus d'informations.",
                    ephemeral=True
                )
                return
            
            # Récupérer le signalement
            if hasattr(interaction.client, 'report_service'):
                report = await interaction.client.report_service.get_report(self.report_id)
                
                if not report:
                    await interaction.response.send_message(
                        "❌ Signalement non trouvé.",
                        ephemeral=True
                    )
                    return
                
                # Récupérer l'utilisateur qui a signalé
                try:
                    reporter = await interaction.client.fetch_user(report.reporter_id)
                    
                    # Envoyer un MP demandant plus d'infos
                    embed = discord.Embed(
                        title="📋 Informations Supplémentaires Demandées",
                        description=f"Les modérateurs de **{interaction.guild.name}** souhaitent obtenir plus d'informations concernant votre signalement **#{self.report_id}**.",
                        color=discord.Color.blue()
                    )
                    
                    embed.add_field(
                        name="📝 Signalement Initial",
                        value=f"**Utilisateur signalé:** `{report.target_username}`\n**Catégorie:** {report.category}\n**Raison:** {report.reason}",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="💭 Demande",
                        value="Pourriez-vous fournir des détails supplémentaires ou des preuves pour nous aider à mieux évaluer ce signalement ?",
                        inline=False
                    )
                    
                    embed.add_field(
                        name="📬 Comment répondre",
                        value="Répondez simplement à ce message avec les informations supplémentaires.",
                        inline=False
                    )
                    
                    embed.set_footer(
                        text=f"Demandé par {interaction.user.display_name}",
                        icon_url=interaction.user.display_avatar.url
                    )
                    
                    await reporter.send(embed=embed)
                    
                    # Confirmer l'envoi
                    await interaction.response.send_message(
                        f"✅ Demande d'informations envoyée à {reporter.mention}.",
                        ephemeral=True
                    )
                    
                    # Ajouter un message dans le thread
                    embed_thread = discord.Embed(
                        title="📋 Plus d'Infos Demandées",
                        description=f"{interaction.user.mention} a demandé plus d'informations au rapporteur.",
                        color=discord.Color.blue()
                    )
                    
                    await interaction.followup.send(embed=embed_thread)
                    
                    logger.info(f"Infos supplémentaires demandées pour {self.report_id} par {interaction.user}")
                    
                except discord.Forbidden:
                    await interaction.response.send_message(
                        "❌ Impossible d'envoyer un message privé à l'utilisateur (DM fermés).",
                        ephemeral=True
                    )
                except Exception as e:
                    logger.error(f"Erreur envoi demande infos: {e}")
                    await interaction.response.send_message(
                        "❌ Erreur lors de l'envoi de la demande.",
                        ephemeral=True
                    )
            
        except Exception as e:
            logger.error(f"Erreur demande infos signalement {self.report_id}: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la demande d'informations.",
                ephemeral=True
            )
    
    def _check_validator_permissions(self, interaction: discord.Interaction) -> bool:
        """Vérifier si l'utilisateur a les permissions de validation"""
        try:
            from services.guild_service import guild_service
            config = guild_service.get_guild_config(interaction.guild_id)
            validator_role_id = config.get('validator_role_id')
            
            if not validator_role_id:
                return interaction.user.guild_permissions.administrator
            
            validator_role = interaction.guild.get_role(validator_role_id)
            if validator_role and validator_role in interaction.user.roles:
                return True
            
            return interaction.user.guild_permissions.administrator
            
        except Exception as e:
            logger.error(f"Erreur vérification permissions: {e}")
            return interaction.user.guild_permissions.administrator
    
    async def _send_validation_feedback(self, interaction: discord.Interaction, report, status: str):
        """Envoyer un feedback automatique à l'utilisateur qui a fait le signalement"""
        try:
            # Récupérer l'utilisateur qui a fait le signalement
            reporter = await interaction.client.fetch_user(report.reporter_id)
            
            # Déterminer les détails selon le statut
            if status == "validated":
                title = "✅ Signalement Validé"
                color = discord.Color.green()
                decision = "**Validé** par l'équipe de modération"
                
                # Déterminer l'action prise selon la config
                from services.guild_service import guild_service
                config = guild_service.get_guild_config(interaction.guild_id)
                auto_actions = config.get('auto_actions', {})
                
                # Calculer le niveau basé sur les signalements validés
                user_reports = [r for r in interaction.client.report_service.active_reports.values() 
                              if r.target_username.lower() == report.target_username.lower() and r.status == "validated"]
                validated_count = len(user_reports)
                
                if validated_count >= 3:
                    level = "critical"
                elif validated_count >= 2:
                    level = "high"
                elif validated_count >= 1:
                    level = "medium"
                else:
                    level = "low"
                
                action_taken = auto_actions.get(level, "none")
                action_text = {
                    "ban": "🔨 Utilisateur banni",
                    "kick": "👢 Utilisateur expulsé", 
                    "quarantine": "🔒 Utilisateur mis en quarantaine",
                    "alert": "⚠️ Modérateurs alertés",
                    "none": "📋 Signalement enregistré"
                }.get(action_taken, "📋 Action manuelle nécessaire")
                
            else:  # rejected
                title = "❌ Signalement Non Retenu"
                color = discord.Color.orange()
                decision = "**Non retenu** après examen"
                action_text = "Aucune action prise"
            
            # Créer l'embed de feedback
            embed = discord.Embed(
                title=title,
                description=f"Votre signalement **#{report.id}** a été analysé.",
                color=color,
                timestamp=interaction.created_at
            )
            
            embed.add_field(
                name="📋 Signalement",
                value=f"**Utilisateur:** `{report.target_username}`\n**Catégorie:** {report.category}\n**Raison:** {report.reason[:100]}{'...' if len(report.reason) > 100 else ''}",
                inline=False
            )
            
            embed.add_field(
                name="⚖️ Décision",
                value=decision,
                inline=True
            )
            
            embed.add_field(
                name="🔧 Action Prise",
                value=action_text,
                inline=True
            )
            
            embed.add_field(
                name="🏠 Serveur",
                value=interaction.guild.name,
                inline=True
            )
            
            embed.set_footer(
                text="Merci pour votre contribution à la sécurité de la communauté",
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None
            )
            
            # Envoyer le MP
            await reporter.send(embed=embed)
            logger.info(f"Feedback {status} envoyé à {reporter} pour signalement {report.id}")
            
        except discord.Forbidden:
            logger.warning(f"Impossible d'envoyer feedback à l'utilisateur {report.reporter_id} (DM fermés)")
        except Exception as e:
            logger.error(f"Erreur envoi feedback pour signalement {report.id}: {e}")