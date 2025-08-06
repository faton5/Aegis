"""
Cog pour les commandes d'administration
"""
import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime, timedelta, timezone
from typing import Optional

from config.logging_config import get_logger
from config.bot_config import bot_settings, ERROR_MESSAGES
from locales.translation_manager import translator

logger = get_logger('admin')


class AdminCog(commands.Cog):
    """Commandes d'administration du bot"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(
        name="stats",
        description="Afficher les statistiques du bot Aegis"
    )
    async def stats_command(self, interaction: discord.Interaction, period: Optional[int] = 7):
        """Affiche les statistiques d'utilisation du bot"""
        
        # Déférer immédiatement pour éviter le timeout
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Vérifier les permissions
            if not self._check_admin_permissions(interaction):
                await interaction.followup.send(
                    translator.t("error_missing_permissions", interaction.guild_id),
                    ephemeral=True
                )
                return
            
            # Obtenir le forum d'alertes
            alerts_forum = discord.utils.get(
                interaction.guild.channels, 
                name=bot_settings.alerts_channel_name
            )
            
            if not alerts_forum:
                await interaction.followup.send(
                    "❌ Forum d'alertes non trouvé. Utilisez /setup pour configurer le bot.",
                    ephemeral=True
                )
                return
            
            # Calculer les statistiques
            stats = await self._calculate_stats(alerts_forum, period or 7)
            
            # Créer l'embed
            embed = discord.Embed(
                title="📊 Statistiques Aegis",
                description=f"Rapport d'activité des {period or 7} derniers jours",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📈 Signalements totaux", 
                value=str(stats['total']), 
                inline=True
            )
            embed.add_field(
                name="✅ Validés", 
                value=str(stats['validated']), 
                inline=True
            )
            embed.add_field(
                name="⏳ En attente", 
                value=str(stats['pending']), 
                inline=True
            )
            
            # Statistiques du bot si disponibles
            if hasattr(self.bot, 'report_service'):
                active_reports = len(self.bot.report_service.active_reports)
                embed.add_field(
                    name="🔄 Signalements actifs",
                    value=str(active_reports),
                    inline=True
                )
            
            # Statistiques du rate limiter
            if hasattr(self.bot, 'rate_limiter'):
                limiter_stats = self.bot.rate_limiter.get_stats()
                embed.add_field(
                    name="👥 Utilisateurs surveillés",
                    value=str(limiter_stats['active_users']),
                    inline=True
                )
            
            embed.set_footer(text=f"Serveur: {interaction.guild.name}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur dans /stats: {e}")
            await interaction.followup.send(
                "❌ Erreur lors du calcul des statistiques.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="check",
        description="Vérifier un utilisateur dans la base de données"
    )
    async def check_command(self, interaction: discord.Interaction, user: discord.User):
        """Vérifier un utilisateur dans la base de données centralisée"""
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Vérifier les permissions
            if not self._check_admin_permissions(interaction):
                await interaction.followup.send(
                    translator.t("error_missing_permissions", interaction.guild_id),
                    ephemeral=True
                )
                return
            
            # Vérifier si Supabase est activé
            if not bot_settings.supabase_enabled:
                await interaction.followup.send(
                    "❌ Base de données centralisée désactivée.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=translator.t("check_title", interaction.guild_id),
                description=translator.t("check_description", interaction.guild_id, user_mention=user.mention, user_id=user.id),
                color=discord.Color.orange()
            )
            
            # TODO: Intégrer avec Supabase quand migré
            embed.add_field(
                name="👤 Utilisateur",
                value=f"{user.display_name}\n`{user.id}`",
                inline=True
            )
            
            embed.add_field(
                name="📅 Compte créé",
                value=discord.utils.format_dt(user.created_at, 'R'),
                inline=True
            )
            
            # Vérifier d'abord dans Supabase (base globale)
            supabase_flag = None
            if hasattr(self.bot.report_service, 'db') and self.bot.report_service.db:
                try:
                    supabase_flag = await self.bot.report_service.db.check_user_flag(
                        user.id, 
                        interaction.guild_id,
                        interaction.guild.name
                    )
                except Exception as e:
                    logger.warning(f"Erreur vérification Supabase: {e}")
            
            # Chercher les signalements locaux concernant cet utilisateur
            user_reports = []
            if hasattr(self.bot, 'report_service'):
                for report in self.bot.report_service.active_reports.values():
                    if report.target_username.lower() == user.name.lower() or report.target_username.lower() == user.display_name.lower():
                        user_reports.append(report)
            
            if user_reports:
                # Trier par date (plus récent en premier)
                user_reports.sort(key=lambda r: r.created_at, reverse=True)
                
                # Statistiques
                validated_count = len([r for r in user_reports if r.status == "validated"])
                pending_count = len([r for r in user_reports if r.status == "pending"])
                rejected_count = len([r for r in user_reports if r.status == "rejected"])
                
                embed.add_field(
                    name="🚨 Signalements",
                    value=f"**Total:** {len(user_reports)}\n**Validés:** {validated_count}\n**En attente:** {pending_count}\n**Rejetés:** {rejected_count}",
                    inline=True
                )
                
                # Détails des signalements récents (max 3)
                recent_reports = user_reports[:3]
                reports_text = ""
                for report in recent_reports:
                    status_emoji = {
                        "validated": "✅",
                        "pending": "🔄", 
                        "rejected": "❌"
                    }.get(report.status, "❓")
                    
                    reports_text += f"{status_emoji} **{report.id}** - {report.category}\n"
                    reports_text += f"   *{report.reason[:50]}{'...' if len(report.reason) > 50 else ''}*\n"
                
                embed.add_field(
                    name="📋 Signalements Récents",
                    value=reports_text if reports_text else "Aucun",
                    inline=False
                )
                
                # Niveau de risque basé sur les signalements validés
                if validated_count >= 3:
                    risk_level = "🔴 **CRITIQUE**"
                    embed.color = discord.Color.red()
                elif validated_count >= 2:
                    risk_level = "🟠 **ÉLEVÉ**"
                    embed.color = discord.Color.orange()
                elif validated_count >= 1:
                    risk_level = "🟡 **MOYEN**"
                    embed.color = discord.Color.gold()
                else:
                    risk_level = "🟢 **FAIBLE**"
                    embed.color = discord.Color.green()
                
                embed.add_field(
                    name="⚠️ Niveau de Risque",
                    value=risk_level,
                    inline=True
                )
                
            else:
                embed.add_field(
                    name=translator.t("check_local_reports", interaction.guild_id),
                    value=translator.t("check_no_local_reports", interaction.guild_id),
                    inline=True
                )
            
            # Afficher les informations de la base globale Supabase
            if supabase_flag:
                embed.add_field(
                    name=translator.t("check_global_database", interaction.guild_id),
                    value=f"🚨 **UTILISATEUR FLAGGÉ**\n**Niveau:** {supabase_flag.get('flag_level', 'Inconnu')}\n**Catégorie:** {supabase_flag.get('flag_category', 'N/A')}\n**Raison:** {supabase_flag.get('flag_reason', 'N/A')[:50]}",
                    inline=False
                )
                embed.color = discord.Color.red()
            elif hasattr(self.bot.report_service, 'db') and self.bot.report_service.db and self.bot.report_service.db.is_connected:
                embed.add_field(
                    name=translator.t("check_global_database", interaction.guild_id),
                    value=translator.t("check_not_flagged_globally", interaction.guild_id),
                    inline=True
                )
                if not user_reports:  # Seulement vert si pas de signalements locaux non plus
                    embed.color = discord.Color.green()
            else:
                embed.add_field(
                    name=translator.t("check_global_database", interaction.guild_id),
                    value=translator.t("check_database_unavailable", interaction.guild_id),
                    inline=True
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur dans /check: {e}")
            await interaction.followup.send(
                "❌ Erreur lors de la vérification.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="validate",
        description="Valider les signalements en attente"
    )
    async def validate_command(self, interaction: discord.Interaction):
        """Interface pour valider les signalements en attente"""
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Vérifier les permissions
            if not self._check_validator_permissions(interaction):
                await interaction.followup.send(
                    translator.t("error_missing_permissions", interaction.guild_id),
                    ephemeral=True
                )
                return
            
            # Obtenir les signalements en attente
            if hasattr(self.bot, 'report_service'):
                pending_reports = await self.bot.report_service.get_guild_reports(
                    interaction.guild_id, 
                    status="pending"
                )
                
                if not pending_reports:
                    await interaction.followup.send(
                        "✅ Aucun signalement en attente de validation.",
                        ephemeral=True
                    )
                    return
                
                embed = discord.Embed(
                    title="🔍 Signalements en attente",
                    description=f"{len(pending_reports)} signalement(s) à valider",
                    color=discord.Color.orange()
                )
                
                for i, report in enumerate(pending_reports[:5], 1):  # Limiter à 5
                    embed.add_field(
                        name=f"#{i} - {report.id}",
                        value=f"**Cible**: {report.target_username}\n**Catégorie**: {report.category}\n**Âge**: {report.age_hours:.1f}h",
                        inline=True
                    )
                
                if len(pending_reports) > 5:
                    embed.set_footer(text=f"... et {len(pending_reports) - 5} autre(s)")
                
                # TODO: Ajouter vue de validation
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    "❌ Service de signalements non disponible.",
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Erreur dans /validate: {e}")
            await interaction.followup.send(
                "❌ Erreur lors de la récupération des signalements.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="purge",
        description="Nettoyer les anciens signalements"
    )
    async def purge_command(self, interaction: discord.Interaction, days: Optional[int] = 30):
        """Nettoyer les anciens signalements du forum"""
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Vérifier les permissions admin
            if not interaction.user.guild_permissions.administrator:
                await interaction.followup.send(
                    translator.t("error_missing_permissions", interaction.guild_id),
                    ephemeral=True
                )
                return
            
            # Obtenir le forum d'alertes
            alerts_forum = discord.utils.get(
                interaction.guild.channels, 
                name=bot_settings.alerts_channel_name
            )
            
            if not alerts_forum:
                await interaction.followup.send(
                    "❌ Forum d'alertes non trouvé.",
                    ephemeral=True
                )
                return
            
            # Calculer la date de coupure
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days or 30)
            
            deleted_count = 0
            
            # Nettoyer les threads archivés anciens
            async for thread in alerts_forum.archived_threads(limit=200):
                if thread.created_at and thread.created_at < cutoff_date:
                    try:
                        await thread.delete()
                        deleted_count += 1
                    except:
                        pass  # Ignorer les erreurs de suppression
            
            # Nettoyer le service si disponible
            if hasattr(self.bot, 'report_service'):
                await self.bot.report_service.cleanup_old_reports(days or 30)
            
            embed = discord.Embed(
                title="🧹 Nettoyage Terminé",
                description=f"Nettoyage des signalements de plus de {days or 30} jours",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📊 Résultats",
                value=f"**Threads supprimés**: {deleted_count}\n**Critère**: Plus de {days or 30} jours",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur dans /purge: {e}")
            await interaction.followup.send(
                "❌ Erreur lors du nettoyage.",
                ephemeral=True
            )
    
    def _check_admin_permissions(self, interaction: discord.Interaction) -> bool:
        """Vérifier si l'utilisateur a les permissions admin"""
        # Admin serveur
        if interaction.user.guild_permissions.administrator:
            return True
        
        # Rôle validateur
        validator_role = discord.utils.get(
            interaction.guild.roles, 
            name=bot_settings.validator_role_name
        )
        if validator_role and validator_role in interaction.user.roles:
            return True
        
        return False
    
    def _check_validator_permissions(self, interaction: discord.Interaction) -> bool:
        """Vérifier si l'utilisateur peut valider des signalements"""
        return self._check_admin_permissions(interaction)
    
    async def _calculate_stats(self, alerts_forum, period_days: int) -> dict:
        """Calculer les statistiques du forum"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=period_days)
        
        total_reports = 0
        validated_reports = 0
        
        try:
            # Analyser les threads archivés
            async for thread in alerts_forum.archived_threads(limit=100):
                if thread.created_at and thread.created_at >= cutoff_date:
                    total_reports += 1
                    
                    # Vérifier si validé (recherche simple)
                    async for message in thread.history(limit=20):
                        if "validé" in message.content.lower() or "✅" in message.content:
                            validated_reports += 1
                            break
            
            # Analyser les threads actifs
            for thread in alerts_forum.threads:
                if thread.created_at and thread.created_at >= cutoff_date:
                    total_reports += 1
                    
                    async for message in thread.history(limit=20):
                        if "validé" in message.content.lower() or "✅" in message.content:
                            validated_reports += 1
                            break
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
        
        return {
            'total': total_reports,
            'validated': validated_reports,
            'pending': total_reports - validated_reports
        }


async def setup(bot):
    """Fonction appelée lors du chargement du cog"""
    await bot.add_cog(AdminCog(bot))
    logger.info("✅ Cog Admin chargé")