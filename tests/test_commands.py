"""
Tests pour les commandes slash du bot Aegis
"""
import pytest
import discord
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Import des commandes à tester
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from bot import agis_report, check_user, validate_report, show_categories, anonymise_report
from config import BOT_CONFIG
from translations import translator


class TestAgisCommand:
    """Tests pour la commande /agis"""
    
    @pytest.mark.asyncio
    async def test_agis_command_not_configured(self, mock_interaction):
        """Test /agis sur un serveur non configuré"""
        # Le serveur n'a pas de forum ni de rôle configuré
        mock_interaction.guild.channels = []
        mock_interaction.guild.roles = []
        
        await agis_report(mock_interaction)
        
        # Vérifier qu'une réponse d'erreur est envoyée
        mock_interaction.response.send_message.assert_called_once()
        args = mock_interaction.response.send_message.call_args
        assert "ephemeral" in args.kwargs
        assert args.kwargs["ephemeral"] is True
        # Vérifier qu'un embed d'erreur est envoyé
        assert "embed" in args.kwargs
    
    @pytest.mark.asyncio
    async def test_agis_command_configured(self, mock_interaction, configured_guild, mock_validator_role, mock_alerts_forum):
        """Test /agis sur un serveur configuré"""
        mock_interaction.guild = configured_guild
        
        # Mock discord.utils.get pour retourner nos objets mockés
        with patch('discord.utils.get') as mock_get:
            def get_side_effect(collection, **kwargs):
                if 'name' in kwargs:
                    if kwargs['name'] == BOT_CONFIG["ALERTS_CHANNEL_NAME"]:
                        return mock_alerts_forum
                    elif kwargs['name'] == BOT_CONFIG["VALIDATOR_ROLE_NAME"]:
                        return mock_validator_role
                return None
            
            mock_get.side_effect = get_side_effect
            
            await agis_report(mock_interaction)
            
            # Vérifier qu'une réponse avec view est envoyée
            mock_interaction.response.send_message.assert_called_once()
            args = mock_interaction.response.send_message.call_args
            assert "ephemeral" in args.kwargs
            assert args.kwargs["ephemeral"] is True
            assert "embed" in args.kwargs
            assert "view" in args.kwargs


class TestCheckCommand:
    """Tests pour la commande /check"""
    
    @pytest.mark.asyncio
    async def test_check_user_no_permissions(self, mock_interaction, mock_user):
        """Test /check sans permissions"""
        # L'utilisateur n'a pas les permissions
        mock_interaction.user.guild_permissions = discord.Permissions.none()
        mock_interaction.guild.roles = []
        
        await check_user(mock_interaction, mock_user)
        
        # Attendre que la réponse soit différée
        mock_interaction.response.defer.assert_called_once_with(ephemeral=True)
        
        # Vérifier qu'un message d'erreur est envoyé
        mock_interaction.followup.send.assert_called_once()
        args = mock_interaction.followup.send.call_args
        assert "ephemeral" in args.kwargs
        assert args.kwargs["ephemeral"] is True
    
    @pytest.mark.asyncio
    async def test_check_user_supabase_disabled(self, mock_interaction, mock_user):
        """Test /check avec Supabase désactivé"""
        # L'utilisateur a les permissions admin
        mock_interaction.user.guild_permissions = discord.Permissions.all()
        
        # Désactiver Supabase temporairement
        original_value = BOT_CONFIG["SUPABASE_ENABLED"]
        BOT_CONFIG["SUPABASE_ENABLED"] = False
        
        try:
            await check_user(mock_interaction, mock_user)
            
            mock_interaction.response.defer.assert_called_once_with(ephemeral=True)
            mock_interaction.followup.send.assert_called_once()
            args = mock_interaction.followup.send.call_args
            assert "ephemeral" in args.kwargs
            assert args.kwargs["ephemeral"] is True
        finally:
            BOT_CONFIG["SUPABASE_ENABLED"] = original_value
    
    @pytest.mark.asyncio
    async def test_check_user_success_no_flag(self, mock_interaction, mock_user, mock_supabase_client):
        """Test /check utilisateur non flagué"""
        # L'utilisateur a les permissions admin
        mock_interaction.user.guild_permissions = discord.Permissions.all()
        
        # Supabase retourne aucun flag
        mock_supabase_client.check_user_flag.return_value = None
        
        with patch('bot.supabase_client', mock_supabase_client):
            await check_user(mock_interaction, mock_user)
            
            mock_interaction.response.defer.assert_called_once_with(ephemeral=True)
            mock_interaction.followup.send.assert_called_once()
            
            # Vérifier que Supabase a été appelé
            mock_supabase_client.check_user_flag.assert_called_once_with(
                mock_user.id,
                mock_interaction.guild.id,
                mock_interaction.guild.name
            )


