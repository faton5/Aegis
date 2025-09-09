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
            
            # Obtenir le forum d'alertes
            alerts_forum = discord.utils.get(
                interaction.guild.channels, 
                name=bot_settings.alerts_channel_name
            )
            
            if not alerts_forum:
                logger.warning("Forum d'alertes non trouvé; stats forum indisponibles.")
                stats = {'total': 0, 'validated': 0, 'pending': 0}
            else:
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
            
            # Statistiques Supabase (si disponibles)
            try:
                db_client = getattr(getattr(self.bot, 'report_service', None), 'db', None)
                if bot_settings.supabase_enabled and db_client and hasattr(db_client, 'get_guild_stats'):
                    supa = await db_client.get_guild_stats(interaction.guild_id, period or 7)
                    if supa:
                        embed.add_field(name="Vérifications", value=str(supa.get('total_checks', 0)), inline=True)
                        embed.add_field(name="Utilisateurs flaggés actifs", value=str(supa.get('active_flagged_users', 0)), inline=True)
                        embed.add_field(name="Flags créés (serveur)", value=str(supa.get('flags_created_by_guild', 0)), inline=True)
                        lb = supa.get('level_breakdown') or {}
                        if isinstance(lb, dict) and lb:
                            parts = [f"{k}: {v}" for k, v in lb.items()]
                            embed.add_field(name="Niveaux", value=", ".join(parts)[:1024] or "N/A", inline=False)
            except Exception as e:
                logger.warning(f"Impossible de récupérer les stats Supabase: {e}")
            
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
                translator.t("admin_stats_error", interaction.guild_id),
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
            
            # Vérifier si Supabase est activé
            if not bot_settings.supabase_enabled:
                await interaction.followup.send(
                    translator.t("admin_database_disabled", interaction.guild_id),
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
                    supabase_flag = await self.bot.report_service.db.check_user(
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
                    # Priorité à l'ID utilisateur, puis au nom
                    if (report.target_user_id and report.target_user_id == user.id) or \
                       (report.target_username.lower() == user.name.lower() or 
                        report.target_username.lower() == user.display_name.lower()):
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
                # Nouveau format avec niveaux et historique
                active_flags = supabase_flag.get('active_flags', 0)
                total_flags = supabase_flag.get('total_flags', 0)
                current_level = supabase_flag.get('current_level', 'unknown').upper()
                
                # Extraire la dernière raison de l'historique JSON
                flag_history = supabase_flag.get('flag_history', [])
                last_reason = "N/A"
                last_category = "N/A"
                
                if flag_history and len(flag_history) > 0:
                    # Trouver le dernier flag actif (non expiré)
                    for flag_item in reversed(flag_history):
                        if not flag_item.get('expired', False):
                            last_reason = flag_item.get('reason', 'N/A')[:50]
                            last_category = flag_item.get('category', 'N/A')
                            break
                
                embed.add_field(
                    name=translator.t("check_global_database", interaction.guild_id),
                    value=f"🚨 **UTILISATEUR FLAGGÉ**\n"
                          f"**Niveau:** {current_level}\n"
                          f"**Flags actifs/total:** {active_flags}/{total_flags}\n"
                          f"**Catégorie:** {last_category}\n"
                          f"**Dernière raison:** {last_reason}",
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
                translator.t("admin_verification_error", interaction.guild_id),
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
                    translator.t("validate_service_unavailable", interaction.guild_id),
                    ephemeral=True
                )
                
        except Exception as e:
            logger.error(f"Erreur dans /validate: {e}")
            await interaction.followup.send(
                translator.t("admin_reports_retrieval_error", interaction.guild_id),
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
            active_deleted = 0
            archived_deleted = 0
            
            # Nettoyer les threads ACTIFS anciens d'abord
            if hasattr(alerts_forum, 'threads'):
                for thread in alerts_forum.threads:
                    if thread.created_at and thread.created_at < cutoff_date:
                        try:
                            await thread.delete()
                            active_deleted += 1
                            deleted_count += 1
                        except Exception as e:
                            logger.debug(f"Erreur suppression thread actif {thread.id}: {e}")
            
            # Nettoyer les threads archivés anciens
            async for thread in alerts_forum.archived_threads(limit=200):
                if thread.created_at and thread.created_at < cutoff_date:
                    try:
                        await thread.delete()
                        archived_deleted += 1
                        deleted_count += 1
                    except Exception as e:
                        logger.debug(f"Erreur suppression thread archivé {thread.id}: {e}")
            
            # Nettoyer le service si disponible
            if hasattr(self.bot, 'report_service'):
                await self.bot.report_service.cleanup_old_reports(days or 30)
            
            embed = discord.Embed(
                title=translator.t("purge_cleanup_completed", interaction.guild_id),
                description=translator.t("purge_cleanup_description", interaction.guild_id, days=days or 30),
                color=discord.Color.green()
            )
            
            embed.add_field(
                name=translator.t("purge_results_field", interaction.guild_id),
                value=translator.t("purge_results_value", interaction.guild_id, 
                                 deleted_count=deleted_count, 
                                 active_count=active_deleted,
                                 archived_count=archived_deleted, 
                                 days=days or 30),
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur dans /purge: {e}")
            await interaction.followup.send(
                translator.t("purge_error", interaction.guild_id),
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
    
    @app_commands.command(
        name="debug-mode",
        description="Activer/désactiver les commandes debug pour ce serveur"
    )
    async def debug_mode_command(self, interaction: discord.Interaction, enabled: bool):
        """Activer ou désactiver le mode debug pour le serveur"""
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Vérifier les permissions administrateur
            if not interaction.user.guild_permissions.administrator:
                await interaction.followup.send(
                    translator.t("error_missing_permissions", interaction.guild_id),
                    ephemeral=True
                )
                return
            
            # Mettre à jour la configuration du serveur
            from services.guild_service import guild_service
            
            guild_config = guild_service.get_guild_config(interaction.guild_id)
            old_status = guild_config.get('debug_enabled', False)
            
            guild_service.update_guild_config(interaction.guild_id, {
                'debug_enabled': enabled
            })
            
            # Créer l'embed de confirmation
            status_emoji = "✅" if enabled else "❌"
            status_text = "activé" if enabled else "désactivé"
            color = discord.Color.green() if enabled else discord.Color.red()
            
            embed = discord.Embed(
                title=f"{status_emoji} Mode Debug {status_text.title()}",
                description=f"Le mode debug a été **{status_text}** pour ce serveur.",
                color=color,
                timestamp=datetime.utcnow()
            )
            
            # Ajouter des informations sur les commandes
            if enabled:
                embed.add_field(
                    name="🔧 Commandes debug disponibles",
                    value="• `/debug-info` - Informations système\n"
                          "• `/debug-services` - État des services\n"
                          "• `/debug-config` - Configuration serveur\n"
                          "• `/debug-translations <clé>` - Test traductions",
                    inline=False
                )
                embed.add_field(
                    name="⚠️ Attention",
                    value="Les commandes debug peuvent révéler des informations sensibles.\n"
                          "Réservez l'accès aux administrateurs de confiance uniquement.",
                    inline=False
                )
            else:
                embed.add_field(
                    name="ℹ️ Informations",
                    value="Les commandes debug ne sont plus accessibles sur ce serveur.\n"
                          "Les administrateurs peuvent les réactiver avec cette commande.",
                    inline=False
                )
            
            # Historique du changement
            if old_status != enabled:
                embed.add_field(
                    name="📝 Changement",
                    value=f"**Avant:** {'Activé' if old_status else 'Désactivé'}\n"
                          f"**Maintenant:** {'Activé' if enabled else 'Désactivé'}\n"
                          f"**Par:** {interaction.user.mention}",
                    inline=True
                )
            else:
                embed.add_field(
                    name="📝 Statut",
                    value=f"Aucun changement (déjà {status_text})",
                    inline=True
                )
            
            embed.set_footer(text=f"Serveur: {interaction.guild.name}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Log le changement
            logger.info(f"Mode debug {'activé' if enabled else 'désactivé'} pour guild {interaction.guild_id} par {interaction.user}")
            
        except Exception as e:
            logger.error(f"Erreur dans /debug-mode: {e}")
            await interaction.followup.send(
                f"❌ Erreur lors du changement de mode debug: {str(e)}",
                ephemeral=True
            )


async def setup(bot):
    """Fonction appelée lors du chargement du cog"""
    await bot.add_cog(AdminCog(bot))
