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