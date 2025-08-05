import discord
from discord import app_commands
from datetime import datetime, timedelta
from config import BOT_CONFIG, REPORT_CATEGORIES, ERROR_MESSAGES
from utils import create_secure_embed, SecurityValidator, AuditLogger, logger
from typing import Optional
# Anciens décorateurs supprimés - réponse directe maintenant

# Commandes supplémentaires pour le bot Agis

@app_commands.command(name="stats", description="Afficher les statistiques du bot Agis")
async def show_stats(interaction: discord.Interaction):
    """Affiche les statistiques d'utilisation du bot"""
    
    # DEFER IMMÉDIATEMENT pour éviter le timeout
    await interaction.response.defer(ephemeral=True)
    
    # Vérifier les permissions
    validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
    if not (validator_role and validator_role in interaction.user.roles) and not interaction.user.guild_permissions.administrator:
        await interaction.followup.send(
            ERROR_MESSAGES["no_permission"], ephemeral=True
        )
        return
    
    period = 7  # Par défaut 7 jours
    
    # Compter les threads dans le forum d'alertes
    alerts_forum = discord.utils.get(interaction.guild.channels, name=BOT_CONFIG["ALERTS_CHANNEL_NAME"])
    
    if not alerts_forum:
        await interaction.followup.send(
            ERROR_MESSAGES["forum_not_found"], ephemeral=True
        )
        return
    
    # Calculer la date limite (timezone-aware)
    from datetime import timezone
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=period)
    
    total_reports = 0
    validated_reports = 0
    
    # Analyser les threads récents
    try:
        async for thread in alerts_forum.archived_threads(limit=100):
            if thread.created_at and thread.created_at >= cutoff_date:
                total_reports += 1
                
                # Vérifier si validé (simplifié)
                async for message in thread.history(limit=20):
                    if "validé par la communauté" in message.content.lower():
                        validated_reports += 1
                        break
        
        # Compter aussi les threads actifs
        for thread in alerts_forum.threads:
            if thread.created_at and thread.created_at >= cutoff_date:
                total_reports += 1
                
                async for message in thread.history(limit=20):
                    if "validé par la communauté" in message.content.lower():
                        validated_reports += 1
                        break
                        
    except Exception as e:
        logger.error(f"Erreur lors du calcul des statistiques: {e}")
    
    pending_reports = total_reports - validated_reports
    
    embed = create_secure_embed(
        "📊 Statistiques Agis",
        f"Rapport d'activité des {period} derniers jours",
        discord.Color.blue()
    )
    
    embed.add_field(name="📈 Signalements totaux", value=str(total_reports), inline=True)
    embed.add_field(name="✅ Validés", value=str(validated_reports), inline=True)
    embed.add_field(name="⏳ En attente", value=str(pending_reports), inline=True)
    
    if total_reports > 0:
        validation_rate = (validated_reports / total_reports) * 100
        embed.add_field(name="📊 Taux de validation", value=f"{validation_rate:.1f}%", inline=True)
    
    embed.add_field(
        name="👥 Validateurs actifs", 
        value=str(len([m for m in interaction.guild.members if validator_role in m.roles])), 
        inline=True
    )
    
    embed.set_footer(text=f"Période: {period} jours • Généré le")
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@app_commands.command(name="export", description="Exporter les signalements validés (Admins uniquement)")
async def export_reports(interaction: discord.Interaction):
    """Exporte les signalements validés pour analyse"""
    
    # DEFER IMMÉDIATEMENT pour éviter le timeout
    await interaction.response.defer(ephemeral=True)
    
    # Vérifier les permissions administrateur
    if not interaction.user.guild_permissions.administrator:
        await interaction.followup.send(
            ERROR_MESSAGES["no_permission"], ephemeral=True
        )
        audit_logger = AuditLogger()
        audit_logger.log_security_event(
            "UNAUTHORIZED_EXPORT", 
            f"User {interaction.user.id} attempted export without admin rights",
            interaction.user.id
        )
        return
    
    format = "json"  # Par défaut JSON
    
    # Collecter les données des signalements validés
    alerts_forum = discord.utils.get(interaction.guild.channels, name=BOT_CONFIG["ALERTS_CHANNEL_NAME"])
    
    if not alerts_forum:
        await interaction.followup.send(
            ERROR_MESSAGES["forum_not_found"], ephemeral=True
        )
        return
    
    export_data = []
    
    try:
        # Analyser tous les threads archivés
        async for thread in alerts_forum.archived_threads(limit=500):
            thread_data = await extract_thread_data(thread)
            if thread_data and thread_data["validated"]:
                export_data.append(thread_data)
        
        # Analyser les threads actifs
        for thread in alerts_forum.threads:
            thread_data = await extract_thread_data(thread)
            if thread_data and thread_data["validated"]:
                export_data.append(thread_data)
        
        if not export_data:
            await interaction.followup.send(
                "📭 Aucun signalement validé trouvé à exporter.", ephemeral=True
            )
            return
        
        # Créer le fichier d'export (simplifié pour démo)
        import json
        export_content = json.dumps(export_data, indent=2, default=str, ensure_ascii=False)
        
        # Créer l'embed de confirmation
        embed = create_secure_embed(
            "📤 Export généré",
            f"Export de {len(export_data)} signalements validés",
            discord.Color.green()
        )
        
        embed.add_field(name="📄 Format", value=format.upper(), inline=True)
        embed.add_field(name="📊 Nombre", value=str(len(export_data)), inline=True)
        embed.add_field(name="📅 Date", value=datetime.now().strftime("%d/%m/%Y %H:%M"), inline=True)
        
        # Note: Dans un vrai bot, on sauvegarderait le fichier et l'enverrait
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export: {e}")
        await interaction.followup.send(
            "❌ Erreur lors de la génération de l'export.", ephemeral=True
        )

