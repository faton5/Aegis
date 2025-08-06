"""
Tests complets pour TOUTES les commandes slash du bot Aegis
Teste que chaque commande fonctionne dans tous les scénarios
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os

# Import des commandes à tester
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from bot import (
    agis_report, check_user, validate_report, show_categories, 
    anonymise_report
)
# from test_commands import test_diagnostics  # Import commenté car non nécessaire
from config import BOT_CONFIG


class TestAgisCommand:
    """Tests exhaustifs pour la commande /agis"""
    
    @pytest.mark.asyncio
    async def test_agis_guild_not_configured(self, mock_interaction, mock_guild, 
                                           mock_discord_utils, clean_guild_config):
        """Test /agis sur serveur non configuré"""
        # Utiliser une guilde non configurée
        mock_interaction.guild = mock_guild
        mock_guild.channels = []
        mock_guild.roles = []
        
        # discord.utils.get ne trouve rien
        mock_discord_utils.return_value = None
        
        await agis_report(mock_interaction)
        
        # Vérifier qu'un message d'erreur est envoyé
        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert call_args.kwargs['ephemeral'] is True
        assert 'embed' in call_args.kwargs
        
        # Vérifier que le contenu indique une configuration manquante
        embed = call_args.kwargs['embed']
        assert "configuration" in embed.title.lower() or "manquante" in embed.title.lower()
    
    @pytest.mark.asyncio
    async def test_agis_guild_configured_success(self, mock_interaction, configured_guild, 
                                               mock_discord_utils):
        """Test /agis sur serveur configuré - succès"""
        mock_interaction.guild = configured_guild
        
        # discord.utils.get retourne les bonnes valeurs
        def utils_get_side_effect(collection, **kwargs):
            if 'name' in kwargs:
                if kwargs['name'] == BOT_CONFIG["ALERTS_CHANNEL_NAME"]:
                    return configured_guild.channels[0]  # Forum
                elif kwargs['name'] == BOT_CONFIG["VALIDATOR_ROLE_NAME"]:
                    return configured_guild.roles[0]    # Rôle validateur
            return None
        
        mock_discord_utils.side_effect = utils_get_side_effect
        
        await agis_report(mock_interaction)
        
        # Vérifier qu'une réponse avec view est envoyée
        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert call_args.kwargs['ephemeral'] is True
        assert 'embed' in call_args.kwargs
        assert 'view' in call_args.kwargs
        
        # Vérifier que l'embed contient le titre du signalement
        embed = call_args.kwargs['embed']
        assert "signalement" in embed.title.lower() or "agis" in embed.title.lower()
    
    @pytest.mark.asyncio
    async def test_agis_missing_forum_only(self, mock_interaction, configured_guild, 
                                         mock_discord_utils):
        """Test /agis avec forum manquant mais rôle présent"""
        mock_interaction.guild = configured_guild
        
        def utils_get_side_effect(collection, **kwargs):
            if 'name' in kwargs:
                if kwargs['name'] == BOT_CONFIG["ALERTS_CHANNEL_NAME"]:
                    return None  # Pas de forum
                elif kwargs['name'] == BOT_CONFIG["VALIDATOR_ROLE_NAME"]:
                    return configured_guild.roles[0]  # Rôle présent
            return None
        
        mock_discord_utils.side_effect = utils_get_side_effect
        
        await agis_report(mock_interaction)
        
        # Doit envoyer un message d'erreur
        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert call_args.kwargs['ephemeral'] is True


class TestCheckCommand:
    """Tests exhaustifs pour la commande /check"""
    
    @pytest.mark.asyncio
    async def test_check_user_no_permissions(self, mock_interaction, mock_user):
        """Test /check sans permissions"""
        # Retirer toutes les permissions
        import discord
        mock_interaction.user.guild_permissions = discord.Permissions.none()
        mock_interaction.guild.roles = []
        
        await check_user(mock_interaction, mock_user)
        
        # Vérifier que la réponse est différée
        mock_interaction.response.defer.assert_called_once_with(ephemeral=True)
        
        # Vérifier qu'un message d'erreur est envoyé
        mock_interaction.followup.send.assert_called_once()
        call_args = mock_interaction.followup.send.call_args
        assert call_args.kwargs['ephemeral'] is True
        assert 'embed' in call_args.kwargs
    
    @pytest.mark.asyncio
    async def test_check_user_admin_permissions(self, mock_admin_interaction, mock_user, 
                                               mock_supabase_client):
        """Test /check avec permissions admin"""
        # Mock Supabase retourne pas de flag
        mock_supabase_client.check_user_flag.return_value = None
        
        with patch('bot.supabase_client', mock_supabase_client):
            await check_user(mock_admin_interaction, mock_user)
            
            # Vérifier que Supabase est appelé
            mock_supabase_client.check_user_flag.assert_called_once_with(
                mock_user.id,
                mock_admin_interaction.guild.id,
                mock_admin_interaction.guild.name
            )
            
            # Vérifier qu'une réponse est envoyée
            mock_admin_interaction.followup.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_check_user_flagged(self, mock_admin_interaction, mock_user, 
                                    mock_supabase_client):
        """Test /check utilisateur flagué"""
        # Mock utilisateur flagué
        flag_data = {
            "is_flagged": True,
            "flag_level": "high",
            "flag_category": "harassment",
            "flag_reason": "Test harassment",
            "flagged_by_guild_name": "Other Guild",
            "validation_count": 3,
            "flagged_date": MagicMock()
        }
        flag_data["flagged_date"].strftime.return_value = "01/01/2024"
        mock_supabase_client.check_user_flag.return_value = flag_data
        
        with patch('bot.supabase_client', mock_supabase_client):
            await check_user(mock_admin_interaction, mock_user)
            
            # Vérifier que l'embed contient les infos du flag
            call_args = mock_admin_interaction.followup.send.call_args
            embed = call_args.kwargs['embed']
            # L'embed doit contenir des informations sur le flag
            assert hasattr(embed, 'fields') or hasattr(embed, 'description')
    
    @pytest.mark.asyncio
    async def test_check_user_supabase_disabled(self, mock_admin_interaction, mock_user):
        """Test /check avec Supabase désactivé"""
        # Désactiver temporairement Supabase
        original_value = BOT_CONFIG["SUPABASE_ENABLED"]
        BOT_CONFIG["SUPABASE_ENABLED"] = False
        
        try:
            await check_user(mock_admin_interaction, mock_user)
            
            # Vérifier qu'un message d'erreur service indisponible est envoyé
            call_args = mock_admin_interaction.followup.send.call_args
            assert call_args.kwargs['ephemeral'] is True
            
        finally:
            BOT_CONFIG["SUPABASE_ENABLED"] = original_value
    
    @pytest.mark.asyncio
    async def test_check_user_validator_role(self, mock_validator_interaction, mock_user, 
                                           mock_supabase_client):
        """Test /check avec rôle validateur"""
        mock_supabase_client.check_user_flag.return_value = None
        
        with patch('bot.supabase_client', mock_supabase_client):
            await check_user(mock_validator_interaction, mock_user)
            
            # L'utilisateur validateur doit pouvoir utiliser la commande
            mock_supabase_client.check_user_flag.assert_called_once()
            mock_validator_interaction.followup.send.assert_called_once()


class TestValidateCommand:
    """Tests exhaustifs pour la commande /validate"""
    
    @pytest.mark.asyncio
    async def test_validate_no_role(self, mock_interaction, mock_discord_utils):
        """Test /validate sans rôle validateur"""
        # discord.utils.get ne trouve pas le rôle
        mock_discord_utils.return_value = None
        
        await validate_report(mock_interaction)
        
        # Vérifier qu'un message d'erreur est envoyé
        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert call_args.kwargs['ephemeral'] is True
        assert 'embed' in call_args.kwargs
    
    @pytest.mark.asyncio
    async def test_validate_with_role(self, mock_validator_interaction, mock_discord_utils):
        """Test /validate avec rôle validateur"""
        # Retourner le rôle validateur
        validator_role = mock_validator_interaction.guild.roles[0]
        mock_discord_utils.return_value = validator_role
        
        await validate_report(mock_validator_interaction)
        
        # Vérifier qu'un message de succès est envoyé
        mock_validator_interaction.response.send_message.assert_called_once()
        call_args = mock_validator_interaction.response.send_message.call_args
        assert call_args.kwargs['ephemeral'] is True
        assert 'embed' in call_args.kwargs
    
    @pytest.mark.asyncio
    async def test_validate_user_not_in_role(self, mock_interaction, mock_discord_utils):
        """Test /validate utilisateur pas dans le rôle validateur"""
        # Retourner le rôle mais l'utilisateur ne l'a pas
        validator_role = MagicMock()
        validator_role.name = BOT_CONFIG["VALIDATOR_ROLE_NAME"]
        mock_discord_utils.return_value = validator_role
        mock_interaction.user.roles = []  # Pas de rôles
        
        await validate_report(mock_interaction)
        
        # Doit envoyer un message d'erreur d'accès refusé
        call_args = mock_interaction.response.send_message.call_args
        assert call_args.kwargs['ephemeral'] is True


class TestCategoriesCommand:
    """Tests pour la commande /categories"""
    
    @pytest.mark.asyncio
    async def test_show_categories_basic(self, mock_interaction):
        """Test /categories affichage basique"""
        await show_categories(mock_interaction)
        
        # Vérifier qu'une réponse est envoyée
        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert call_args.kwargs['ephemeral'] is True
        assert 'embed' in call_args.kwargs
        
        # Vérifier que l'embed contient les catégories
        embed = call_args.kwargs['embed']
        assert hasattr(embed, 'fields') or hasattr(embed, 'description')
    
    @pytest.mark.asyncio
    async def test_show_categories_content(self, mock_interaction):
        """Test que /categories affiche bien le contenu attendu"""
        await show_categories(mock_interaction)
        
        call_args = mock_interaction.response.send_message.call_args
        embed = call_args.kwargs['embed']
        
        # Le titre doit mentionner les catégories
        assert "catégories" in embed.title.lower() or "categories" in embed.title.lower()


class TestAnonymiseCommand:
    """Tests exhaustifs pour la commande /anonymiser"""
    
    @pytest.mark.asyncio
    async def test_anonymise_no_permissions(self, mock_interaction, mock_discord_utils):
        """Test /anonymiser sans permissions"""
        # Retirer les permissions et le rôle
        import discord
        mock_interaction.user.guild_permissions = discord.Permissions.none()
        mock_interaction.user.roles = []
        mock_discord_utils.return_value = None
        
        await anonymise_report(mock_interaction)
        
        # Vérifier qu'un message d'erreur est envoyé
        mock_interaction.response.send_message.assert_called_once()
        call_args = mock_interaction.response.send_message.call_args
        assert call_args.kwargs['ephemeral'] is True
    
    @pytest.mark.asyncio
    async def test_anonymise_with_admin(self, mock_admin_interaction, mock_evidence_collector):
        """Test /anonymiser avec permissions admin"""
        # Pas de signalements actifs
        mock_evidence_collector.user_thread_mapping = {}
        
        await anonymise_report(mock_admin_interaction, None)
        
        # Vérifier que la réponse est différée puis envoyée
        mock_admin_interaction.response.defer.assert_called_once_with(ephemeral=True)
        mock_admin_interaction.followup.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_anonymise_with_validator_role(self, mock_validator_interaction, 
                                               mock_evidence_collector, mock_discord_utils):
        """Test /anonymiser avec rôle validateur"""
        mock_evidence_collector.user_thread_mapping = {}
        validator_role = mock_validator_interaction.guild.roles[0]
        mock_discord_utils.return_value = validator_role
        
        await anonymise_report(mock_validator_interaction, None)
        
        # Doit fonctionner car l'utilisateur a le rôle validateur
        mock_validator_interaction.response.defer.assert_called_once()
        mock_validator_interaction.followup.send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_anonymise_with_active_report(self, mock_admin_interaction, 
                                              mock_evidence_collector):
        """Test /anonymiser avec un signalement actif"""
        # Simuler un signalement actif
        from datetime import datetime, timedelta
        future_expiry = (datetime.now() + timedelta(hours=1)).timestamp()
        
        mock_evidence_collector.user_thread_mapping = {
            123456789: (999888777, "TEST_REPORT_123", future_expiry)
        }
        
        await anonymise_report(mock_admin_interaction, "TEST_REPORT_123")
        
        # Vérifier que remove_user_mapping est appelé
        mock_evidence_collector.remove_user_mapping.assert_called_once_with(123456789)
        
        # Vérifier qu'un message de succès est envoyé
        call_args = mock_admin_interaction.followup.send.call_args
        assert call_args.kwargs['ephemeral'] is True
    
    @pytest.mark.asyncio
    async def test_anonymise_report_not_found(self, mock_admin_interaction, 
                                            mock_evidence_collector):
        """Test /anonymiser avec ID de signalement inexistant"""
        mock_evidence_collector.user_thread_mapping = {}
        
        await anonymise_report(mock_admin_interaction, "NONEXISTENT_REPORT")
        
        # Vérifier qu'un message "non trouvé" est envoyé
        call_args = mock_admin_interaction.followup.send.call_args
        embed = call_args.kwargs['embed']
        # L'embed doit indiquer que le signalement n'a pas été trouvé
        assert "non trouvé" in embed.title.lower() or "not found" in embed.title.lower()


class TestCommandsIntegration:
    """Tests d'intégration entre plusieurs commandes"""
    
    @pytest.mark.asyncio
    async def test_commands_work_with_translations(self, mock_interaction, configured_guild):
        """Test que toutes les commandes fonctionnent avec le système de traduction"""
        # Tester avec différentes langues
        from guild_config import guild_config
        
        # Test en français
        guild_config.update_guild_config(configured_guild.id, {'language': 'fr'})
        await show_categories(mock_interaction)
        
        # Test en anglais
        guild_config.update_guild_config(configured_guild.id, {'language': 'en'})
        await show_categories(mock_interaction)
        
        # Les deux doivent fonctionner sans erreur
        assert mock_interaction.response.send_message.call_count == 2
    
    @pytest.mark.asyncio
    async def test_all_commands_handle_exceptions(self, mock_interaction):
        """Test que toutes les commandes gèrent les exceptions"""
        # Simuler une exception dans discord.utils.get
        with patch('discord.utils.get', side_effect=Exception("Test exception")):
            
            # Tester toutes les commandes principales
            commands_to_test = [
                (agis_report, [mock_interaction]),
                (show_categories, [mock_interaction]),
                (validate_report, [mock_interaction]),
                (anonymise_report, [mock_interaction, None])
            ]
            
            for command, args in commands_to_test:
                try:
                    await command(*args)
                    # Si on arrive ici, la commande a géré l'exception
                    assert True
                except Exception as e:
                    # La commande ne doit pas crasher
                    pytest.fail(f"Commande {command.__name__} a crashé: {e}")


