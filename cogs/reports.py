"""
Cog pour les commandes de signalement
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from config.logging_config import get_logger
from config.bot_config import REPORT_CATEGORIES
from locales.translation_manager import translator
from ui.views.report_views import CategorySelectView
from ui.modals.report_modals import AgisReportModal

logger = get_logger('reports')


class ReportsCog(commands.Cog):
    """Commandes liées aux signalements"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(
        name="agis",
        description="Créer un signalement anonyme"
    )
    async def agis_command(self, interaction: discord.Interaction):
        """Commande principale pour créer un signalement"""
        try:
            logger.info(f"Commande /agis utilisée par {interaction.user} dans {interaction.guild}")
            
            # Vérifier que le serveur est configuré
            # TODO: Intégrer guild_config
            
            # Créer la vue de sélection de catégorie
            view = CategorySelectView(
                guild_id=interaction.guild_id,
                bot=self.bot,
                translator=translator
            )
            
            # Créer l'embed de présentation
            embed = discord.Embed(
                title=translator.t("report_modal_title", interaction.guild_id),
                description="Sélectionnez une catégorie pour votre signalement :",
                color=discord.Color.blue()
            )
            
            # Ajouter les catégories à l'embed
            categories_text = ""
            for category_id, category_data in REPORT_CATEGORIES.items():
                categories_text += f"{category_data['label']}\n{category_data['description']}\n\n"
            
            embed.add_field(
                name="📋 Catégories disponibles",
                value=categories_text[:1024],  # Limite Discord
                inline=False
            )
            
            await interaction.response.send_message(
                embed=embed,
                view=view,
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Erreur dans /agis: {e}")
            await self._send_error_message(interaction, "error_database_error")
    
    @app_commands.command(
        name="categories",
        description="Afficher les catégories de signalement disponibles"
    )
    async def categories_command(self, interaction: discord.Interaction):
        """Afficher toutes les catégories de signalement"""
        try:
            embed = discord.Embed(
                title="📋 Catégories de Signalement Aegis",
                description="Voici toutes les catégories disponibles pour vos signalements :",
                color=discord.Color.blue()
            )
            
            for category_id, category_data in REPORT_CATEGORIES.items():
                embed.add_field(
                    name=category_data['label'],
                    value=f"{category_data['description']}\n*Sévérité: {category_data['severity']}*",
                    inline=True
                )
            
            embed.set_footer(text="Utilisez /agis pour créer un signalement")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur dans /categories: {e}")
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
    await bot.add_cog(ReportsCog(bot))
    logger.info("✅ Cog Reports chargé")