"""
Cog pour la configuration avancée du serveur
"""
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from config.logging_config import get_logger
from locales.translation_manager import translator

logger = get_logger('config')


class ConfigCog(commands.Cog):
    """Commandes de configuration avancée"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(
        name="config",
        description="Configuration avancée du serveur Aegis"
    )
    async def config_command(self, interaction: discord.Interaction):
        """Interface de configuration avancée"""
        try:
            # Vérifier les permissions administrateur
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    "❌ Vous devez être administrateur pour utiliser cette commande.",
                    ephemeral=True
                )
                return
            
            logger.info(f"Commande /config utilisée par {interaction.user} dans {interaction.guild}")
            
            # Créer la vue principale de configuration
            view = ConfigMainView(interaction.guild_id)
            
            # Créer l'embed principal
            embed = discord.Embed(
                title=translator.t("config_title", interaction.guild_id),
                description=translator.t("config_description", interaction.guild_id),
                color=discord.Color.blue()
            )
            
            # Obtenir la configuration actuelle
            from services.guild_service import guild_service
            config = guild_service.get_guild_config(interaction.guild_id)
            
            # Afficher les actions automatiques actuelles
            auto_actions = config.get('auto_actions', {})
            embed.add_field(
                name="🔧 Actions Automatiques",
                value=f"**Critique:** {auto_actions.get('critical', 'ban')}\n**Élevé:** {auto_actions.get('high', 'quarantine')}\n**Moyen:** {auto_actions.get('medium', 'alert')}\n**Faible:** {auto_actions.get('low', 'none')}",
                inline=True
            )
            
            # Afficher les seuils de validation
            thresholds = config.get('validation_thresholds', {})
            embed.add_field(
                name="📊 Seuils de Validation",
                value=f"**Quorum:** {thresholds.get('quorum_percentage', 80)}%\n**Min validateurs:** {thresholds.get('min_validators', 2)}\n**Timeout:** {thresholds.get('validation_timeout_hours', 24)}h",
                inline=True
            )
            
            # Afficher les limites de taux
            limits = config.get('rate_limits', {})
            embed.add_field(
                name="⏱️ Limites de Taux",
                value=f"**Reports/user/h:** {limits.get('reports_per_user_per_hour', 3)}\n**Reports/guild/h:** {limits.get('reports_per_guild_per_hour', 20)}",
                inline=True
            )
            
            embed.set_footer(text="Utilisez les boutons ci-dessous pour modifier ces paramètres")
            
            await interaction.response.send_message(
                embed=embed,
                view=view,
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"Erreur dans /config: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de l'affichage de la configuration.",
                ephemeral=True
            )


class ConfigMainView(discord.ui.View):
    """Vue principale de configuration"""
    
    def __init__(self, guild_id: int, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
    
    @discord.ui.button(
        label="🔧 Actions Auto", 
        style=discord.ButtonStyle.primary, 
        custom_id="auto_actions_config"
    )
    async def auto_actions_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configuration des actions automatiques"""
        view = AutoActionsConfigView(self.guild_id)
        
        from services.guild_service import guild_service
        config = guild_service.get_guild_config(self.guild_id)
        auto_actions = config.get('auto_actions', {})
        
        embed = discord.Embed(
            title="🔧 Configuration Actions Automatiques",
            description="Définissez les actions à prendre automatiquement selon le niveau de gravité des signalements validés.",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="🔴 Niveau CRITIQUE (3+ signalements validés)",
            value=f"Action actuelle: **{auto_actions.get('critical', 'ban')}**",
            inline=False
        )
        
        embed.add_field(
            name="🟠 Niveau ÉLEVÉ (2+ signalements validés)", 
            value=f"Action actuelle: **{auto_actions.get('high', 'quarantine')}**",
            inline=False
        )
        
        embed.add_field(
            name="🟡 Niveau MOYEN (1+ signalement validé)",
            value=f"Action actuelle: **{auto_actions.get('medium', 'alert')}**", 
            inline=False
        )
        
        embed.add_field(
            name="🟢 Niveau FAIBLE (0 signalement validé)",
            value=f"Action actuelle: **{auto_actions.get('low', 'none')}**",
            inline=False
        )
        
        embed.add_field(
            name="📋 Actions Disponibles",
            value="• **ban** - Bannir l'utilisateur\n• **kick** - Expulser l'utilisateur\n• **quarantine** - Mettre en quarantaine\n• **alert** - Alerter les modérateurs\n• **none** - Aucune action",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(
        label="📊 Seuils", 
        style=discord.ButtonStyle.secondary, 
        custom_id="thresholds_config"
    )
    async def thresholds_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configuration des seuils de validation"""
        view = ThresholdsConfigView(self.guild_id)
        
        from services.guild_service import guild_service
        config = guild_service.get_guild_config(self.guild_id)
        thresholds = config.get('validation_thresholds', {})
        
        embed = discord.Embed(
            title="📊 Configuration Seuils de Validation",
            description="Paramétrez les critères pour valider automatiquement les signalements.",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="🎯 Quorum (%)",
            value=f"**{thresholds.get('quorum_percentage', 80)}%** des validateurs doivent approuver",
            inline=True
        )
        
        embed.add_field(
            name="👥 Minimum Validateurs",
            value=f"Au moins **{thresholds.get('min_validators', 2)}** validateurs nécessaires",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Timeout (heures)",
            value=f"Auto-rejet après **{thresholds.get('validation_timeout_hours', 24)}h** sans consensus",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(
        label="⏱️ Limites", 
        style=discord.ButtonStyle.secondary, 
        custom_id="limits_config"
    )
    async def limits_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configuration des limites de taux"""
        view = LimitsConfigView(self.guild_id)
        
        from services.guild_service import guild_service
        config = guild_service.get_guild_config(self.guild_id)
        limits = config.get('rate_limits', {})
        
        embed = discord.Embed(
            title="⏱️ Configuration Limites de Taux",
            description="Définissez les limites pour éviter le spam de signalements.",
            color=discord.Color.yellow()
        )
        
        embed.add_field(
            name="👤 Par Utilisateur",
            value=f"**{limits.get('reports_per_user_per_hour', 3)}** signalements max par heure",
            inline=True
        )
        
        embed.add_field(
            name="🏠 Par Serveur", 
            value=f"**{limits.get('reports_per_guild_per_hour', 20)}** signalements max par heure",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class AutoActionsConfigView(discord.ui.View):
    """Vue pour configurer les actions automatiques"""
    
    def __init__(self, guild_id: int, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
        self.current_level = "critical"
    
    @discord.ui.select(
        placeholder="Sélectionner le niveau à configurer",
        options=[
            discord.SelectOption(label="🔴 Critique", value="critical", description="3+ signalements validés"),
            discord.SelectOption(label="🟠 Élevé", value="high", description="2+ signalements validés"),
            discord.SelectOption(label="🟡 Moyen", value="medium", description="1+ signalement validé"),
            discord.SelectOption(label="🟢 Faible", value="low", description="0 signalement validé"),
        ]
    )
    async def select_level(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.current_level = select.values[0]
        await interaction.response.defer()
    
    @discord.ui.select(
        placeholder="Sélectionner l'action à appliquer",
        options=[
            discord.SelectOption(label="🔨 Bannir", value="ban", description="Bannir l'utilisateur"),
            discord.SelectOption(label="👢 Expulser", value="kick", description="Expulser l'utilisateur"),
            discord.SelectOption(label="🔒 Quarantaine", value="quarantine", description="Mettre en quarantaine"),
            discord.SelectOption(label="⚠️ Alerter", value="alert", description="Alerter les modérateurs"),
            discord.SelectOption(label="❌ Aucune", value="none", description="Aucune action automatique"),
        ]
    )
    async def select_action(self, interaction: discord.Interaction, select: discord.ui.Select):
        action = select.values[0]
        
        # Sauvegarder la configuration
        from services.guild_service import guild_service
        config = guild_service.get_guild_config(self.guild_id)
        
        if 'auto_actions' not in config:
            config['auto_actions'] = {}
        
        config['auto_actions'][self.current_level] = action
        
        guild_service.update_guild_config(self.guild_id, {
            'auto_actions': config['auto_actions']
        })
        
        await interaction.response.send_message(
            f"✅ Action **{action}** configurée pour le niveau **{self.current_level}**.",
            ephemeral=True
        )


class ThresholdsConfigView(discord.ui.View):
    """Vue pour configurer les seuils"""
    
    def __init__(self, guild_id: int, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
    
    @discord.ui.button(label="🎯 Modifier Quorum", style=discord.ButtonStyle.primary)
    async def modify_quorum(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = QuorumModal(self.guild_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="👥 Modifier Min Validateurs", style=discord.ButtonStyle.primary)  
    async def modify_min_validators(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = MinValidatorsModal(self.guild_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="⏰ Modifier Timeout", style=discord.ButtonStyle.primary)
    async def modify_timeout(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TimeoutModal(self.guild_id)
        await interaction.response.send_modal(modal)


class LimitsConfigView(discord.ui.View):
    """Vue pour configurer les limites"""
    
    def __init__(self, guild_id: int, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
    
    @discord.ui.button(label="👤 Limites Utilisateur", style=discord.ButtonStyle.secondary)
    async def modify_user_limits(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = UserLimitsModal(self.guild_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🏠 Limites Serveur", style=discord.ButtonStyle.secondary)
    async def modify_guild_limits(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = GuildLimitsModal(self.guild_id)
        await interaction.response.send_modal(modal)


# Modals pour la configuration
class QuorumModal(discord.ui.Modal):
    def __init__(self, guild_id: int):
        super().__init__(title="Modifier le Quorum", timeout=300)
        self.guild_id = guild_id
        
        self.quorum_input = discord.ui.TextInput(
            label="Pourcentage de Quorum (1-100)",
            placeholder="80",
            min_length=1,
            max_length=3
        )
        self.add_item(self.quorum_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            quorum = int(self.quorum_input.value)
            if not 1 <= quorum <= 100:
                raise ValueError("Le quorum doit être entre 1 et 100")
            
            from services.guild_service import guild_service
            config = guild_service.get_guild_config(self.guild_id)
            if 'validation_thresholds' not in config:
                config['validation_thresholds'] = {}
            
            config['validation_thresholds']['quorum_percentage'] = quorum
            guild_service.update_guild_config(self.guild_id, {
                'validation_thresholds': config['validation_thresholds']
            })
            
            await interaction.response.send_message(
                f"✅ Quorum mis à jour: {quorum}%", ephemeral=True
            )
        except ValueError as e:
            await interaction.response.send_message(
                translator.t("config_invalid_value", interaction.guild_id, error=str(e)),
                ephemeral=True
            )


class MinValidatorsModal(discord.ui.Modal):
    def __init__(self, guild_id: int):
        super().__init__(title="Modifier Min Validateurs", timeout=300)
        self.guild_id = guild_id
        
        self.min_validators_input = discord.ui.TextInput(
            label="Nombre minimum de validateurs (1-10)",
            placeholder="2",
            min_length=1,
            max_length=2
        )
        self.add_item(self.min_validators_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            min_val = int(self.min_validators_input.value)
            if not 1 <= min_val <= 10:
                raise ValueError("Le minimum doit être entre 1 et 10")
            
            from services.guild_service import guild_service
            config = guild_service.get_guild_config(self.guild_id)
            if 'validation_thresholds' not in config:
                config['validation_thresholds'] = {}
            
            config['validation_thresholds']['min_validators'] = min_val
            guild_service.update_guild_config(self.guild_id, {
                'validation_thresholds': config['validation_thresholds']
            })
            
            await interaction.response.send_message(
                f"✅ Minimum validateurs mis à jour: {min_val}", ephemeral=True
            )
        except ValueError as e:
            await interaction.response.send_message(
                translator.t("config_invalid_value", interaction.guild_id, error=str(e)),
                ephemeral=True
            )


class TimeoutModal(discord.ui.Modal):
    def __init__(self, guild_id: int):
        super().__init__(title="Modifier Timeout", timeout=300)
        self.guild_id = guild_id
        
        self.timeout_input = discord.ui.TextInput(
            label="Timeout en heures (1-168)",
            placeholder="24",
            min_length=1,
            max_length=3
        )
        self.add_item(self.timeout_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            timeout = int(self.timeout_input.value)
            if not 1 <= timeout <= 168:  # Max 1 semaine
                raise ValueError("Le timeout doit être entre 1 et 168 heures")
            
            from services.guild_service import guild_service
            config = guild_service.get_guild_config(self.guild_id)
            if 'validation_thresholds' not in config:
                config['validation_thresholds'] = {}
            
            config['validation_thresholds']['validation_timeout_hours'] = timeout
            guild_service.update_guild_config(self.guild_id, {
                'validation_thresholds': config['validation_thresholds']
            })
            
            await interaction.response.send_message(
                f"✅ Timeout mis à jour: {timeout} heures", ephemeral=True
            )
        except ValueError as e:
            await interaction.response.send_message(
                translator.t("config_invalid_value", interaction.guild_id, error=str(e)),
                ephemeral=True
            )


class UserLimitsModal(discord.ui.Modal):
    def __init__(self, guild_id: int):
        super().__init__(title="Limites Utilisateur", timeout=300)
        self.guild_id = guild_id
        
        self.user_limit_input = discord.ui.TextInput(
            label="Reports par utilisateur par heure (1-20)",
            placeholder="3",
            min_length=1,
            max_length=2
        )
        self.add_item(self.user_limit_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.user_limit_input.value)
            if not 1 <= limit <= 20:
                raise ValueError("La limite doit être entre 1 et 20")
            
            from services.guild_service import guild_service
            config = guild_service.get_guild_config(self.guild_id)
            if 'rate_limits' not in config:
                config['rate_limits'] = {}
            
            config['rate_limits']['reports_per_user_per_hour'] = limit
            guild_service.update_guild_config(self.guild_id, {
                'rate_limits': config['rate_limits']
            })
            
            await interaction.response.send_message(
                f"✅ Limite utilisateur mise à jour: {limit} reports/h", ephemeral=True
            )
        except ValueError as e:
            await interaction.response.send_message(
                translator.t("config_invalid_value", interaction.guild_id, error=str(e)),
                ephemeral=True
            )


class GuildLimitsModal(discord.ui.Modal):
    def __init__(self, guild_id: int):
        super().__init__(title="Limites Serveur", timeout=300)
        self.guild_id = guild_id
        
        self.guild_limit_input = discord.ui.TextInput(
            label="Reports par serveur par heure (5-100)",
            placeholder="20",
            min_length=1,
            max_length=3
        )
        self.add_item(self.guild_limit_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit = int(self.guild_limit_input.value)
            if not 5 <= limit <= 100:
                raise ValueError("La limite doit être entre 5 et 100")
            
            from services.guild_service import guild_service
            config = guild_service.get_guild_config(self.guild_id)
            if 'rate_limits' not in config:
                config['rate_limits'] = {}
            
            config['rate_limits']['reports_per_guild_per_hour'] = limit
            guild_service.update_guild_config(self.guild_id, {
                'rate_limits': config['rate_limits']
            })
            
            await interaction.response.send_message(
                f"✅ Limite serveur mise à jour: {limit} reports/h", ephemeral=True
            )
        except ValueError as e:
            await interaction.response.send_message(
                translator.t("config_invalid_value", interaction.guild_id, error=str(e)),
                ephemeral=True
            )


async def setup(bot):
    """Fonction appelée lors du chargement du cog"""
    await bot.add_cog(ConfigCog(bot))
