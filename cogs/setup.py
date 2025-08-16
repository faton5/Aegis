"""
Cog pour les commandes de configuration du serveur
"""
import discord
from discord import app_commands
from discord.ext import commands

from config.logging_config import get_logger
from locales.translation_manager import translator
from ui.views.setup_views import SetupMainView

logger = get_logger('setup')


class SetupCog(commands.Cog):
    """Commandes de configuration du serveur"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(
        name="setup",
        description="Configurer Aegis pour votre serveur"
    )
    async def setup_command(self, interaction: discord.Interaction):
        """Commande principale de configuration"""
        try:
            # Vérifier les permissions administrateur
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    translator.t("error_missing_permissions", interaction.guild_id),
                    ephemeral=True
                )
                return
            
            logger.info(f"Commande /setup utilisée par {interaction.user} dans {interaction.guild}")
            
            # Créer la vue principale de configuration
            view = SetupMainView(interaction.guild_id)
            
            # Créer l'embed de bienvenue
            embed = discord.Embed(
                title=translator.t("setup_welcome_title", interaction.guild_id),
                description=translator.t("setup_welcome_description", interaction.guild_id),
                color=discord.Color.blue()
            )
            
            # Ajouter des informations sur le serveur
            embed.add_field(
                name="🏠 Serveur",
                value=f"{interaction.guild.name}\n{interaction.guild.member_count} membres",
                inline=True
            )
            
            embed.add_field(
                name="👤 Administrateur",
                value=f"{interaction.user.mention}",
                inline=True
            )
            
            # Vérifier l'état actuel
            try:
                from services.guild_service import guild_service
                
                config = guild_service.get_guild_config(interaction.guild_id)
                status = translator.t("setup_status_configured", interaction.guild_id) if config.get('configured', False) else translator.t("setup_status_to_configure", interaction.guild_id)
                
                embed.add_field(
                    name=translator.t("setup_state_field", interaction.guild_id),
                    value=status,
                    inline=True
                )
            except Exception as e:
                logger.warning(f"Impossible de vérifier l'état de configuration: {e}")
            
            embed.set_footer(text="Utilisez les boutons ci-dessous pour configurer le bot")
            
            await interaction.response.send_message(
                embed=embed,
                view=view,
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Erreur dans /setup: {e}")
            await self._send_error_message(interaction, "error_database_error")
    
    async def _send_error_message(self, interaction: discord.Interaction, error_key: str):
        """Envoyer un message d'erreur traduit"""
        try:
            error_message = translator.t(error_key, interaction.guild_id)
            
            embed = discord.Embed(
                title="❌ Erreur",
                description=error_message,
                color=discord.Color.red()
            )
            
            if interaction.response.is_done():
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True)
                
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du message d'erreur: {e}")


async def setup(bot):
    """Fonction appelée lors du chargement du cog"""
    await bot.add_cog(SetupCog(bot))
<<<<<<< HEAD
    # Cog chargé silencieusement
=======
    logger.info("✅ Cog Setup chargé")
>>>>>>> a512c3414221258fe8b4b13148490d4f0b66e5d7
