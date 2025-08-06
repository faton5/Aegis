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
                title="⚙️ Configuration Avancée Aegis",
                description="Personnalisez le comportement du bot selon vos besoins.",
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
    
    # TODO: Ajouter des modals pour modifier les valeurs numériques


class LimitsConfigView(discord.ui.View):
    """Vue pour configurer les limites"""
    
    def __init__(self, guild_id: int, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
    
    # TODO: Ajouter des modals pour modifier les limites


async def setup(bot):
    """Fonction appelée lors du chargement du cog"""
    await bot.add_cog(ConfigCog(bot))
    logger.info("✅ Cog Config chargé")