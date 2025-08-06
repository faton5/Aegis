"""
Vues Discord pour les signalements
"""
import discord
from discord.ui import View, Select, Button
from typing import Optional

from config.logging_config import get_logger
from config.bot_config import REPORT_CATEGORIES

logger = get_logger('ui.report_views')


class CategorySelectView(View):
    """Vue pour sélectionner une catégorie de signalement"""
    
    def __init__(self, guild_id: int, bot, translator, timeout: float = 300):
        super().__init__(timeout=timeout)
        self.guild_id = guild_id
        self.bot = bot
        self.translator = translator
        
        # Créer le menu de sélection
        self._create_category_select()
    
    def _create_category_select(self):
        """Créer le menu de sélection des catégories"""
        options = []
        
        for category_id, category_data in REPORT_CATEGORIES.items():
            # Traduire le label et la description
            label_key = f"category_{category_id}"
            label = self.translator.t(label_key, self.guild_id, fallback=category_data['label'])
            
            # Traduire la description aussi
            desc_key = f"category_{category_id}_description"
            description = self.translator.t(desc_key, self.guild_id, fallback=category_data['description'])
            
            option = discord.SelectOption(
                label=label,
                value=category_id,
                description=description[:100],  # Limite Discord
                emoji=self._get_category_emoji(category_id)
            )
            options.append(option)
        
        # Créer le select avec les options (placeholder traduit)
        placeholder = self.translator.t("category_select_placeholder", self.guild_id)
        select = CategorySelect(
            placeholder=placeholder,
            options=options,
            guild_id=self.guild_id,
            bot=self.bot,
            translator=self.translator
        )
        
        self.add_item(select)
    
    def _get_category_emoji(self, category_id: str) -> Optional[str]:
        """Obtenir l'emoji pour une catégorie"""
        emoji_map = {
            "harassment": "🚫",
            "inappropriate_content": "📵", 
            "suspicious_behavior": "🔍",
            "child_safety": "🛡️",
            "spam": "📢",
            "scam": "💰",
            "threats": "⚔️",
            "other": "❓"
        }
        return emoji_map.get(category_id)
    
    async def on_timeout(self):
        """Quand la vue expire"""
        # Désactiver tous les composants
        for item in self.children:
            item.disabled = True
        
        # Note: Nous ne pouvons pas modifier le message ici
        # car nous n'avons pas de référence à l'interaction


class CategorySelect(Select):
    """Menu de sélection des catégories"""
    
    def __init__(self, guild_id: int, bot, translator, **kwargs):
        super().__init__(**kwargs)
        self.guild_id = guild_id
        self.bot = bot
        self.translator = translator
    
    async def callback(self, interaction: discord.Interaction):
        """Callback quand une catégorie est sélectionnée"""
        try:
            selected_category = self.values[0]
            logger.info(f"Catégorie sélectionnée: {selected_category} par {interaction.user}")
            
            # Import dynamique pour éviter les dépendances circulaires
            from ui.modals.report_modals import AgisReportModal
            
            # Créer le modal de signalement
            modal = AgisReportModal(
                category=selected_category,
                guild_id=self.guild_id,
                bot=self.bot,
                translator=self.translator
            )
            
            # Afficher le modal
            await interaction.response.send_modal(modal)
            
        except Exception as e:
            logger.error(f"Erreur dans CategorySelect callback: {e}")
            
            try:
                error_message = self.translator.t("error_database_error", self.guild_id)
                await interaction.response.send_message(
                    f"❌ {error_message}",
                    ephemeral=True
                )
            except:
                pass  # Éviter les erreurs en cascade


class ReportValidationView(View):
    """Vue pour valider/rejeter un signalement"""
    
    def __init__(self, report_id: str, bot, translator, timeout: float = 3600):  # 1h timeout
        super().__init__(timeout=timeout)
        self.report_id = report_id
        self.bot = bot
        self.translator = translator
    
    @discord.ui.button(
        label="✅ Approuver",
        style=discord.ButtonStyle.success,
        custom_id="approve_report"
    )
    async def approve_button(self, interaction: discord.Interaction, button: Button):
        """Bouton pour approuver un signalement"""
        try:
            # Vérifier les permissions
            if not self._check_validation_permissions(interaction):
                await interaction.response.send_message(
                    "❌ Vous n'avez pas les permissions pour valider les signalements.",
                    ephemeral=True
                )
                return
            
            # Valider le signalement
            success = await self.bot.report_service.update_report_status(
                self.report_id,
                "validated",
                interaction.user.id
            )
            
            if success:
                embed = discord.Embed(
                    title="✅ Signalement Approuvé",
                    description=f"Le signalement `{self.report_id}` a été approuvé par {interaction.user.mention}",
                    color=discord.Color.green()
                )
                
                # Désactiver les boutons
                for item in self.children:
                    item.disabled = True
                
                await interaction.response.edit_message(embed=embed, view=self)
                
            else:
                await interaction.response.send_message(
                    "❌ Erreur lors de l'approbation du signalement.",
                    ephemeral=True
                )
        
        except Exception as e:
            logger.error(f"Erreur lors de l'approbation: {e}")
            await interaction.response.send_message(
                "❌ Une erreur s'est produite.",
                ephemeral=True
            )
    
    @discord.ui.button(
        label="❌ Rejeter",
        style=discord.ButtonStyle.danger,
        custom_id="reject_report"
    )
    async def reject_button(self, interaction: discord.Interaction, button: Button):
        """Bouton pour rejeter un signalement"""
        try:
            # Vérifier les permissions
            if not self._check_validation_permissions(interaction):
                await interaction.response.send_message(
                    "❌ Vous n'avez pas les permissions pour valider les signalements.",
                    ephemeral=True
                )
                return
            
            # Rejeter le signalement
            success = await self.bot.report_service.update_report_status(
                self.report_id,
                "rejected",
                interaction.user.id
            )
            
            if success:
                embed = discord.Embed(
                    title="❌ Signalement Rejeté",
                    description=f"Le signalement `{self.report_id}` a été rejeté par {interaction.user.mention}",
                    color=discord.Color.red()
                )
                
                # Désactiver les boutons
                for item in self.children:
                    item.disabled = True
                
                await interaction.response.edit_message(embed=embed, view=self)
                
            else:
                await interaction.response.send_message(
                    "❌ Erreur lors du rejet du signalement.",
                    ephemeral=True
                )
        
        except Exception as e:
            logger.error(f"Erreur lors du rejet: {e}")
            await interaction.response.send_message(
                "❌ Une erreur s'est produite.",
                ephemeral=True
            )
    
    def _check_validation_permissions(self, interaction: discord.Interaction) -> bool:
        """Vérifier si l'utilisateur peut valider des signalements"""
        # Vérifier les permissions administrateur
        if interaction.user.guild_permissions.administrator:
            return True
        
        # TODO: Vérifier le rôle validateur configuré
        # from config.bot_config import bot_settings
        # validator_role_name = bot_settings.validator_role_name
        
        return False