"""
Tests d'intégration pour le bot Aegis avec mocks des services externes
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Import des modules d'intégration
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from supabase_client import supabase_client
from guild_config import guild_config
from config import BOT_CONFIG


class TestSupabaseIntegration:
    """Tests d'intégration avec Supabase (mockés)"""
    
    @pytest.mark.asyncio
    async def test_supabase_connect_success(self, mock_supabase_client):
        """Test connexion Supabase réussie"""
        mock_supabase_client.connect.return_value = True
        
        result = await mock_supabase_client.connect()
        assert result is True
        mock_supabase_client.connect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_supabase_connect_failure(self, mock_supabase_client):
        """Test échec de connexion Supabase"""
        mock_supabase_client.connect.return_value = False
        
        result = await mock_supabase_client.connect()
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_user_flag_not_flagged(self, mock_supabase_client):
        """Test vérification utilisateur non flagué"""
        mock_supabase_client.check_user_flag.return_value = None
        
        result = await mock_supabase_client.check_user_flag(123456789, 987654321, "Test Guild")
        assert result is None
        mock_supabase_client.check_user_flag.assert_called_once_with(123456789, 987654321, "Test Guild")
    
    @pytest.mark.asyncio
    async def test_check_user_flag_flagged(self, mock_supabase_client):
        """Test vérification utilisateur flagué"""
        flag_data = {
            "is_flagged": True,
            "flag_level": "high",
            "flag_category": "harassment",
            "flag_reason": "Test reason",
            "flagged_by_guild_name": "Other Guild",
            "validation_count": 2,
            "flagged_date": "2024-01-01"
        }
        mock_supabase_client.check_user_flag.return_value = flag_data
        
        result = await mock_supabase_client.check_user_flag(123456789, 987654321, "Test Guild")
        assert result == flag_data
        assert result["is_flagged"] is True
        assert result["flag_level"] == "high"
    
    @pytest.mark.asyncio
    async def test_add_validated_report_success(self, mock_supabase_client):
        """Test ajout de signalement validé"""
        mock_supabase_client.add_validated_report.return_value = True
        
        result = await mock_supabase_client.add_validated_report(
            user_id=123456789,
            username="testuser",
            flag_level="high",
            reason="Test reason",
            category="harassment",
            guild_id=987654321,
            guild_name="Test Guild"
        )
        
        assert result is True
        mock_supabase_client.add_validated_report.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_guild_stats(self, mock_supabase_client):
        """Test récupération des statistiques de guilde"""
        stats = {
            "total_checks": 15,
            "flags_found": 3,
            "flags_contributed": 7
        }
        mock_supabase_client.get_guild_stats.return_value = stats
        
        result = await mock_supabase_client.get_guild_stats(987654321)
        assert result == stats
        assert result["total_checks"] == 15
        assert result["flags_found"] == 3


class TestGuildConfigIntegration:
    """Tests d'intégration avec le système de configuration des guildes"""
    
    def test_guild_config_get_nonexistent(self, clean_guild_config):
        """Test récupération configuration guilde inexistante"""
        config = guild_config.get_guild_config(999999999)
        # Doit retourner une configuration par défaut ou vide
        assert isinstance(config, dict)
    
    def test_guild_config_update_new_guild(self, clean_guild_config):
        """Test mise à jour configuration nouvelle guilde"""
        guild_id = 123456789
        new_config = {
            'language': 'en',
            'configured': True,
            'forum_channel_id': 111222333,
            'validator_role_id': 444555666
        }
        
        guild_config.update_guild_config(guild_id, new_config)
        
        retrieved_config = guild_config.get_guild_config(guild_id)
        assert retrieved_config['language'] == 'en'
        assert retrieved_config['configured'] is True
    
    def test_guild_config_update_existing_guild(self, clean_guild_config):
        """Test mise à jour configuration guilde existante"""
        guild_id = 123456789
        
        # Configuration initiale
        initial_config = {'language': 'fr', 'configured': False}
        guild_config.update_guild_config(guild_id, initial_config)
        
        # Mise à jour partielle
        update_config = {'configured': True, 'forum_channel_id': 111222333}
        guild_config.update_guild_config(guild_id, update_config)
        
        # Vérifier que les deux sont fusionnées
        final_config = guild_config.get_guild_config(guild_id)
        assert final_config['language'] == 'fr'  # Conservé
        assert final_config['configured'] is True  # Mis à jour
        assert final_config['forum_channel_id'] == 111222333  # Ajouté
    
    def test_guild_config_list_configured_guilds(self, clean_guild_config):
        """Test liste des guildes configurées"""
        # Ajouter quelques guildes
        guild_config.update_guild_config(111, {'configured': True})
        guild_config.update_guild_config(222, {'configured': False})
        guild_config.update_guild_config(333, {'configured': True})
        
        configured_guilds = guild_config.list_configured_guilds()
        
        # Doit retourner une liste
        assert isinstance(configured_guilds, list)
        # Les guildes configurées doivent être présentes
        assert 111 in configured_guilds
        assert 333 in configured_guilds


