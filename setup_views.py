# Interface de configuration avancée pour /setup
import discord
from discord import app_commands
from guild_config import guild_config
from utils import create_secure_embed, logger
from config import BOT_CONFIG
from translations import translator

class SetupMainView(discord.ui.View):
    """Vue principale du setup avec boutons de configuration"""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)  # 5 minutes
        self.guild_id = guild_id
    
    @discord.ui.button(label="🔧 Configuration de base", style=discord.ButtonStyle.primary, row=0)
    async def basic_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configuration de base (forums, rôles)"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Vérifier si le forum existe déjà
            alerts_forum = discord.utils.get(interaction.guild.channels, name=BOT_CONFIG["ALERTS_CHANNEL_NAME"])
            validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
            
            role_created = False
            channel_created = False
            
            # Créer le rôle Validateur s'il n'existe pas
            if not validator_role:
                validator_role = await interaction.guild.create_role(
                    name=BOT_CONFIG["VALIDATOR_ROLE_NAME"],
                    color=discord.Color.green(),
                    reason="Configuration du bot Agis"
                )
                role_created = True
            
            # Créer le forum d'alertes s'il n'existe pas
            if not alerts_forum:
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, create_public_threads=True),
                    validator_role: discord.PermissionOverwrite(read_messages=True, send_messages=True)
                }
                
                # Ajouter les administrateurs
                for role in interaction.guild.roles:
                    if role.permissions.administrator:
                        overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True, create_public_threads=True)
                
                alerts_forum = await interaction.guild.create_forum(
                    name=BOT_CONFIG["ALERTS_CHANNEL_NAME"],
                    overwrites=overwrites,
                    reason="Configuration du bot Agis"
                )
                channel_created = True
            
            # Créer un embed de confirmation
            embed = create_secure_embed(
                "✅ Configuration de base terminée",
                "Les éléments de base ont été configurés avec succès !",
                discord.Color.green()
            )
            
            if role_created:
                embed.add_field(name="🆕 Rôle créé", value=f"@{BOT_CONFIG['VALIDATOR_ROLE_NAME']}", inline=True)
            else:
                embed.add_field(name="✅ Rôle existant", value=f"@{BOT_CONFIG['VALIDATOR_ROLE_NAME']}", inline=True)
            
            if channel_created:
                embed.add_field(name="🆕 Forum créé", value=f"#{BOT_CONFIG['ALERTS_CHANNEL_NAME']}", inline=True)
            else:
                embed.add_field(name="✅ Forum existant", value=f"#{BOT_CONFIG['ALERTS_CHANNEL_NAME']}", inline=True)
            
            embed.add_field(name="📋 Prochaines étapes", value=f"1. Attribuer le rôle @{BOT_CONFIG['VALIDATOR_ROLE_NAME']} aux modérateurs\n2. Utiliser /agis pour tester", inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur configuration de base: {e}")
            await interaction.followup.send(f"❌ Erreur lors de la configuration: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="⚔️ Actions automatiques", style=discord.ButtonStyle.danger, row=0)
    async def auto_actions_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configuration des actions automatiques par niveau de flag"""
        view = AutoActionsView(self.guild_id)
        embed = create_auto_actions_embed(self.guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="🔔 Notifications", style=discord.ButtonStyle.secondary, row=1)
    async def notifications_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configuration des notifications"""
        view = NotificationsView(self.guild_id)
        embed = create_notifications_embed(self.guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="📊 Seuils & Limites", style=discord.ButtonStyle.secondary, row=1)
    async def thresholds_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configuration des seuils et limites"""
        view = ThresholdsView(self.guild_id)
        embed = create_thresholds_embed(self.guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="🛡️ Quarantaine", style=discord.ButtonStyle.secondary, row=2)
    async def quarantine_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configuration du système de quarantaine"""
        view = QuarantineView(self.guild_id)
        embed = create_quarantine_embed(self.guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="🌐 Langue", style=discord.ButtonStyle.secondary, row=2)
    async def language_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Sélection de la langue"""
        view = LanguageView(self.guild_id)
        embed = create_language_embed(self.guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="✅ Valider config", style=discord.ButtonStyle.success, row=3)
    async def validate_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Valider la configuration actuelle"""
        embed = create_config_summary_embed(self.guild_id)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class NotificationsView(discord.ui.View):
    """Vue pour configurer les notifications"""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
    
    @discord.ui.button(label="🔔 Canal notifications", style=discord.ButtonStyle.primary)
    async def set_notification_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Définir le canal de notification"""
        await interaction.response.send_message("Fonctionnalité en développement", ephemeral=True)
    
    @discord.ui.button(label="📬 Mentions", style=discord.ButtonStyle.secondary)
    async def set_mentions(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configurer les mentions automatiques"""
        await interaction.response.send_message("Fonctionnalité en développement", ephemeral=True)


class ThresholdsView(discord.ui.View):
    """Vue pour configurer les seuils et limites"""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
    
    @discord.ui.button(label="⏰ Rate Limiting", style=discord.ButtonStyle.primary)
    async def set_rate_limits(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configurer les limites de taux"""
        await interaction.response.send_message("Fonctionnalité en développement", ephemeral=True)
    
    @discord.ui.button(label="📊 Seuils validation", style=discord.ButtonStyle.secondary)
    async def set_validation_thresholds(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configurer les seuils de validation"""
        await interaction.response.send_message("Fonctionnalité en développement", ephemeral=True)


class AutoActionsView(discord.ui.View):
    """Vue pour configurer les actions automatiques"""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
    
    @discord.ui.select(
        placeholder="⚔️ Choisir l'action pour niveau CRITIQUE",
        options=[
            discord.SelectOption(label="🚫 Ban automatique", value="ban", description="Bannir immédiatement"),
            discord.SelectOption(label="👢 Kick automatique", value="kick", description="Expulser immédiatement"),
            discord.SelectOption(label="🛡️ Quarantaine", value="quarantine", description="Isoler l'utilisateur"),
            discord.SelectOption(label="🚨 Alerte seulement", value="alert", description="Alerter sans action"),
            discord.SelectOption(label="❌ Aucune action", value="none", description="Désactivé")
        ]
    )
    async def configure_critical_action(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Configurer l'action pour niveau critique"""
        await interaction.response.defer(ephemeral=True)
        
        # Mettre à jour la configuration
        config = guild_config.get_guild_config(self.guild_id)
        config["auto_actions"]["critical"] = select.values[0]
        guild_config.update_guild_config(self.guild_id, config)
        
        embed = create_secure_embed(
            "✅ Action CRITIQUE configurée",
            f"Action pour niveau critique : **{select.values[0]}**",
            discord.Color.green()
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)


class QuarantineView(discord.ui.View):
    """Vue pour configurer la quarantaine"""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
    
    @discord.ui.select(
        placeholder="🛡️ Configurer la quarantaine",
        options=[
            discord.SelectOption(label="✅ Activer la quarantaine", value="enable", description="Activer le système de quarantaine"),
            discord.SelectOption(label="❌ Désactiver la quarantaine", value="disable", description="Désactiver le système de quarantaine"),
            discord.SelectOption(label="🏷️ Changer nom du rôle", value="rename", description="Modifier le nom du rôle de quarantaine"),
            discord.SelectOption(label="⏰ Modifier durée", value="duration", description="Changer la durée de quarantaine")
        ]
    )
    async def configure_quarantine(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Configurer le système de quarantaine"""
        action = select.values[0]
        
        if action == "enable":
            await interaction.response.defer(ephemeral=True)
            
            config = guild_config.get_guild_config(self.guild_id)
            config["quarantine"]["enabled"] = True
            guild_config.update_guild_config(self.guild_id, config)
            
            embed = create_secure_embed(
                "✅ Quarantaine activée",
                "Le système de quarantaine est maintenant actif.",
                discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        elif action == "disable":
            await interaction.response.defer(ephemeral=True)
            
            config = guild_config.get_guild_config(self.guild_id)
            config["quarantine"]["enabled"] = False
            guild_config.update_guild_config(self.guild_id, config)
            
            embed = create_secure_embed(
                "❌ Quarantaine désactivée",
                "Le système de quarantaine est maintenant inactif.",
                discord.Color.orange()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        elif action == "rename":
            modal = QuarantineRenameModal(self.guild_id)
            await interaction.response.send_modal(modal)
            
        elif action == "duration":
            modal = QuarantineDurationModal(self.guild_id)
            await interaction.response.send_modal(modal)


class LanguageView(discord.ui.View):
    """Vue pour sélectionner la langue"""
    
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
    
    @discord.ui.button(label="🇫🇷 Français", style=discord.ButtonStyle.primary)
    async def set_french(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Définir le français comme langue"""
        translator.set_guild_language(self.guild_id, 'fr')
        await interaction.response.send_message("✅ Langue définie sur Français", ephemeral=True)
    
    @discord.ui.button(label="🇬🇧 English", style=discord.ButtonStyle.secondary)
    async def set_english(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Définir l'anglais comme langue"""
        translator.set_guild_language(self.guild_id, 'en')
        await interaction.response.send_message("✅ Language set to English", ephemeral=True)


# Fonctions pour créer les embeds
def create_notifications_embed(guild_id: int):
    """Crée l'embed pour la configuration des notifications"""
    config = guild_config.get_guild_config(guild_id) or {}
    
    embed = discord.Embed(
        title="🔔 Configuration des Notifications",
        description="Configurez les notifications automatiques pour votre serveur",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Canal actuel",
        value=config.get('notification_channel', 'Non configuré'),
        inline=True
    )
    
    embed.add_field(
        name="Mentions automatiques",
        value="Activées" if config.get('auto_mentions', False) else "Désactivées",
        inline=True
    )
    
    return embed


def create_thresholds_embed(guild_id: int):
    """Crée l'embed pour la configuration des seuils"""
    config = guild_config.get_guild_config(guild_id) or {}
    
    embed = discord.Embed(
        title="📊 Configuration des Seuils & Limites",
        description="Configurez les seuils de validation et limites de rate",
        color=discord.Color.orange()
    )
    
    embed.add_field(
        name="Rate limiting",
        value=f"{config.get('max_reports_per_hour', BOT_CONFIG['MAX_REPORTS_PER_USER_PER_HOUR'])} signalements/heure",
        inline=True
    )
    
    embed.add_field(
        name="Quorum validation",
        value=f"{config.get('quorum_percentage', BOT_CONFIG['QUORUM_PERCENTAGE'])}%",
        inline=True
    )
    
    return embed


def create_auto_actions_embed(guild_id: int):
    """Crée l'embed pour la configuration des actions automatiques"""
    embed = discord.Embed(
        title="⚔️ Actions Automatiques",
        description="Configurez les actions à effectuer selon le niveau de flagging",
        color=discord.Color.red()
    )
    
    embed.add_field(
        name="Niveau 1 (1-2 flags)",
        value="Surveillance renforcée",
        inline=False
    )
    
    embed.add_field(
        name="Niveau 2 (3-4 flags)",
        value="Restriction de permissions",
        inline=False
    )
    
    embed.add_field(
        name="Niveau 3 (5+ flags)",
        value="Quarantaine automatique",
        inline=False
    )
    
    return embed


def create_quarantine_embed(guild_id: int):
    """Crée l'embed pour la configuration de la quarantaine"""
    config = guild_config.get_guild_config(guild_id) or {}
    
    embed = discord.Embed(
        title="🛡️ Système de Quarantaine",
        description="Configurez le système de quarantaine automatique",
        color=discord.Color.dark_red()
    )
    
    embed.add_field(
        name="Rôle quarantaine",
        value=config.get('quarantine_role', 'Non configuré'),
        inline=True
    )
    
    embed.add_field(
        name="Canal quarantaine",
        value=config.get('quarantine_channel', 'Non configuré'),
        inline=True
    )
    
    return embed


def create_language_embed(guild_id: int):
    """Crée l'embed pour la sélection de langue"""
    current_lang = translator.get_guild_language(guild_id)
    lang_names = {"fr": "🇫🇷 Français", "en": "🇬🇧 English"}
    
    embed = discord.Embed(
        title="🌐 Sélection de Langue / Language Selection",
        description="Choisissez la langue du bot / Choose the bot language",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="Langue actuelle / Current language",
        value=lang_names.get(current_lang, current_lang),
        inline=False
    )
    
    embed.add_field(
        name="Note",
        value="Cette langue sera utilisée pour toutes les interactions du bot sur ce serveur.\n"
              "This language will be used for all bot interactions on this server.",
        inline=False
    )
    
    return embed


def create_config_summary_embed(guild_id: int):
    """Crée l'embed de résumé de configuration"""
    config = guild_config.get_guild_config(guild_id) or {}
    lang = translator.get_guild_language(guild_id)
    
    embed = discord.Embed(
        title="📋 Résumé de Configuration",
        description="Résumé de la configuration actuelle du serveur",
        color=discord.Color.green()
    )
    
    # Langue
    lang_names = {"fr": "🇫🇷 Français", "en": "🇬🇧 English"}
    embed.add_field(
        name="🌐 Langue",
        value=lang_names.get(lang, lang),
        inline=True
    )
    
    # Forum d'alertes
    embed.add_field(
        name="📢 Forum d'alertes", 
        value=config.get('alerts_channel', BOT_CONFIG["ALERTS_CHANNEL_NAME"]),
        inline=True
    )
    
    # Rôle validateur
    embed.add_field(
        name="👤 Rôle validateur",
        value=config.get('validator_role', BOT_CONFIG["VALIDATOR_ROLE_NAME"]),
        inline=True
    )
    
    # Seuils
    embed.add_field(
        name="📊 Quorum validation",
        value=f"{config.get('quorum_percentage', BOT_CONFIG['QUORUM_PERCENTAGE'])}%",
        inline=True
    )
    
    embed.add_field(
        name="⏰ Rate limiting",
        value=f"{config.get('max_reports_per_hour', BOT_CONFIG['MAX_REPORTS_PER_USER_PER_HOUR'])} signalements/h",
        inline=True
    )
    
    # Supabase
    embed.add_field(
        name="🗄️ Supabase",
        value="✅ Activé" if BOT_CONFIG["SUPABASE_ENABLED"] else "❌ Désactivé",
        inline=True
    )
    
    embed.set_footer(text="Configuration validée • Use /setup to modify")
    
    return embed


# Modals pour configuration avancée
class ActionConfigModal(discord.ui.Modal, title="⚔️ Configuration Actions Automatiques"):
    """Modal pour configurer les actions automatiques"""
    
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id
        
        # Charger la config actuelle
        config = guild_config.get_guild_config(guild_id)
        auto_actions = config.get("auto_actions", {})
        
        # Pré-remplir avec les valeurs actuelles
        self.critical_action.default = auto_actions.get("critical", "ban")
        self.high_action.default = auto_actions.get("high", "quarantine")
        self.medium_action.default = auto_actions.get("medium", "alert")
        self.low_action.default = auto_actions.get("low", "none")
    
    critical_action = discord.ui.TextInput(
        label="Action pour niveau CRITIQUE",
        placeholder="ban, kick, quarantine, alert, none",
        required=True,
        max_length=20
    )
    
    high_action = discord.ui.TextInput(
        label="Action pour niveau ÉLEVÉ",
        placeholder="ban, kick, quarantine, alert, none",
        required=True,
        max_length=20
    )
    
    medium_action = discord.ui.TextInput(
        label="Action pour niveau MOYEN",
        placeholder="ban, kick, quarantine, alert, none",
        required=True,
        max_length=20
    )
    
    low_action = discord.ui.TextInput(
        label="Action pour niveau FAIBLE",
        placeholder="ban, kick, quarantine, alert, none",
        required=True,
        max_length=20
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        valid_actions = ["ban", "kick", "quarantine", "alert", "none"]
        
        # Valider les entrées
        actions = {
            "critical": self.critical_action.value.lower().strip(),
            "high": self.high_action.value.lower().strip(),
            "medium": self.medium_action.value.lower().strip(),
            "low": self.low_action.value.lower().strip()
        }
        
        for level, action in actions.items():
            if action not in valid_actions:
                await interaction.followup.send(
                    f"❌ Action invalide pour {level}: `{action}`. Actions valides: {', '.join(valid_actions)}",
                    ephemeral=True
                )
                return
        
        # Sauvegarder la configuration
        try:
            guild_config.update_guild_config(self.guild_id, {"auto_actions": actions})
            
            embed = create_secure_embed(
                "✅ Actions automatiques configurées",
                "Les actions automatiques ont été mises à jour avec succès !",
                discord.Color.green()
            )
            
            embed.add_field(name="🔴 Critique", value=actions["critical"], inline=True)
            embed.add_field(name="🟡 Élevé", value=actions["high"], inline=True)
            embed.add_field(name="🟢 Moyen", value=actions["medium"], inline=True)
            embed.add_field(name="⚪ Faible", value=actions["low"], inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur configuration actions: {e}")
            await interaction.followup.send(
                f"❌ Erreur lors de la sauvegarde: {str(e)}",
                ephemeral=True
            )


class QuarantineConfigModal(discord.ui.Modal, title="🛡️ Configuration Quarantaine"):
    """Modal pour configurer la quarantaine"""
    
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id
        
        # Charger la config actuelle
        config = guild_config.get_guild_config(guild_id)
        quarantine = config.get("quarantine", {})
        
        # Pré-remplir avec les valeurs actuelles
        self.role_name.default = quarantine.get("role_name", "Quarantaine Aegis")
        self.duration.default = str(quarantine.get("duration_hours", 24))
        self.remove_roles.default = "oui" if quarantine.get("remove_roles", True) else "non"
    
    role_name = discord.ui.TextInput(
        label="Nom du rôle de quarantaine",
        placeholder="Quarantaine Aegis",
        required=True,
        max_length=50
    )
    
    duration = discord.ui.TextInput(
        label="Durée en heures",
        placeholder="24",
        required=True,
        max_length=5
    )
    
    remove_roles = discord.ui.TextInput(
        label="Supprimer autres rôles ? (oui/non)",
        placeholder="oui",
        required=True,
        max_length=3
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Valider la durée
            duration_hours = int(self.duration.value)
            if duration_hours < 1 or duration_hours > 168:  # 1h à 7 jours
                raise ValueError("La durée doit être entre 1 et 168 heures")
            
            # Valider remove_roles
            remove_roles_str = self.remove_roles.value.lower().strip()
            if remove_roles_str not in ["oui", "non", "yes", "no"]:
                raise ValueError("Supprimer rôles doit être 'oui' ou 'non'")
            
            remove_roles_bool = remove_roles_str in ["oui", "yes"]
            
            # Sauvegarder la configuration
            quarantine_config = {
                "enabled": True,
                "role_name": self.role_name.value.strip(),
                "duration_hours": duration_hours,
                "remove_roles": remove_roles_bool,
                "restricted_channels": []
            }
            
            guild_config.update_guild_config(self.guild_id, {"quarantine": quarantine_config})
            
            embed = create_secure_embed(
                "✅ Quarantaine configurée",
                "Le système de quarantaine a été configuré avec succès !",
                discord.Color.green()
            )
            
            embed.add_field(name="🏷️ Rôle", value=quarantine_config["role_name"], inline=True)
            embed.add_field(name="⏰ Durée", value=f"{duration_hours}h", inline=True)
            embed.add_field(name="🗑️ Supprimer rôles", value="✅ Oui" if remove_roles_bool else "❌ Non", inline=True)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except ValueError as e:
            await interaction.followup.send(f"❌ Valeur invalide: {str(e)}", ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur configuration quarantaine: {e}")
            await interaction.followup.send(f"❌ Erreur lors de la sauvegarde: {str(e)}", ephemeral=True)


# Modals simples pour quarantaine
class QuarantineRenameModal(discord.ui.Modal, title="🏷️ Renommer le rôle de quarantaine"):
    """Modal pour renommer le rôle de quarantaine"""
    
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id
        
        # Charger le nom actuel
        config = guild_config.get_guild_config(guild_id)
        current_name = config.get("quarantine", {}).get("role_name", "Quarantaine Aegis")
        self.role_name.default = current_name
    
    role_name = discord.ui.TextInput(
        label="Nouveau nom du rôle",
        placeholder="Quarantaine Aegis",
        required=True,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            config = guild_config.get_guild_config(self.guild_id)
            config["quarantine"]["role_name"] = self.role_name.value.strip()
            guild_config.update_guild_config(self.guild_id, config)
            
            embed = create_secure_embed(
                "✅ Rôle renommé",
                f"Le rôle de quarantaine s'appelle maintenant : **{self.role_name.value.strip()}**",
                discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur renommage rôle quarantaine: {e}")
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)


class QuarantineDurationModal(discord.ui.Modal, title="⏰ Modifier la durée de quarantaine"):
    """Modal pour modifier la durée de quarantaine"""
    
    def __init__(self, guild_id: int):
        super().__init__()
        self.guild_id = guild_id
        
        # Charger la durée actuelle
        config = guild_config.get_guild_config(guild_id)
        current_duration = config.get("quarantine", {}).get("duration_hours", 24)
        self.duration.default = str(current_duration)
    
    duration = discord.ui.TextInput(
        label="Durée en heures (1-168)",
        placeholder="24",
        required=True,
        max_length=3
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            duration_hours = int(self.duration.value)
            if duration_hours < 1 or duration_hours > 168:
                raise ValueError("La durée doit être entre 1 et 168 heures")
            
            config = guild_config.get_guild_config(self.guild_id)
            config["quarantine"]["duration_hours"] = duration_hours
            guild_config.update_guild_config(self.guild_id, config)
            
            embed = create_secure_embed(
                "✅ Durée modifiée",
                f"La durée de quarantaine est maintenant de **{duration_hours}h**",
                discord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except ValueError as e:
            await interaction.followup.send(f"❌ Valeur invalide: {str(e)}", ephemeral=True)
        except Exception as e:
            logger.error(f"Erreur modification durée quarantaine: {e}")
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)