async def extract_thread_data(thread):
    """Extrait les données d'un thread de signalement"""
    try:
        report_data = {
            "thread_id": thread.id,
            "thread_name": thread.name,
            "created_at": thread.created_at,
            "validated": False,
            "report_id": None,
            "target_user": None,
            "category": None,
            "reason": None
        }
        
        # Analyser les messages du thread
        async for message in thread.history(limit=20):
            # Vérifier si le signalement est validé
            if "validé par la communauté" in message.content.lower():
                report_data["validated"] = True
            
            # Extraire les données des embeds
            for embed in message.embeds:
                if embed.title and "signalement agis" in embed.title.lower():
                    for field in embed.fields:
                        if "id signalement" in field.name.lower():
                            report_data["report_id"] = field.value.strip("`")
                        elif "utilisateur signalé" in field.name.lower():
                            report_data["target_user"] = field.value
                        elif "catégorie" in field.name.lower():
                            report_data["category"] = field.value
                        elif "motif" in field.name.lower():
                            report_data["reason"] = field.value
        
        return report_data
    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des données du thread {thread.id}: {e}")
        return None

class PurgeConfirmationView(discord.ui.View):
    """Vue de confirmation pour la purge avec validation par quorum"""
    
    def __init__(self, guild_id: int, initiator_id: int, forum_channel):
        super().__init__(timeout=600)  # 10 minutes
        self.guild_id = guild_id
        self.initiator_id = initiator_id
        self.forum_channel = forum_channel
        self.validators = set()  # Validateurs qui approuvent
        self.rejectors = set()   # Validateurs qui rejettent
        self.is_finalized = False
        
    @discord.ui.button(label="✅ Approuver la purge", style=discord.ButtonStyle.danger, custom_id="approve_purge")
    async def approve_purge(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.InteractionResponded:
            pass
        except Exception:
            return
            
        if self.is_finalized:
            await interaction.followup.send("ℹ️ Cette demande de purge a déjà été traitée.", ephemeral=True)
            return
            
        validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
        
        if validator_role and validator_role in interaction.user.roles:
            if interaction.user.id in self.validators:
                await interaction.followup.send("⚠️ Vous avez déjà approuvé cette purge.", ephemeral=True)
                return
                
            self.rejectors.discard(interaction.user.id)
            self.validators.add(interaction.user.id)
            
            # Calculer le pourcentage d'approbation
            total_validators = len([member for member in interaction.guild.members if validator_role in member.roles])
            approval_percentage = (len(self.validators) / total_validators) * 100 if total_validators > 0 else 0
            
            embed = create_secure_embed(
                "✅ Purge approuvée",
                f"Approuvée par {interaction.user.display_name}",
                discord.Color.green()
            )
            embed.add_field(
                name="Progression", 
                value=f"{approval_percentage:.1f}% ({len(self.validators)}/{total_validators})", 
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Si le quorum est atteint, exécuter la purge
            if approval_percentage >= BOT_CONFIG["QUORUM_PERCENTAGE"]:
                await self.execute_purge(interaction)
        else:
            await interaction.followup.send(
                f"❌ Vous devez avoir le rôle '{BOT_CONFIG['VALIDATOR_ROLE_NAME']}' pour approuver la purge.",
                ephemeral=True
            )
    
    @discord.ui.button(label="❌ Rejeter la purge", style=discord.ButtonStyle.secondary, custom_id="reject_purge")
    async def reject_purge(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer(ephemeral=True)
        except discord.InteractionResponded:
            pass
        except Exception:
            return
            
        if self.is_finalized:
            await interaction.followup.send("ℹ️ Cette demande de purge a déjà été traitée.", ephemeral=True)
            return
            
        validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
        
        if validator_role and validator_role in interaction.user.roles:
            if interaction.user.id in self.rejectors:
                await interaction.followup.send("⚠️ Vous avez déjà rejeté cette purge.", ephemeral=True)
                return
                
            self.validators.discard(interaction.user.id)
            self.rejectors.add(interaction.user.id)
            
            # Calculer le pourcentage de rejet
            total_validators = len([member for member in interaction.guild.members if validator_role in member.roles])
            rejection_percentage = (len(self.rejectors) / total_validators) * 100 if total_validators > 0 else 0
            
            embed = create_secure_embed(
                "❌ Purge rejetée",
                f"Rejetée par {interaction.user.display_name}",
                discord.Color.red()
            )
            embed.add_field(
                name="Progression rejet", 
                value=f"{rejection_percentage:.1f}% ({len(self.rejectors)}/{total_validators})", 
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
            # Si le quorum de rejet est atteint
            if rejection_percentage >= BOT_CONFIG["QUORUM_PERCENTAGE"]:
                await self.finalize_rejection(interaction)
        else:
            await interaction.followup.send(
                f"❌ Vous devez avoir le rôle '{BOT_CONFIG['VALIDATOR_ROLE_NAME']}' pour rejeter la purge.",
                ephemeral=True
            )
    
    async def execute_purge(self, interaction: discord.Interaction):
        """Exécute la purge après validation du quorum"""
        self.is_finalized = True
        
        # Désactiver les boutons
        for item in self.children:
            item.disabled = True
        
        # Commencer la purge
        embed = create_secure_embed(
            "🧹 Purge en cours...",
            "Suppression de tous les signalements du forum. Veuillez patienter...",
            discord.Color.orange()
        )
        
        purge_message = await interaction.channel.send(embed=embed)
        
        purged_count = 0
        
        try:
            # Supprimer tous les threads actifs
            for thread in self.forum_channel.threads:
                try:
                    await thread.delete()
                    purged_count += 1
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression du thread {thread.id}: {e}")
            
            # Supprimer tous les threads archivés
            async for thread in self.forum_channel.archived_threads(limit=None):
                try:
                    await thread.delete()
                    purged_count += 1
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression du thread archivé {thread.id}: {e}")
            
            # Message de succès
            success_embed = create_secure_embed(
                "✅ Purge terminée avec succès !",
                f"**{purged_count}** signalements ont été supprimés du forum.\n\n📋 **Approuvé par:** {len(self.validators)} validateurs\n📅 **Date:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                discord.Color.green()
            )
            
            # Log de sécurité
            audit_logger = AuditLogger()
            audit_logger.log_security_event(
                "FORUM_PURGED",
                f"Forum purged by quorum validation. Deleted {purged_count} threads. Approved by {len(self.validators)} validators.",
                interaction.user.id
            )
            
            await purge_message.edit(embed=success_embed)
            
        except Exception as e:
            error_embed = create_secure_embed(
                "❌ Erreur lors de la purge",
                f"Une erreur s'est produite: {str(e)}",
                discord.Color.red()
            )
            await purge_message.edit(embed=error_embed)
            logger.error(f"Erreur lors de la purge: {e}")
    
    async def finalize_rejection(self, interaction: discord.Interaction):
        """Finalise le rejet de la purge"""
        self.is_finalized = True
        
        for item in self.children:
            item.disabled = True
        
        embed = create_secure_embed(
            "❌ Purge annulée",
            f"La demande de purge a été rejetée par la communauté.\n\n📅 **Date:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            discord.Color.red()
        )
        
        await interaction.channel.send(embed=embed)
        
        # Mettre à jour le message avec les boutons désactivés
        try:
            async for message in interaction.channel.history(limit=10):
                if message.author == interaction.client.user and message.components:
                    await message.edit(view=self)
                    break
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des boutons: {e}")


class PurgeFirstConfirmationModal(discord.ui.Modal, title="⚠️ CONFIRMATION DE PURGE - ÉTAPE 1/2"):
    """Première étape de confirmation par modal"""
    
    def __init__(self, guild_id: int, initiator_id: int, forum_channel, total_threads: int, validators_count: int):
        super().__init__()
        self.guild_id = guild_id
        self.initiator_id = initiator_id  
        self.forum_channel = forum_channel
        self.total_threads = total_threads
        self.validators_count = validators_count
    
    confirmation_text = discord.ui.TextInput(
        label="Tapez 'CONFIRMER PURGE' pour continuer",
        placeholder="CONFIRMER PURGE",
        required=True,
        max_length=50
    )
    
    reason = discord.ui.TextInput(
        label="Raison de la purge (obligatoire)",
        placeholder="Ex: Nettoyage mensuel, forum saturé, maintenance...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.confirmation_text.value.upper() != "CONFIRMER PURGE":
            await interaction.response.send_message(
                "❌ Confirmation incorrecte. Opération annulée.", ephemeral=True
            )
            return
        
        # Deuxième étape : validation par quorum des validateurs
        view = PurgeConfirmationView(self.guild_id, self.initiator_id, self.forum_channel)
        
        embed = create_secure_embed(
            "⚠️ DEMANDE DE PURGE - VALIDATION REQUISE",
            f"**Demandeur:** {interaction.user.display_name}\n**Raison:** {self.reason.value}\n\n📊 **Statistiques:**\n- Threads à supprimer: **{self.total_threads}**\n- Validateurs requis: **{int(self.validators_count * BOT_CONFIG['QUORUM_PERCENTAGE'] / 100)}** sur {self.validators_count} ({BOT_CONFIG['QUORUM_PERCENTAGE']}%)\n\n⚠️ **ATTENTION:** Cette action supprimera TOUS les signalements du forum !",
            discord.Color.red()
        )
        
        embed.add_field(
            name="🕰️ Validité",
            value="10 minutes",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Action",
            value="Purge complète du forum",
            inline=True
        )
        
        # Log de sécurité
        audit_logger = AuditLogger()
        audit_logger.log_security_event(
            "PURGE_REQUESTED",
            f"Purge requested by {interaction.user.id}. Reason: {self.reason.value}. Threads to delete: {self.total_threads}",
            interaction.user.id
        )
        
        await interaction.response.send_message(
            f"<@&{discord.utils.get(interaction.guild.roles, name=BOT_CONFIG['VALIDATOR_ROLE_NAME']).id}>\n🚨 **DEMANDE DE PURGE** 🚨",
            embed=embed, 
            view=view
        )


@app_commands.command(name="purge", description="Purger complètement le forum de signalements (Double confirmation + Quorum requis)")
async def purge_forum_reports(interaction: discord.Interaction):
    """Purge complète du forum avec double confirmation et validation par quorum"""
    
    # VÉRIFICATIONS RAPIDES SEULEMENT - tout le reste dans le modal
    try:
        # Vérification admin rapide
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                ERROR_MESSAGES["no_permission"], ephemeral=True
            )
            return
        
        # Trouver le forum rapidement
        alerts_forum = discord.utils.get(interaction.guild.channels, name=BOT_CONFIG["ALERTS_CHANNEL_NAME"])
        if not alerts_forum:
            await interaction.response.send_message(
                ERROR_MESSAGES["forum_not_found"], ephemeral=True
            )
            return
        
        # Compter les threads rapidement
        total_threads = len(alerts_forum.threads)
        
        # Envoyer le modal IMMÉDIATEMENT
        modal = PurgeFirstConfirmationModal(interaction.guild.id, interaction.user.id, alerts_forum, total_threads, 1)
        await interaction.response.send_modal(modal)
        
    except Exception as e:
        logger.error(f"Erreur purge: {e}")
        try:
            await interaction.response.send_message(
                f"❌ Erreur lors de l'initialisation: {str(e)[:100]}", ephemeral=True
            )
        except:
            pass