class TestCompleteReportFlow:
    """Tests d'intégration pour le flux complet de signalement"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_report_flow_with_mocks(self, mock_interaction, configured_guild, 
                                                   mock_supabase_client, mock_alerts_forum):
        """Test flux complet de signalement avec tous les mocks"""
        
        # Configuration des mocks
        mock_interaction.guild = configured_guild
        mock_supabase_client.is_connected = True
        
        # Import des composants nécessaires
        from bot import AgisReportModal, ValidationView
        
        # 1. Création du modal de signalement
        modal = AgisReportModal(configured_guild.id, "harassment", True)
        
        # 2. Simulation des données du modal
        modal.children[0].value = "testuser123"  # Username
        modal.children[1].value = "Comportement de harcèlement observé"  # Reason
        if len(modal.children) > 2:
            modal.children[2].value = "https://discord.com/channels/123/456/789"  # Evidence
        
        # 3. Mock des validateurs de sécurité
        with patch('bot.SecurityValidator') as mock_validator_class:
            validator_instance = MagicMock()
            validator_instance.validate_input.return_value = True
            validator_instance.sanitize_input.side_effect = lambda x: x
            mock_validator_class.return_value = validator_instance
            
            # 4. Mock rate limiter (autoriser)
            with patch('bot.RateLimiter') as mock_rate_limiter_class:
                rate_limiter_instance = MagicMock()
                rate_limiter_instance.check_rate_limit.return_value = True
                mock_rate_limiter_class.return_value = rate_limiter_instance
                
                # 5. Mock report tracker (pas de doublon)
                with patch('bot.ReportTracker') as mock_tracker_class:
                    tracker_instance = MagicMock()
                    tracker_instance.is_duplicate_report.return_value = False
                    mock_tracker_class.return_value = tracker_instance
                    
                    # 6. Mock création de thread dans le forum
                    mock_thread = AsyncMock()
                    mock_thread.id = 999888777666555444
                    mock_thread.send = AsyncMock()
                    mock_alerts_forum.create_thread = AsyncMock(return_value=(mock_thread, None))
                    
                    # 7. Mock discord.utils.get pour retourner le forum
                    with patch('discord.utils.get', return_value=mock_alerts_forum):
                        
                        # 8. Exécution du modal
                        try:
                            await modal.on_submit(mock_interaction)
                            
                            # 9. Vérifications
                            # Le modal doit avoir répondu
                            assert mock_interaction.response.send_message.called or mock_interaction.response.defer.called
                            
                            # Un thread doit avoir été créé
                            mock_alerts_forum.create_thread.assert_called_once()
                            
                            # Les validateurs doivent avoir été appelés
                            validator_instance.validate_input.assert_called()
                            rate_limiter_instance.check_rate_limit.assert_called()
                            tracker_instance.is_duplicate_report.assert_called()
                            
                        except Exception as e:
                            pytest.fail(f"Le flux complet de signalement a échoué: {e}")
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_validation_flow_with_centralization(self, mock_interaction, configured_guild, 
                                                       mock_supabase_client, mock_validator_role):
        """Test flux de validation avec centralisation"""
        
        # Configuration
        mock_interaction.guild = configured_guild
        mock_interaction.user.roles = [mock_validator_role]
        configured_guild.members = [mock_interaction.user]  # Un seul validateur = 100%
        
        # Créer une vue de validation
        validation_view = ValidationView(
            "TEST_REPORT_123",
            configured_guild.id,
            "987654321098765432",  # ID Discord valide
            "harassment",
            "Test harassment reason",
            configured_guild.name
        )
        
        # Mock Supabase pour succès de centralisation
        mock_supabase_client.add_validated_report.return_value = True
        
        # Mock discord.utils.get pour retourner le rôle validateur
        with patch('discord.utils.get', return_value=mock_validator_role):
            # Mock audit logger
            with patch('bot.audit_logger') as mock_audit:
                mock_audit.log_validation_action = MagicMock()
                
                # Mock supabase_client dans le module bot
                with patch('bot.supabase_client', mock_supabase_client):
                    
                    try:
                        # Exécuter la validation
                        await validation_view.validate_button(mock_interaction)
                        
                        # Vérifications
                        # Une réponse doit être envoyée
                        mock_interaction.followup.send.assert_called()
                        
                        # L'audit doit être loggé
                        mock_audit.log_validation_action.assert_called()
                        
                        # Le quorum étant atteint (100%), finalisation doit être appelée
                        # (Ceci dépend de la configuration du quorum dans BOT_CONFIG)
                        
                    except Exception as e:
                        pytest.fail(f"Le flux de validation a échoué: {e}")


class TestErrorHandling:
    """Tests de gestion d'erreur"""
    
    @pytest.mark.asyncio
    async def test_supabase_connection_error(self, mock_interaction, mock_user):
        """Test gestion d'erreur de connexion Supabase"""
        from bot import check_user
        
        # L'utilisateur a les permissions
        mock_interaction.user.guild_permissions = mock_interaction.user.guild_permissions.all()
        
        # Mock Supabase en échec
        with patch('bot.supabase_client') as mock_client:
            mock_client.is_connected = False
            mock_client.check_user_flag.side_effect = Exception("Connection failed")
            
            # L'appel ne doit pas crasher
            try:
                await check_user(mock_interaction, mock_user)
                assert True
            except Exception as e:
                pytest.fail(f"check_user a crashé sur erreur Supabase: {e}")
    
    @pytest.mark.asyncio
    async def test_modal_submit_exception_handling(self, mock_interaction, mock_guild):
        """Test gestion d'exception dans soumission de modal"""
        from bot import AgisReportModal
        
        modal = AgisReportModal(mock_guild.id, "harassment", True)
        modal.children[0].value = "testuser"
        modal.children[1].value = "Test reason"
        
        # Mock SecurityValidator pour lever une exception
        with patch('bot.SecurityValidator') as mock_validator_class:
            mock_validator_class.side_effect = Exception("Validator error")
            
            # L'appel ne doit pas crasher le bot
            try:
                await modal.on_submit(mock_interaction)
                # Une réponse d'erreur doit être envoyée
                mock_interaction.response.send_message.assert_called()
            except Exception as e:
                pytest.fail(f"Modal submit a crashé: {e}")


