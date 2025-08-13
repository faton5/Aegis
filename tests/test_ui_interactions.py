"""
Tests pour les interactions UI du bot Aegis (modals, boutons, views)
"""
import pytest
import discord
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Import des composants UI à tester
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from bot import CategorySelectView, ProofSelectView, AgisReportModal, ValidationView
from setup_views import LanguageView


class TestCategorySelectView:
    """Tests pour CategorySelectView"""
    
    def test_category_select_view_init(self, mock_guild):
        """Test initialisation de CategorySelectView"""
        view = CategorySelectView(mock_guild.id)
        assert view.guild_id == mock_guild.id
        assert len(view.children) > 0  # Au moins un composant
    
    @pytest.mark.asyncio
    async def test_category_select_callback(self, mock_interaction, mock_guild):
        """Test callback de sélection de catégorie"""
        view = CategorySelectView(mock_guild.id)
        
        # Simuler une sélection
        mock_select = MagicMock()
        mock_select.values = ["harassment"]
        
        # Mock de l'interaction pour le callback
        mock_interaction.data = {"values": ["harassment"]}
        
        # Tester que le callback fonctionne sans erreur
        try:
            await view.category_select(mock_interaction, mock_select)
            # Si on arrive ici, pas d'exception levée
            assert True
        except Exception as e:
            pytest.fail(f"Callback a levé une exception: {e}")


class TestProofSelectView:
    """Tests pour ProofSelectView"""
    
    def test_proof_select_view_init(self, mock_guild):
        """Test initialisation de ProofSelectView"""
        view = ProofSelectView(mock_guild.id, "harassment")
        assert view.guild_id == mock_guild.id
        assert view.selected_category == "harassment"
        assert len(view.children) > 0


class TestAgisReportModal:
    """Tests pour AgisReportModal"""
    
    def test_modal_init(self, mock_guild):
        """Test initialisation du modal"""
        modal = AgisReportModal(mock_guild.id, "harassment", True)
        assert modal.guild_id == mock_guild.id
        assert modal.category == "harassment"
        assert modal.has_proof is True
        assert len(modal.children) >= 2  # Au moins username et reason
    
    @pytest.mark.asyncio
    async def test_modal_submit_invalid_username(self, mock_interaction, mock_guild):
        """Test soumission du modal avec username invalide"""
        modal = AgisReportModal(mock_guild.id, "harassment", True)
        
        # Mock des valeurs du modal
        modal.children[0].value = ""  # Username vide
        modal.children[1].value = "Test reason"  # Reason valide
        
        # Mock SecurityValidator pour retourner invalide
        with patch('bot.SecurityValidator') as mock_validator_class:
            validator_instance = MagicMock()
            validator_instance.validate_input.return_value = False
            mock_validator_class.return_value = validator_instance
            
            await modal.on_submit(mock_interaction)
            
            # Vérifier qu'une réponse d'erreur est envoyée
            mock_interaction.response.send_message.assert_called_once()
            args = mock_interaction.response.send_message.call_args
            assert "ephemeral" in args.kwargs
            assert args.kwargs["ephemeral"] is True
    
    @pytest.mark.asyncio
    async def test_modal_submit_rate_limited(self, mock_interaction, mock_guild):
        """Test soumission du modal avec rate limiting"""
        modal = AgisReportModal(mock_guild.id, "harassment", True)
        
        # Mock des valeurs du modal
        modal.children[0].value = "testuser"
        modal.children[1].value = "Test reason"
        
        # Mock SecurityValidator pour retourner valide
        with patch('bot.SecurityValidator') as mock_validator_class:
            validator_instance = MagicMock()
            validator_instance.validate_input.return_value = True
            validator_instance.sanitize_input.side_effect = lambda x: x
            mock_validator_class.return_value = validator_instance
            
            # Mock RateLimiter pour retourner rate limited
            with patch('bot.RateLimiter') as mock_rate_limiter_class:
                rate_limiter_instance = MagicMock()
                rate_limiter_instance.check_rate_limit.return_value = False
                mock_rate_limiter_class.return_value = rate_limiter_instance
                
                await modal.on_submit(mock_interaction)
                
                # Vérifier qu'une réponse d'erreur de rate limit est envoyée
                mock_interaction.response.send_message.assert_called_once()
                args = mock_interaction.response.send_message.call_args
                assert "ephemeral" in args.kwargs
                assert args.kwargs["ephemeral"] is True


