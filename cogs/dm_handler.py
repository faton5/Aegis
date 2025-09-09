"""
Cog pour gérer les messages privés et les transférer vers les threads de signalement
"""
import discord
from discord.ext import commands
import re

from config.logging_config import get_logger

logger = get_logger('dm_handler')


class DMHandlerCog(commands.Cog):
    """Gestionnaire de messages privés pour les signalements"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Écouter les messages privés pour les transférer vers les threads"""
        
        # Ignorer les messages du bot
        if message.author.bot:
            return
        
        # Seulement traiter les DM
        if not isinstance(message.channel, discord.DMChannel):
            return
        
        try:
            # Chercher si c'est une réponse à un signalement
            await self._handle_dm_response(message)
            
        except Exception as e:
            logger.error(f"Erreur traitement DM de {message.author}: {e}")
    
    async def _handle_dm_response(self, message: discord.Message):
        """Traiter une réponse par MP à un signalement"""
        
        # Vérifier si l'utilisateur a des signalements actifs
        if not hasattr(self.bot, 'report_service'):
            return
        
        # Chercher les signalements de cet utilisateur
        user_reports = []
        for report in self.bot.report_service.active_reports.values():
            if report.reporter_id == message.author.id:
                user_reports.append(report)
        
        if not user_reports:
            return
        
        # Si un seul signalement, l'utiliser
        if len(user_reports) == 1:
            target_report = user_reports[0]
        else:
            # Chercher si le message mentionne un ID de signalement
            report_id_pattern = r'#([A-Z0-9]{8})'
            matches = re.findall(report_id_pattern, message.content.upper())
            
            if matches:
                report_id = matches[0]
                target_report = next(
                    (r for r in user_reports if r.id == report_id), 
                    user_reports[0]  # Fallback au plus récent
                )
            else:
                # Prendre le plus récent
                target_report = max(user_reports, key=lambda r: r.created_at)
        
        # Transférer le message vers le thread
        await self._forward_to_thread(message, target_report)
    
    async def _forward_to_thread(self, message: discord.Message, report):
        """Transférer un MP vers le thread de signalement"""
        try:
            if not report.thread_id:
                return
            
            # Récupérer le thread
            thread = self.bot.get_channel(report.thread_id)
            if not thread:
                logger.warning(f"Thread {report.thread_id} non trouvé pour signalement {report.id}")
                return
            
            # Créer l'embed pour le message transféré (ANONYME)
            embed = discord.Embed(
                title="💬 Message du Rapporteur (Anonyme)",
                description=message.content if message.content else "*[Aucun texte]*",
                color=discord.Color.blue(),
                timestamp=message.created_at
            )
            
            # PAS de set_author pour préserver l'anonymat
            
            embed.set_footer(
                text=f"Signalement #{report.id} • Réponse anonyme via MP"
            )
            
            # Ajouter les pièces jointes s'il y en a
            files_to_send = []
            if message.attachments:
                attachment_text = "\n\n**📎 Pièces jointes:**\n"
                for attachment in message.attachments:
                    attachment_text += f"• [{attachment.filename}]({attachment.url})\n"
                    
                    # Si c'est une image, l'inclure dans l'embed
                    if attachment.content_type and attachment.content_type.startswith('image/'):
                        embed.set_image(url=attachment.url)
                
                embed.description += attachment_text
            
            # Envoyer dans le thread
            await thread.send(embed=embed)
            
            # Confirmer à l'utilisateur que son message a été transféré
            from locales.translation_manager import translator
            # Récupérer la guild depuis le thread pour les traductions
            guild_id = thread.guild.id if hasattr(thread, 'guild') else None
            
            confirmation_embed = discord.Embed(
                title=translator.t("dm_transferred_title", guild_id) if guild_id else "✅ Message Transféré",
                description=translator.t("dm_transferred_description", guild_id, report_id=report.id) if guild_id else f"Votre message a été ajouté au signalement **#{report.id}**.",
                color=discord.Color.green()
            )
            
            confirmation_embed.add_field(
                name="📋 Signalement",
                value=f"**#{report.id}** - {report.category}",
                inline=True
            )
            
            confirmation_embed.set_footer(
                text="Les modérateurs verront votre message (anonyme)"
            )
            
            await message.author.send(embed=confirmation_embed)
            
            logger.info(f"MP de {message.author} transféré vers thread {report.thread_id} (signalement {report.id})")
            
        except Exception as e:
            logger.error(f"Erreur transfert MP vers thread {report.thread_id}: {e}")
            
            # Essayer d'informer l'utilisateur
            try:
                await message.author.send(
                    "❌ Erreur lors du transfert de votre message. Contactez un administrateur."
                )
            except:
                pass


async def setup(bot):
    """Fonction appelée lors du chargement du cog"""
    await bot.add_cog(DMHandlerCog(bot))