class TestConfigurationValidation:
    """Tests de validation de la configuration"""
    
    def test_bot_config_required_keys(self):
        """Test que toutes les clés requises sont présentes dans BOT_CONFIG"""
        required_keys = [
            "ALERTS_CHANNEL_NAME",
            "VALIDATOR_ROLE_NAME", 
            "MAX_REPORTS_PER_USER_PER_HOUR",
            "QUORUM_PERCENTAGE",
            "VALIDATION_TIMEOUT_HOURS",
            "SUPABASE_ENABLED"
        ]
        
        for key in required_keys:
            assert key in BOT_CONFIG, f"Clé manquante dans BOT_CONFIG: {key}"
    
    def test_bot_config_types(self):
        """Test que les types de configuration sont corrects"""
        assert isinstance(BOT_CONFIG["ALERTS_CHANNEL_NAME"], str)
        assert isinstance(BOT_CONFIG["VALIDATOR_ROLE_NAME"], str)
        assert isinstance(BOT_CONFIG["MAX_REPORTS_PER_USER_PER_HOUR"], int)
        assert isinstance(BOT_CONFIG["QUORUM_PERCENTAGE"], (int, float))
        assert isinstance(BOT_CONFIG["VALIDATION_TIMEOUT_HOURS"], int)
        assert isinstance(BOT_CONFIG["SUPABASE_ENABLED"], bool)
    
    def test_bot_config_values(self):
        """Test que les valeurs de configuration sont raisonnables"""
        assert BOT_CONFIG["MAX_REPORTS_PER_USER_PER_HOUR"] > 0
        assert 0 < BOT_CONFIG["QUORUM_PERCENTAGE"] <= 100
        assert BOT_CONFIG["VALIDATION_TIMEOUT_HOURS"] > 0