class TestValidationView:
    """Tests pour ValidationView (boutons de validation)"""
    
    def test_validation_view_init(self, mock_guild):
        """Test initialisation de ValidationView"""
        view = ValidationView("REPORT_123", mock_guild.id, "testuser", "harassment", "test reason", "Test Guild")
        assert view.report_id == "REPORT_123"
        assert view.guild_id == mock_guild.id
        assert view.target_username == "testuser"
        assert view.category == "harassment"
        assert view.reason == "test reason"
        assert view.guild_name == "Test Guild"
        assert len(view.children) >= 3  # Au moins valider, rejeter, détails
    
    @pytest.mark.asyncio
    async def test_validate_button_no_role(self, mock_interaction, mock_guild):
        """Test bouton valider sans rôle validateur"""
        view = ValidationView("REPORT_123", mock_guild.id)
        mock_interaction.guild = mock_guild
        mock_interaction.user.roles = []
        
        # Mock discord.utils.get pour ne retourner aucun rôle
        with patch('discord.utils.get', return_value=None):
            await view.validate_button(mock_interaction)
            
            # Vérifier qu'une réponse d'erreur est envoyée
            mock_interaction.followup.send.assert_called_once()
            args = mock_interaction.followup.send.call_args
            assert "ephemeral" in args.kwargs
            assert args.kwargs["ephemeral"] is True
    
    @pytest.mark.asyncio
    async def test_validate_button_already_finalized(self, mock_interaction, mock_guild, mock_validator_role):
        """Test bouton valider sur signalement déjà finalisé"""
        view = ValidationView("REPORT_123", mock_guild.id)
        view.is_finalized = True  # Marquer comme finalisé
        mock_interaction.guild = mock_guild
        mock_interaction.user.roles = [mock_validator_role]
        
        await view.validate_button(mock_interaction)
        
        # Vérifier qu'un message "déjà finalisé" est envoyé
        mock_interaction.followup.send.assert_called_once()
        args = mock_interaction.followup.send.call_args
        assert "ephemeral" in args.kwargs
        assert args.kwargs["ephemeral"] is True
    
    @pytest.mark.asyncio
    async def test_reject_button_success(self, mock_interaction, mock_guild, mock_validator_role):
        """Test bouton rejeter avec succès"""
        view = ValidationView("REPORT_123", mock_guild.id)
        mock_interaction.guild = mock_guild
        mock_interaction.user.roles = [mock_validator_role]
        mock_guild.members = [mock_interaction.user]  # Un seul validateur
        
        with patch('discord.utils.get', return_value=mock_validator_role):
            await view.reject_button(mock_interaction)
            
            # Vérifier qu'une réponse est envoyée
            mock_interaction.followup.send.assert_called_once()
            args = mock_interaction.followup.send.call_args
            assert "ephemeral" in args.kwargs
            assert args.kwargs["ephemeral"] is True


class TestLanguageView:
    """Tests pour LanguageView (boutons de changement de langue)"""
    
    def test_language_button_view_init(self, mock_guild):
        """Test initialisation de LanguageView"""
        view = LanguageView(mock_guild.id)
        assert view.guild_id == mock_guild.id
        assert len(view.children) >= 2  # Au moins boutons FR et EN
    
    @pytest.mark.asyncio
    async def test_french_button(self, mock_interaction, mock_guild):
        """Test bouton français"""
        view = LanguageView(mock_guild.id)
        mock_interaction.guild = mock_guild
        
        with patch('setup_views.guild_config') as mock_guild_config:
            mock_guild_config.update_guild_config = MagicMock()
            
            await view.french_button(mock_interaction, MagicMock())
            
            # Vérifier que la langue est mise à jour
            mock_guild_config.update_guild_config.assert_called_once_with(
                mock_guild.id, {'language': 'fr'}
            )
            
            # Vérifier qu'une réponse est envoyée
            mock_interaction.response.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_english_button(self, mock_interaction, mock_guild):
        """Test bouton anglais"""
        view = LanguageView(mock_guild.id)
        mock_interaction.guild = mock_guild
        
        with patch('setup_views.guild_config') as mock_guild_config:
            mock_guild_config.update_guild_config = MagicMock()
            
            await view.english_button(mock_interaction, MagicMock())
            
            # Vérifier que la langue est mise à jour
            mock_guild_config.update_guild_config.assert_called_once_with(
                mock_guild.id, {'language': 'en'}
            )
            
            # Vérifier qu'une réponse est envoyée
            mock_interaction.response.send_message.assert_called_once()


class TestUIInteractionsIntegration:
    """Tests d'intégration pour les interactions UI"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_report_flow_mock(self, mock_interaction, configured_guild, mock_alerts_forum):
        """Test du flux complet de signalement (mocké)"""
        # 1. Étape de sélection de catégorie
        category_view = CategorySelectView(configured_guild.id)
        
        # 2. Simuler sélection de catégorie
        mock_select = MagicMock()
        mock_select.values = ["harassment"]
        
        # Mock l'interaction pour le callback
        mock_interaction.data = {"values": ["harassment"]}
        
        # 3. Test que le flow ne lève pas d'exception
        try:
            # Cette partie testera la logique sans vraiment envoyer de messages
            proof_view = ProofSelectView(configured_guild.id, "harassment")
            modal = AgisReportModal(configured_guild.id, "harassment", True)
            
            # Si on arrive ici, les objets sont créés correctement
            assert category_view.guild_id == configured_guild.id
            assert proof_view.selected_category == "harassment"
            assert modal.category == "harassment"
            
        except Exception as e:
            pytest.fail(f"Le flux de signalement a échoué: {e}")
    
    @pytest.mark.asyncio
    async def test_validation_flow_mock(self, mock_interaction, configured_guild):
        """Test du flux de validation (mocké)"""
        # Créer une vue de validation
        validation_view = ValidationView(
            "TEST_REPORT_123", 
            configured_guild.id,
            "testuser",
            "harassment", 
            "Test reason",
            configured_guild.name
        )
        
        # Vérifier que tous les boutons sont présents
        assert len(validation_view.children) >= 3
        
        # Vérifier que l'objet est bien initialisé
        assert validation_view.report_id == "TEST_REPORT_123"
        assert validation_view.is_finalized is False
        assert len(validation_view.validators) == 0
        assert len(validation_view.rejectors) == 0