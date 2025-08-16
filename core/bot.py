"""
Classe principale du bot Aegis (version refactorisée)
"""
import discord
from discord.ext import commands
from typing import Optional, Dict, Any

from config.bot_config import bot_settings
from config.logging_config import get_logger
from services.report_service import ReportService
from utils.security import SecurityValidator
from utils.rate_limiter import RateLimiter
from locales.translation_manager import translator

logger = get_logger('bot')


class AegisBot(commands.Bot):
    """Bot Aegis principal - Version refactorisée"""
    
    def __init__(self):
        # Configuration des intents Discord
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        intents.members = True
        
        super().__init__(
            command_prefix='!aegis',  # Fallback, le bot utilise slash commands
            intents=intents,
            help_command=None  # Désactiver l'aide par défaut
        )
        
        # Services centralisés
        self.report_service: Optional[ReportService] = None
        self.security_validator: Optional[SecurityValidator] = None
        self.rate_limiter: Optional[RateLimiter] = None
        
        # État du bot
        self.is_ready = False
        self.startup_time = None
        
    async def setup(self):
        """Initialiser les services et charger les cogs"""
        try:
<<<<<<< HEAD
            # Services init silencieux sauf erreurs
=======
            logger.info("🔧 Initialisation des services...")
>>>>>>> a512c3414221258fe8b4b13148490d4f0b66e5d7
            
            # Initialiser les services
            self.security_validator = SecurityValidator()
            self.rate_limiter = RateLimiter(
                max_actions=bot_settings.max_reports_per_hour,
                time_window=3600  # 1 heure
            )
            
            # Intégrer Supabase si activé
            db_client = None
            if bot_settings.supabase_enabled:
                try:
                    from database.supabase_client import supabase_client
                    connection_success = await supabase_client.connect()
                    if connection_success:
                        db_client = supabase_client
<<<<<<< HEAD
                        # Supabase connecté silencieusement
=======
                        logger.info("✅ Supabase intégré au ReportService")
>>>>>>> a512c3414221258fe8b4b13148490d4f0b66e5d7
                    else:
                        logger.warning("⚠️ Supabase activé mais connexion échouée")
                except Exception as e:
                    logger.error(f"❌ Erreur intégration Supabase: {e}")
            
            # Service de signalements
            self.report_service = ReportService(
                db_client=db_client,
                validator=self.security_validator,
                rate_limiter=self.rate_limiter
            )
            
            # Service de configuration des guildes
            from services.guild_service import guild_service
            self.guild_service = guild_service
            
<<<<<<< HEAD
            # Services initialisés silencieusement
=======
            logger.info("✅ Services initialisés")
>>>>>>> a512c3414221258fe8b4b13148490d4f0b66e5d7
            
            # Charger les cogs (extensions)
            await self._load_cogs()
            
<<<<<<< HEAD
            # Extensions chargées silencieusement
=======
            logger.info("🔌 Extensions chargées")
>>>>>>> a512c3414221258fe8b4b13148490d4f0b66e5d7
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation: {e}")
            raise
    
    async def _load_cogs(self):
        """Charger les cogs (extensions) du bot"""
        cogs_to_load = [
            'cogs.reports',    # Commandes de signalement
            'cogs.admin',      # Commandes admin
            'cogs.setup',      # Configuration serveurs
            'cogs.dm_handler', # Gestionnaire de MP
            'cogs.config',     # Configuration avancée
        ]
        
        if bot_settings.debug_enabled:
            cogs_to_load.append('cogs.debug')
        
        for cog_name in cogs_to_load:
            try:
                await self.load_extension(cog_name)
                logger.debug(f"✅ Cog chargé: {cog_name}")
            except Exception as e:
                logger.error(f"❌ Erreur chargement cog {cog_name}: {e}")
    
    async def on_ready(self):
        """Événement: Bot prêt"""
        from datetime import datetime
        
        self.startup_time = datetime.utcnow()
        self.is_ready = True
        
<<<<<<< HEAD
        # Variables pour le message final
        guild_count = len(self.guilds)
=======
        logger.info("=" * 50)
        logger.info(f"🤖 {self.user} est connecté et prêt !")
        logger.info(f"📊 Serveurs connectés: {len(self.guilds)}")
        
        for guild in self.guilds:
            logger.info(f"   - {guild.name} (ID: {guild.id}, Membres: {guild.member_count})")
        
        logger.info(f"🌐 Langues disponibles: {list(translator.get_available_languages().keys())}")
        logger.info("=" * 50)
>>>>>>> a512c3414221258fe8b4b13148490d4f0b66e5d7
        
        # Synchroniser les commandes slash
        try:
            synced = await self.tree.sync()
<<<<<<< HEAD
            synced_count = len(synced)
        except Exception as e:
            logger.error(f"❌ Erreur synchronisation commandes: {e}")
            synced_count = 0
        
        # Message final simple et propre
        print(f"✅ {self.user} connecté - {guild_count} serveur(s) - {synced_count} commandes")
=======
            logger.info(f"⚡ {len(synced)} commandes slash synchronisées")
        except Exception as e:
            logger.error(f"❌ Erreur synchronisation commandes: {e}")
>>>>>>> a512c3414221258fe8b4b13148490d4f0b66e5d7
    
    async def on_guild_join(self, guild: discord.Guild):
        """Événement: Bot rejoint un serveur"""
        logger.info(f"➕ Nouveau serveur rejoint: {guild.name} (ID: {guild.id})")
        
        # TODO: Créer configuration par défaut pour la guilde
        # from guild_config import guild_config
        # guild_config.get_guild_config(guild.id)
    
    async def on_guild_remove(self, guild: discord.Guild):
        """Événement: Bot quitte un serveur"""
        logger.info(f"➖ Serveur quitté: {guild.name} (ID: {guild.id})")
    
    async def on_app_command_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        """Gestionnaire d'erreurs pour les commandes slash"""
        logger.error(f"❌ Erreur commande slash: {error}")
        
        try:
            if interaction.response.is_done():
                await interaction.followup.send(
                    "❌ Une erreur inattendue s'est produite.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Une erreur inattendue s'est produite.",
                    ephemeral=True
                )
        except:
            pass  # Éviter les erreurs en cascade
    
    async def on_error(self, event_method: str, *args, **kwargs):
        """Gestionnaire d'erreurs général"""
        logger.error(f"❌ Erreur dans {event_method}", exc_info=True)
    
    async def close(self):
        """Fermeture propre du bot"""
        logger.info("🔌 Fermeture du bot...")
        
        # Nettoyer les ressources si nécessaire
        if self.report_service:
            await self.report_service.cleanup_old_reports()
        
        await super().close()
        logger.info("✅ Bot fermé proprement")
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtenir les statistiques du bot"""
        stats = {
            'guilds': len(self.guilds),
            'users': sum(guild.member_count or 0 for guild in self.guilds),
            'startup_time': self.startup_time.isoformat() if self.startup_time else None,
            'is_ready': self.is_ready
        }
        
        # Ajouter stats des services
        if self.rate_limiter:
            stats['rate_limiter'] = self.rate_limiter.get_stats()
            
        if self.report_service:
            stats['active_reports'] = len(self.report_service.active_reports)
        
        return stats