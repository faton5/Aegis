"""
Vues Discord pour la configuration du serveur (version refactorisée)
"""
import discord
from discord.ui import View, Button, Select
from typing import Optional

from config.bot_config import bot_settings
from config.logging_config import get_logger
from locales.translation_manager import translator

logger = get_logger('ui.setup_views')


class SetupMainView(View):
    """Vue principale du setup avec boutons de configuration"""
    
    def __init__(self, guild_id: int, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
    
    @discord.ui.button(
        label="🔧 Configuration de base", 
        style=discord.ButtonStyle.primary, 
        custom_id="basic_setup"
    )
    async def basic_setup(self, interaction: discord.Interaction, button: Button):
        """Configuration de base (forums, rôles)"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Vérifier si le forum existe déjà
            alerts_forum = discord.utils.get(
                interaction.guild.channels, 
                name=bot_settings.alerts_channel_name
            )
            validator_role = discord.utils.get(
                interaction.guild.roles, 
                name=bot_settings.validator_role_name
            )
            
            role_created = False
            channel_created = False
            
            # Créer le rôle Validateur s'il n'existe pas
            if not validator_role:
                validator_role = await interaction.guild.create_role(
                    name=bot_settings.validator_role_name,
                    color=discord.Color.green(),
                    reason="Configuration du bot Aegis"
                )
                role_created = True
                logger.info(f"Rôle {bot_settings.validator_role_name} créé dans {interaction.guild}")
            
            # Créer le forum d'alertes s'il n'existe pas
            if not alerts_forum:
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    interaction.guild.me: discord.PermissionOverwrite(
                        read_messages=True, 
                        send_messages=True, 
                        create_public_threads=True,
                        manage_messages=True
                    ),
                    validator_role: discord.PermissionOverwrite(
                        read_messages=True, 
                        send_messages=False,  # Pas d'écriture libre
                        use_application_commands=True,  # Pour les boutons
                        add_reactions=True  # Pour les réactions
                    )
                }
                
                # Ajouter les administrateurs
                for role in interaction.guild.roles:
                    if role.permissions.administrator:
                        overwrites[role] = discord.PermissionOverwrite(
                            read_messages=True, 
                            send_messages=True, 
                            create_public_threads=True
                        )
                
                alerts_forum = await interaction.guild.create_forum(
                    name=bot_settings.alerts_channel_name,
                    overwrites=overwrites,
                    reason="Configuration du bot Aegis"
                )
                channel_created = True
                logger.info(f"Forum {bot_settings.alerts_channel_name} créé dans {interaction.guild}")
            
            # Créer l'embed de confirmation
            embed = discord.Embed(
                title=translator.t("setup_complete_title", self.guild_id),
                description=translator.t("setup_complete_description", self.guild_id),
                color=discord.Color.green()
            )
            
            if role_created:
                embed.add_field(
                    name="🆕 Rôle créé", 
                    value=f"@{bot_settings.validator_role_name}", 
                    inline=True
                )
            else:
                embed.add_field(
                    name="✅ Rôle existant", 
                    value=f"@{bot_settings.validator_role_name}", 
                    inline=True
                )
            
            if channel_created:
                embed.add_field(
                    name="🆕 Forum créé", 
                    value=f"#{bot_settings.alerts_channel_name}", 
                    inline=True
                )
            else:
                embed.add_field(
                    name="✅ Forum existant", 
                    value=f"#{bot_settings.alerts_channel_name}", 
                    inline=True
                )
            
            # Sauvegarder la configuration
            from services.guild_service import guild_service
            guild_service.update_guild_config(self.guild_id, {
                'forum_channel_id': alerts_forum.id,
                'validator_role_id': validator_role.id,
                'configured': True
            })
            
            embed.add_field(
                name="📋 Prochaines étapes", 
                value=f"1. Attribuer le rôle @{bot_settings.validator_role_name} aux modérateurs\n2. Utiliser /agis pour tester", 
                inline=False
            )
            
            embed.set_footer(text="Configuration sauvegardée automatiquement")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur configuration de base: {e}")
            await interaction.followup.send(
                f"❌ Erreur lors de la configuration: {str(e)}", 
                ephemeral=True
            )
    
    @discord.ui.button(
        label="🌐 Langue", 
        style=discord.ButtonStyle.secondary, 
        custom_id="language_setup"
    )
    async def language_setup(self, interaction: discord.Interaction, button: Button):
        """Configuration de la langue du bot"""
        view = LanguageSelectView(self.guild_id)
        
        embed = discord.Embed(
            title=translator.t("setup_language_title", self.guild_id),
            description=translator.t("setup_language_description", self.guild_id),
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(
        label="📊 Statistiques", 
        style=discord.ButtonStyle.secondary, 
        custom_id="stats_setup"
    )
    async def stats_setup(self, interaction: discord.Interaction, button: Button):
        """Afficher les statistiques de configuration"""
        try:
            # Import dynamique pour éviter les dépendances circulaires
            from services.guild_service import guild_service as guild_config
            
            config = guild_config.get_guild_config(self.guild_id)
            
            embed = discord.Embed(
                title="📊 Configuration Actuelle",
                description="État de la configuration de votre serveur",
                color=discord.Color.blue()
            )
            
            # Vérifications des éléments configurés
            alerts_forum = discord.utils.get(
                interaction.guild.channels, 
                name=bot_settings.alerts_channel_name
            )
            validator_role = discord.utils.get(
                interaction.guild.roles, 
                name=bot_settings.validator_role_name
            )
            
            # Statut des éléments
            embed.add_field(
                name="🏷️ Langue configurée",
                value=config.get('language', 'fr').upper(),
                inline=True
            )
            
            embed.add_field(
                name="📋 Forum d'alertes",
                value="✅ Configuré" if alerts_forum else "❌ Manquant",
                inline=True
            )
            
            embed.add_field(
                name="👥 Rôle validateur", 
                value="✅ Configuré" if validator_role else "❌ Manquant",
                inline=True
            )
            
            # Statistiques d'utilisation si disponibles
            try:
                from services.report_service import ReportService
                # TODO: Ajouter stats si disponibles
                embed.add_field(
                    name="📈 Signalements",
                    value="Aucune donnée",
                    inline=True
                )
            except:
                pass
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'affichage des stats: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la récupération des statistiques.", 
                ephemeral=True
            )


class LanguageSelectView(View):
    """Vue pour sélectionner la langue du bot"""
    
    def __init__(self, guild_id: int, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
        
        # Créer le menu de sélection
        self._create_language_select()
    
    def _create_language_select(self):
        """Créer le menu de sélection des langues"""
        languages = translator.get_available_languages()
        
        options = []
        for code, name in languages.items():
            options.append(discord.SelectOption(
                label=name,
                value=code,
                description=f"Configurer le bot en {name.split()[1]}",
                emoji="🌐"
            ))
        
        select = LanguageSelect(
            placeholder="Choisissez une langue...",
            options=options,
            guild_id=self.guild_id
        )
        
        self.add_item(select)


class LanguageSelect(Select):
    """Menu de sélection des langues"""
    
    def __init__(self, guild_id: int, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = guild_id
    
    async def callback(self, interaction: discord.Interaction):
        """Callback quand une langue est sélectionnée"""
        try:
            selected_language = self.values[0]
            logger.info(f"Langue sélectionnée: {selected_language} pour guild {self.guild_id}")
            
            # Import dynamique pour éviter les dépendances circulaires
            from services.guild_service import guild_service
            
            # Mettre à jour la configuration
            guild_service.update_guild_config(self.guild_id, {
                'language': selected_language
            })
            
            # Confirmation avec la nouvelle langue
            embed = discord.Embed(
                title=translator.t("setup_complete_title", self.guild_id, language=selected_language),
                description=f"Langue configurée : {translator.get_available_languages()[selected_language]}",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="✅ Configuration sauvegardée",
                value=f"Le bot utilisera maintenant {selected_language.upper()} pour ce serveur.",
                inline=False
            )
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            logger.error(f"Erreur lors du changement de langue: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la configuration de la langue.",
                ephemeral=True
            )