class TestValidateCommand:
    """Tests pour la commande /validate"""
    
    @pytest.mark.asyncio
    async def test_validate_no_role(self, mock_interaction):
        """Test /validate sans rôle validateur"""
        mock_interaction.guild.roles = []
        mock_interaction.user.roles = []
        
        with patch('discord.utils.get', return_value=None):
            await validate_report(mock_interaction)
            
            mock_interaction.response.send_message.assert_called_once()
            args = mock_interaction.response.send_message.call_args
            assert "ephemeral" in args.kwargs
            assert args.kwargs["ephemeral"] is True
    
    @pytest.mark.asyncio
    async def test_validate_with_role(self, mock_interaction, mock_validator_role):
        """Test /validate avec rôle validateur"""
        mock_interaction.user.roles = [mock_validator_role]
        
        with patch('discord.utils.get', return_value=mock_validator_role):
            await validate_report(mock_interaction)
            
            mock_interaction.response.send_message.assert_called_once()
            args = mock_interaction.response.send_message.call_args
            assert "ephemeral" in args.kwargs
            assert args.kwargs["ephemeral"] is True
            # Vérifier qu'un embed de succès est envoyé
            assert "embed" in args.kwargs


class TestCategoriesCommand:
    """Tests pour la commande /categories"""
    
    @pytest.mark.asyncio
    async def test_show_categories(self, mock_interaction):
        """Test /categories affiche les catégories"""
        await show_categories(mock_interaction)
        
        mock_interaction.response.send_message.assert_called_once()
        args = mock_interaction.response.send_message.call_args
        assert "ephemeral" in args.kwargs
        assert args.kwargs["ephemeral"] is True
        assert "embed" in args.kwargs


class TestAnonymiseCommand:
    """Tests pour la commande /anonymiser"""
    
    @pytest.mark.asyncio
    async def test_anonymise_no_permissions(self, mock_interaction):
        """Test /anonymiser sans permissions"""
        mock_interaction.user.guild_permissions = discord.Permissions.none()
        mock_interaction.user.roles = []
        mock_interaction.guild.roles = []
        
        with patch('discord.utils.get', return_value=None):
            await anonymise_report(mock_interaction)
            
            mock_interaction.response.send_message.assert_called_once()
            args = mock_interaction.response.send_message.call_args
            assert "ephemeral" in args.kwargs
            assert args.kwargs["ephemeral"] is True
    
    @pytest.mark.asyncio
    async def test_anonymise_no_active_reports(self, mock_interaction, mock_validator_role):
        """Test /anonymiser sans signalements actifs"""
        mock_interaction.user.roles = [mock_validator_role]
        mock_interaction.user.guild_permissions = discord.Permissions.all()
        
        # Mock evidence_collector vide
        with patch('bot.evidence_collector') as mock_evidence:
            mock_evidence.user_thread_mapping = {}
            
            with patch('discord.utils.get', return_value=mock_validator_role):
                await anonymise_report(mock_interaction, None)
                
                mock_interaction.response.defer.assert_called_once_with(ephemeral=True)
                mock_interaction.followup.send.assert_called_once()


class TestTranslationSystem:
    """Tests pour le système de traduction"""
    
    def test_translator_french_default(self):
        """Test que le français est la langue par défaut"""
        result = translator.t("report_modal_title")
        assert "Signalement Agis" in result
    
    def test_translator_english(self):
        """Test traduction en anglais"""
        result = translator.t("report_modal_title", language="en")
        assert "Agis Report" in result
    
    def test_translator_fallback(self):
        """Test fallback pour clé inexistante"""
        result = translator.t("nonexistent_key", fallback="fallback_text")
        assert result == "fallback_text"
    
    def test_translator_with_parameters(self):
        """Test traduction avec paramètres"""
        result = translator.t("user_flagged_centralized", language="fr")
        # Doit contenir le placeholder pour formatting
        assert "{user}" in result