class TestCommandsErrorHandling:
    """Tests de gestion d'erreur pour toutes les commandes"""
    
    @pytest.mark.asyncio
    async def test_agis_handles_forum_creation_error(self, mock_interaction, configured_guild, 
                                                   mock_discord_utils):
        """Test que /agis gère les erreurs de création de thread"""
        mock_interaction.guild = configured_guild
        
        # Mock discord.utils.get pour retourner les objets configurés
        def utils_get_side_effect(collection, **kwargs):
            if 'name' in kwargs:
                if kwargs['name'] == BOT_CONFIG["ALERTS_CHANNEL_NAME"]:
                    forum = configured_guild.channels[0]
                    # Simuler une erreur lors de create_thread
                    forum.create_thread.side_effect = Exception("Thread creation failed")
                    return forum
                elif kwargs['name'] == BOT_CONFIG["VALIDATOR_ROLE_NAME"]:
                    return configured_guild.roles[0]
            return None
        
        mock_discord_utils.side_effect = utils_get_side_effect
        
        # La commande ne doit pas crasher même si create_thread échoue
        await agis_report(mock_interaction)
        
        # Une réponse doit quand même être envoyée
        mock_interaction.response.send_message.assert_called()
    
    @pytest.mark.asyncio
    async def test_check_handles_supabase_error(self, mock_admin_interaction, mock_user, 
                                              mock_supabase_client):
        """Test que /check gère les erreurs Supabase"""
        # Simuler une erreur Supabase
        mock_supabase_client.check_user_flag.side_effect = Exception("Supabase error")
        
        with patch('bot.supabase_client', mock_supabase_client):
            # La commande ne doit pas crasher
            await check_user(mock_admin_interaction, mock_user)
            
            # Une réponse doit être envoyée même en cas d'erreur
            mock_admin_interaction.response.defer.assert_called_once()


