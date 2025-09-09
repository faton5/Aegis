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
        description="Create an anonymous report"
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
                title=translator.t("agis_command_title", interaction.guild_id),
                description=translator.t("agis_command_description", interaction.guild_id),
                color=discord.Color.blue()
            )
            
            # Ajouter les catégories à l'embed (traduites)
            categories_text = ""
            for category_id, category_data in REPORT_CATEGORIES.items():
                label_key = f"category_{category_id}"
                desc_key = f"category_{category_id}_description"
                label = translator.t(label_key, interaction.guild_id, fallback=category_data['label'])
                description = translator.t(desc_key, interaction.guild_id, fallback=category_data['description'])
                categories_text += f"{label}\n{description}\n\n"
            
            embed.add_field(
                name=translator.t("agis_categories_field", interaction.guild_id),
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
        description="Display available report categories"
    )
    async def categories_command(self, interaction: discord.Interaction):
        """Afficher toutes les catégories de signalement"""
        try:
            embed = discord.Embed(
                title=translator.t("categories_command_title", interaction.guild_id),
                description=translator.t("categories_command_description", interaction.guild_id),
                color=discord.Color.blue()
            )
            
            for category_id, category_data in REPORT_CATEGORIES.items():
                label_key = f"category_{category_id}"
                desc_key = f"category_{category_id}_description"
                label = translator.t(label_key, interaction.guild_id, fallback=category_data['label'])
                description = translator.t(desc_key, interaction.guild_id, fallback=category_data['description'])
                severity_label = translator.t("severity_label", interaction.guild_id)
                
                embed.add_field(
                    name=label,
                    value=f"{description}\n*{severity_label}: {category_data['severity']}*",
                    inline=True
                )
            
            embed.set_footer(text=translator.t("categories_command_footer", interaction.guild_id))
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur dans /categories: {e}")
            await self._send_error_message(interaction, "error_database_error")
    
    async def _send_error_message(self, interaction: discord.Interaction, error_key: str):
        """Envoyer un message d'erreur traduit"""
        try:
            error_message = translator.t(error_key, interaction.guild_id)
            
            embed = discord.Embed(
                title=translator.t("error_title", interaction.guild_id),
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
