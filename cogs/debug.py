"""
Cog pour les commandes de debug (mode développement uniquement)
"""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import sys
from typing import Optional

from config.logging_config import get_logger
from config.bot_config import bot_settings

logger = get_logger('debug')


class DebugCog(commands.Cog):
    """Commandes de debug et développement"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        """Vérifier que le mode debug est activé pour ce serveur"""
        # Si ctx est une interaction (slash command)
        if hasattr(ctx, 'guild_id') and ctx.guild_id:
            try:
                from services.guild_service import guild_service
                guild_config = guild_service.get_guild_config(ctx.guild_id)
                return guild_config.get('debug_enabled', False)
            except Exception:
                return False
        # Fallback sur la config globale si pas de serveur
        return bot_settings.debug_enabled
    
    @app_commands.command(
        name="debug-info",
        description="[DEBUG] Informations système et bot"
    )
    async def debug_info_command(self, interaction: discord.Interaction):
        """Afficher les informations de debug"""
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            embed = discord.Embed(
                title="🔧 Debug - Informations Système",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            
            # Informations Python
            embed.add_field(
                name="🐍 Python",
                value=f"Version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\nPlateforme: {sys.platform}",
                inline=True
            )
            
            # Informations Discord.py
            embed.add_field(
                name="🤖 Discord.py",
                value=f"Version: {discord.__version__}",
                inline=True
            )
            
            # Informations Bot
            if hasattr(self.bot, 'startup_time') and self.bot.startup_time:
                uptime = datetime.utcnow() - self.bot.startup_time
                uptime_str = f"{uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m"
            else:
                uptime_str = "N/A"
            
            embed.add_field(
                name="⏱️ Bot",
                value=f"Uptime: {uptime_str}\nServeurs: {len(self.bot.guilds)}\nLatence: {round(self.bot.latency * 1000)}ms",
                inline=True
            )
            
            # Configuration
            embed.add_field(
                name="⚙️ Configuration",
                value=f"Test Mode: {bot_settings.test_mode_enabled}\nDebug: {bot_settings.debug_enabled}\nSupabase: {bot_settings.supabase_enabled}",
                inline=True
            )
            
            # Services
            services_status = []
            if hasattr(self.bot, 'report_service'):
                active_reports = len(self.bot.report_service.active_reports)
                services_status.append(f"Reports: {active_reports}")
            
            if hasattr(self.bot, 'rate_limiter'):
                stats = self.bot.rate_limiter.get_stats()
                services_status.append(f"Rate Limiter: {stats['active_users']} users")
            
            if services_status:
                embed.add_field(
                    name="🔧 Services",
                    value="\n".join(services_status),
                    inline=True
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur dans /debug-info: {e}")
            await interaction.followup.send(
                f"❌ Erreur: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(
        name="debug-translations",
        description="[DEBUG] Tester le système de traductions"
    )
    async def debug_translations_command(self, interaction: discord.Interaction, key: str, language: Optional[str] = None):
        """Tester une clé de traduction"""
        
        try:
            from locales.translation_manager import translator
            
            # Tester la traduction
            result = translator.t(key, interaction.guild_id, language=language)
            
            embed = discord.Embed(
                title="🌐 Debug - Traductions",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="🔑 Clé",
                value=f"`{key}`",
                inline=False
            )
            
            embed.add_field(
                name="🏷️ Langue demandée",
                value=language or "Auto (serveur)",
                inline=True
            )
            
            embed.add_field(
                name="🏷️ Langue utilisée",
                value=language or translator._get_guild_language(interaction.guild_id) or translator.default_language,
                inline=True
            )
            
            embed.add_field(
                name="📝 Résultat",
                value=f"```\n{result}\n```",
                inline=False
            )
            
            # Statistiques des traductions
            stats = translator.get_stats()
            embed.add_field(
                name="📊 Stats",
                value=f"Langues: {stats['languages']}\nClés totales: {stats['total_keys']}",
                inline=True
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur dans /debug-translations: {e}")
            await interaction.response.send_message(
                f"❌ Erreur: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(
        name="debug-services",
        description="[DEBUG] État des services du bot"
    )
    async def debug_services_command(self, interaction: discord.Interaction):
        """Vérifier l'état des services"""
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            embed = discord.Embed(
                title="🔧 Debug - Services",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            # Service de signalements
            if hasattr(self.bot, 'report_service') and self.bot.report_service:
                reports_count = len(self.bot.report_service.active_reports)
                embed.add_field(
                    name="📋 ReportService",
                    value=f"✅ Actif\n{reports_count} signalements actifs",
                    inline=True
                )
            else:
                embed.add_field(
                    name="📋 ReportService",
                    value="❌ Non disponible",
                    inline=True
                )
            
            # Rate Limiter
            if hasattr(self.bot, 'rate_limiter') and self.bot.rate_limiter:
                stats = self.bot.rate_limiter.get_stats()
                embed.add_field(
                    name="⏱️ RateLimiter",
                    value=f"✅ Actif\n{stats['active_users']} utilisateurs surveillés\n{stats['total_tracked_actions']} actions trackées",
                    inline=True
                )
            else:
                embed.add_field(
                    name="⏱️ RateLimiter",
                    value="❌ Non disponible",
                    inline=True
                )
            
            # Security Validator
            if hasattr(self.bot, 'security_validator') and self.bot.security_validator:
                embed.add_field(
                    name="🛡️ SecurityValidator",
                    value="✅ Actif",
                    inline=True
                )
            else:
                embed.add_field(
                    name="🛡️ SecurityValidator",
                    value="❌ Non disponible",
                    inline=True
                )
            
            # Traductions
            try:
                from locales.translation_manager import translator
                stats = translator.get_stats()
                embed.add_field(
                    name="🌐 Translations",
                    value=f"✅ Actif\n{stats['languages']} langues\n{stats['total_keys']} clés",
                    inline=True
                )
            except Exception as e:
                embed.add_field(
                    name="🌐 Translations",
                    value=f"❌ Erreur: {str(e)[:50]}",
                    inline=True
                )
            
            # Guild Service
            try:
                from services.guild_service import guild_service
                stats = guild_service.get_stats()
                embed.add_field(
                    name="🏠 GuildService",
                    value=f"✅ Actif\n{stats['configured_guilds']} serveurs configurés",
                    inline=True
                )
            except Exception as e:
                embed.add_field(
                    name="🏠 GuildService",
                    value=f"❌ Erreur: {str(e)[:50]}",
                    inline=True
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur dans /debug-services: {e}")
            await interaction.followup.send(
                f"❌ Erreur: {str(e)}",
                ephemeral=True
            )
    
    @app_commands.command(
        name="debug-config",
        description="[DEBUG] Configuration du serveur actuel"
    )
    async def debug_config_command(self, interaction: discord.Interaction):
        """Afficher la configuration du serveur"""
        
        try:
            from services.guild_service import guild_service
            
            config = guild_service.get_guild_config(interaction.guild_id)
            
            embed = discord.Embed(
                title=f"🔧 Debug - Configuration {interaction.guild.name}",
                color=discord.Color.purple(),
                timestamp=datetime.utcnow()
            )
            
            # Configuration de base
            embed.add_field(
                name="⚙️ Base",
                value=f"Configuré: {config.get('configured', False)}\nLangue: {config.get('language', 'fr')}\nVersion: {config.get('version', 'N/A')}",
                inline=True
            )
            
            # Seuils
            thresholds = config.get('validation_thresholds', {})
            embed.add_field(
                name="📊 Seuils",
                value=f"Quorum: {thresholds.get('quorum_percentage', 'N/A')}%\nMin validateurs: {thresholds.get('min_validators', 'N/A')}\nTimeout: {thresholds.get('validation_timeout_hours', 'N/A')}h",
                inline=True
            )
            
            # Limites
            limits = config.get('rate_limits', {})
            embed.add_field(
                name="⏱️ Limites",
                value=f"Reports/user/h: {limits.get('reports_per_user_per_hour', 'N/A')}\nReports/guild/h: {limits.get('reports_per_guild_per_hour', 'N/A')}",
                inline=True
            )
            
            # IDs Discord
            embed.add_field(
                name="🆔 Discord IDs",
                value=f"Forum: {config.get('forum_channel_id', 'Non configuré')}\nRôle validateur: {config.get('validator_role_id', 'Non configuré')}\nLogs: {config.get('log_channel_id', 'Non configuré')}",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur dans /debug-config: {e}")
            await interaction.response.send_message(
                f"❌ Erreur: {str(e)}",
                ephemeral=True
            )


async def setup(bot):
    """Fonction appelée lors du chargement du cog"""
    # Toujours charger le cog, la vérification se fait par serveur dans cog_check
    await bot.add_cog(DebugCog(bot))
    logger.info("✅ Cog Debug chargé (activation par serveur via guild config)")