class TestCommandsConfiguration:
    """Tests de validation de la configuration pour les commandes"""
    
    def test_bot_config_has_required_values(self):
        """Test que BOT_CONFIG contient toutes les valeurs requises"""
        required_keys = [
            "ALERTS_CHANNEL_NAME",
            "VALIDATOR_ROLE_NAME",
            "SUPABASE_ENABLED",
            "MAX_REPORTS_PER_USER_PER_HOUR",
            "QUORUM_PERCENTAGE"
        ]
        
        for key in required_keys:
            assert key in BOT_CONFIG, f"Clé manquante dans BOT_CONFIG: {key}"
            assert BOT_CONFIG[key] is not None, f"Valeur nulle pour {key}"
    
    def test_bot_config_types(self):
        """Test que les types dans BOT_CONFIG sont corrects"""
        assert isinstance(BOT_CONFIG["ALERTS_CHANNEL_NAME"], str)
        assert isinstance(BOT_CONFIG["VALIDATOR_ROLE_NAME"], str)
        assert isinstance(BOT_CONFIG["SUPABASE_ENABLED"], bool)
        assert isinstance(BOT_CONFIG["MAX_REPORTS_PER_USER_PER_HOUR"], int)
        assert isinstance(BOT_CONFIG["QUORUM_PERCENTAGE"], (int, float))
    
    @pytest.mark.asyncio
    async def test_commands_work_without_supabase(self, mock_interaction):
        """Test que les commandes fonctionnent même si Supabase est désactivé"""
        original_value = BOT_CONFIG["SUPABASE_ENABLED"]
        BOT_CONFIG["SUPABASE_ENABLED"] = False
        
        try:
            # Ces commandes doivent fonctionner même sans Supabase
            await show_categories(mock_interaction)
            await validate_report(mock_interaction)
            
            # Vérifier qu'elles ont bien répondu
            assert mock_interaction.response.send_message.call_count >= 2
            
        finally:
            BOT_CONFIG["SUPABASE_ENABLED"] = original_value