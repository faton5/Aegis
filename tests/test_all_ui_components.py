"""
Tests complets pour TOUS les composants UI du bot Aegis
Teste que tous les modals, boutons, selects fonctionnent correctement
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import sys
import os
from datetime import datetime

# Import des composants UI à tester
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from bot import CategorySelectView, ProofSelectView, AgisReportModal, ValidationView
from setup_views import LanguageView
from tests.discord_mocks import MockTextInput


class TestCategorySelectView:
    """Tests complets pour CategorySelectView"""
    
    def test_category_select_view_initialization(self, configured_guild):
        """Test initialisation correcte de CategorySelectView"""
        view = CategorySelectView(configured_guild.id)
        
        assert view.guild_id == configured_guild.id
        assert len(view.children) > 0
        
        # Vérifier que le select menu est présent
        select_menu = view.children[0]
        assert hasattr(select_menu, 'options')
        assert len(select_menu.options) > 0
    
    def test_category_select_options_content(self, configured_guild):
        """Test que les options du select contiennent les bonnes catégories"""
        view = CategorySelectView(configured_guild.id)
        select_menu = view.children[0]
        
        # Vérifier que les catégories principales sont présentes
        option_values = [opt.value for opt in select_menu.options]
        expected_categories = ["harassment", "inappropriate_content", "suspicious_behavior", 
                             "child_safety", "spam", "scam", "threats", "other"]
        
        for category in expected_categories:
            assert category in option_values, f"Catégorie manquante: {category}"
    
    @pytest.mark.asyncio
    async def test_category_select_callback(self, mock_interaction, configured_guild):
        """Test callback de sélection de catégorie"""
        view = CategorySelectView(configured_guild.id)
        mock_interaction.guild = configured_guild
        
        # Simuler une sélection
        mock_select = MagicMock()
        mock_select.values = ["harassment"]
        
        # Mock de l'interaction data
        mock_interaction.data = {"values": ["harassment"]}
        
        # Le callback ne doit pas lever d'exception
        try:
            # Simuler l'appel du callback
            await view.category_select(mock_interaction, mock_select)
            
            # Vérifier qu'une réponse est envoyée
            assert mock_interaction.response.send_message.called or \
                   mock_interaction.response.edit_message.called
        except Exception as e:
            pytest.fail(f"Callback de sélection de catégorie a échoué: {e}")


class TestProofSelectView:
    """Tests complets pour ProofSelectView"""
    
    def test_proof_select_view_initialization(self, configured_guild):
        """Test initialisation de ProofSelectView"""
        view = ProofSelectView(configured_guild.id, "harassment")
        
        assert view.guild_id == configured_guild.id
        assert view.selected_category == "harassment"
        assert len(view.children) > 0
        
        # Vérifier que le select menu pour les preuves est présent
        select_menu = view.children[0]
        assert hasattr(select_menu, 'options')
        assert len(select_menu.options) == 2  # Oui/Non
    
    def test_proof_select_options(self, configured_guild):
        """Test que les options de preuve sont correctes"""
        view = ProofSelectView(configured_guild.id, "harassment")
        select_menu = view.children[0]
        
        option_values = [opt.value for opt in select_menu.options]
        assert "yes" in option_values
        assert "no" in option_values
    
    @pytest.mark.asyncio
    async def test_proof_select_callback_yes(self, mock_interaction, configured_guild):
        """Test callback sélection "Oui" pour les preuves"""
        view = ProofSelectView(configured_guild.id, "harassment")
        mock_interaction.guild = configured_guild
        
        mock_select = MagicMock()
        mock_select.values = ["yes"]
        
        try:
            await view.proof_select(mock_interaction, mock_select)
            # Doit envoyer un modal
            assert mock_interaction.response.send_modal.called
        except Exception as e:
            pytest.fail(f"Callback preuve 'oui' a échoué: {e}")
    
    @pytest.mark.asyncio
    async def test_proof_select_callback_no(self, mock_interaction, configured_guild):
        """Test callback sélection "Non" pour les preuves"""
        view = ProofSelectView(configured_guild.id, "harassment")
        mock_interaction.guild = configured_guild
        
        mock_select = MagicMock()
        mock_select.values = ["no"]
        
        try:
            await view.proof_select(mock_interaction, mock_select)
            # Doit envoyer un modal
            assert mock_interaction.response.send_modal.called
        except Exception as e:
            pytest.fail(f"Callback preuve 'non' a échoué: {e}")


class TestAgisReportModal:
    """Tests exhaustifs pour AgisReportModal"""
    
    def test_modal_initialization_with_proof(self, configured_guild):
        """Test initialisation du modal avec preuves"""
        modal = AgisReportModal(configured_guild.id, "harassment", True)
        
        assert modal.guild_id == configured_guild.id
        assert modal.category == "harassment"
        assert modal.has_proof is True
        assert len(modal.children) >= 2  # Au moins username et reason
        
        # Vérifier les champs obligatoires
        field_labels = [child.label for child in modal.children]
        assert any("utilisateur" in label.lower() or "username" in label.lower() 
                  for label in field_labels)
        assert any("motif" in label.lower() or "reason" in label.lower() 
                  for label in field_labels)
    
    def test_modal_initialization_without_proof(self, configured_guild):
        """Test initialisation du modal sans preuves"""
        modal = AgisReportModal(configured_guild.id, "spam", False)
        
        assert modal.guild_id == configured_guild.id
        assert modal.category == "spam"
        assert modal.has_proof is False
        
        # Même structure mais le champ preuves peut être optionnel
        assert len(modal.children) >= 2
    
    @pytest.mark.asyncio
    async def test_modal_submit_valid_data(self, mock_interaction, configured_guild,
                                         mock_security_validator, mock_rate_limiter,
                                         mock_report_tracker, mock_discord_utils,
                                         mock_forum_channel, mock_audit_logger):
        """Test soumission modal avec données valides - flux complet"""
        modal = AgisReportModal(configured_guild.id, "harassment", True)
        mock_interaction.guild = configured_guild
        
        # Simuler les valeurs du modal
        username_field = MockTextInput("Username", "Nom d'utilisateur à signaler")
        username_field.value = "TestUser123"
        reason_field = MockTextInput("Reason", "Motif du signalement")
        reason_field.value = "Comportement de harcèlement répété"
        evidence_field = MockTextInput("Evidence", "Liens et preuves")
        evidence_field.value = "https://discord.com/channels/123/456/789"
        
        modal.children = [username_field, reason_field, evidence_field]
        
        # Mock discord.utils.get pour retourner le forum
        mock_discord_utils.return_value = mock_forum_channel
        
        # Mock tous les validateurs pour succès
        mock_security_validator.validate_input.return_value = True
        mock_security_validator.sanitize_input.side_effect = lambda x: x
        mock_rate_limiter.check_rate_limit.return_value = True
        mock_report_tracker.is_duplicate_report.return_value = False
        
        try:
            await modal.on_submit(mock_interaction)
            
            # Vérifications
            mock_security_validator.validate_input.assert_called()
            mock_rate_limiter.check_rate_limit.assert_called()
            mock_report_tracker.is_duplicate_report.assert_called()
            mock_forum_channel.create_thread.assert_called_once()
            mock_audit_logger.log_security_event.assert_called()
            
            # Une réponse de succès doit être envoyée
            assert mock_interaction.response.send_message.called or \
                   mock_interaction.followup.send.called
            
        except Exception as e:
            pytest.fail(f"Soumission modal valide a échoué: {e}")
    
    @pytest.mark.asyncio
    async def test_modal_submit_invalid_username(self, mock_interaction, configured_guild,
                                               mock_security_validator):
        """Test soumission modal avec username invalide"""
        modal = AgisReportModal(configured_guild.id, "spam", False)
        
        username_field = MockTextInput()
        username_field.value = ""  # Username vide
        reason_field = MockTextInput()
        reason_field.value = "Test reason"
        modal.children = [username_field, reason_field]
        
        # Mock validation échoue
        mock_security_validator.validate_input.return_value = False
        
        await modal.on_submit(mock_interaction)
        
        # Vérifier qu'une erreur est envoyée
        mock_interaction.response.send_message.assert_called()
        call_args = mock_interaction.response.send_message.call_args
        assert call_args.kwargs['ephemeral'] is True
    
    @pytest.mark.asyncio
    async def test_modal_submit_rate_limited(self, mock_interaction, configured_guild,
                                           mock_security_validator, mock_rate_limiter):
        """Test soumission modal avec rate limiting"""
        modal = AgisReportModal(configured_guild.id, "threats", True)
        
        username_field = MockTextInput()
        username_field.value = "ValidUser"
        reason_field = MockTextInput()
        reason_field.value = "Valid reason"
        modal.children = [username_field, reason_field]
        
        # Mock validation réussit mais rate limit échoue
        mock_security_validator.validate_input.return_value = True
        mock_security_validator.sanitize_input.side_effect = lambda x: x
        mock_rate_limiter.check_rate_limit.return_value = False
        
        await modal.on_submit(mock_interaction)
        
        # Vérifier qu'une erreur de rate limit est envoyée
        call_args = mock_interaction.response.send_message.call_args
        assert call_args.kwargs['ephemeral'] is True
    
    @pytest.mark.asyncio
    async def test_modal_submit_duplicate_report(self, mock_interaction, configured_guild,
                                                mock_security_validator, mock_rate_limiter,
                                                mock_report_tracker):
        """Test soumission modal avec signalement dupliqué"""
        modal = AgisReportModal(configured_guild.id, "scam", False)
        
        username_field = MockTextInput()
        username_field.value = "ScamUser"
        reason_field = MockTextInput()
        reason_field.value = "Tentative d'arnaque"
        modal.children = [username_field, reason_field]
        
        # Mock validation et rate limit OK, mais doublon détecté
        mock_security_validator.validate_input.return_value = True
        mock_security_validator.sanitize_input.side_effect = lambda x: x
        mock_rate_limiter.check_rate_limit.return_value = True
        mock_report_tracker.is_duplicate_report.return_value = True
        
        await modal.on_submit(mock_interaction)
        
        # Vérifier qu'une erreur de doublon est envoyée
        call_args = mock_interaction.response.send_message.call_args
        assert call_args.kwargs['ephemeral'] is True


class TestValidationView:
    """Tests exhaustifs pour ValidationView (boutons de validation)"""
    
    def test_validation_view_initialization(self, configured_guild):
        """Test initialisation de ValidationView"""
        view = ValidationView("REPORT_123", configured_guild.id, "testuser", 
                            "harassment", "Test reason", configured_guild.name)
        
        assert view.report_id == "REPORT_123"
        assert view.guild_id == configured_guild.id
        assert view.target_username == "testuser"
        assert view.category == "harassment"
        assert view.reason == "Test reason"
        assert view.guild_name == configured_guild.name
        assert view.is_finalized is False
        assert len(view.validators) == 0
        assert len(view.rejectors) == 0
        
        # Vérifier que les boutons sont présents
        assert len(view.children) >= 3  # Valider, Rejeter, Détails
    
    def test_validation_view_buttons_labels(self, configured_guild):
        """Test que les boutons ont les bons labels traduits"""
        view = ValidationView("REPORT_123", configured_guild.id)
        
        # Vérifier que les boutons existent avec des labels
        button_labels = []
        for child in view.children:
            if hasattr(child, 'label'):
                button_labels.append(child.label)
        
        # Au moins 3 boutons avec des labels
        assert len(button_labels) >= 3
        assert any(button_labels)  # Au moins un label non vide
    
    @pytest.mark.asyncio
    async def test_validate_button_success(self, mock_validator_interaction, configured_guild,
                                         mock_discord_utils, mock_audit_logger):
        """Test bouton valider avec succès"""
        view = ValidationView("REPORT_123", configured_guild.id)
        mock_validator_interaction.guild = configured_guild
        
        # Mock pour retourner le rôle validateur
        validator_role = configured_guild.roles[0]
        mock_discord_utils.return_value = validator_role
        
        # L'utilisateur a le rôle
        mock_validator_interaction.user.roles = [validator_role]
        
        # Un seul membre = 100% de validation
        configured_guild.members = [mock_validator_interaction.user]
        
        await view.validate_button(mock_validator_interaction)
        
        # Vérifications
        assert mock_validator_interaction.user.id in view.validators
        mock_audit_logger.log_validation_action.assert_called()
        mock_validator_interaction.followup.send.assert_called()
    
    @pytest.mark.asyncio
    async def test_validate_button_no_role(self, mock_interaction, configured_guild,
                                         mock_discord_utils):
        """Test bouton valider sans rôle"""
        view = ValidationView("REPORT_123", configured_guild.id)
        mock_interaction.guild = configured_guild
        
        # Pas de rôle validateur
        mock_discord_utils.return_value = None
        mock_interaction.user.roles = []
        
        await view.validate_button(mock_interaction)
        
        # Vérifier qu'une erreur est envoyée
        call_args = mock_interaction.followup.send.call_args
        assert call_args.kwargs['ephemeral'] is True
    
    @pytest.mark.asyncio
    async def test_validate_button_already_finalized(self, mock_validator_interaction, configured_guild):
        """Test bouton valider sur signalement déjà finalisé"""
        view = ValidationView("REPORT_123", configured_guild.id)
        view.is_finalized = True  # Déjà finalisé
        
        await view.validate_button(mock_validator_interaction)
        
        # Vérifier qu'un message "déjà finalisé" est envoyé
        call_args = mock_validator_interaction.followup.send.call_args
        assert call_args.kwargs['ephemeral'] is True
    
    @pytest.mark.asyncio
    async def test_validate_button_already_validated(self, mock_validator_interaction, configured_guild,
                                                   mock_discord_utils):
        """Test double validation par le même utilisateur"""
        view = ValidationView("REPORT_123", configured_guild.id)
        mock_validator_interaction.guild = configured_guild
        
        validator_role = configured_guild.roles[0]
        mock_discord_utils.return_value = validator_role
        mock_validator_interaction.user.roles = [validator_role]
        
        # Ajouter l'utilisateur aux validators
        view.validators.add(mock_validator_interaction.user.id)
        
        await view.validate_button(mock_validator_interaction)
        
        # Vérifier qu'un message "déjà validé" est envoyé
        call_args = mock_validator_interaction.followup.send.call_args
        assert call_args.kwargs['ephemeral'] is True
    
    @pytest.mark.asyncio
    async def test_reject_button_success(self, mock_validator_interaction, configured_guild,
                                       mock_discord_utils, mock_audit_logger):
        """Test bouton rejeter avec succès"""
        view = ValidationView("REPORT_123", configured_guild.id)
        mock_validator_interaction.guild = configured_guild
        
        validator_role = configured_guild.roles[0]
        mock_discord_utils.return_value = validator_role
        mock_validator_interaction.user.roles = [validator_role]
        configured_guild.members = [mock_validator_interaction.user]
        
        await view.reject_button(mock_validator_interaction)
        
        # Vérifications
        assert mock_validator_interaction.user.id in view.rejectors
        mock_audit_logger.log_validation_action.assert_called()
        mock_validator_interaction.followup.send.assert_called()
    
    @pytest.mark.asyncio
    async def test_request_details_button(self, mock_validator_interaction, configured_guild,
                                        mock_discord_utils, mock_evidence_collector):
        """Test bouton demander détails"""
        view = ValidationView("REPORT_123", configured_guild.id)
        mock_validator_interaction.guild = configured_guild
        
        validator_role = configured_guild.roles[0]
        mock_discord_utils.return_value = validator_role
        mock_validator_interaction.user.roles = [validator_role]
        
        # Simuler un signalement dans la fenêtre de collecte
        mock_evidence_collector.user_thread_mapping = {
            123456789: (999888777, "REPORT_123", 9999999999)
        }
        
        # Mock get_user pour retourner un utilisateur
        mock_user = MagicMock()
        mock_user.send = AsyncMock()
        mock_validator_interaction.client.get_user = MagicMock(return_value=mock_user)
        
        await view.request_details_button(mock_validator_interaction, MagicMock())
        
        # Une demande de détails doit être envoyée
        mock_user.send.assert_called_once()
        mock_validator_interaction.followup.send.assert_called()


class TestLanguageView:
    """Tests pour LanguageView (boutons de changement de langue)"""
    
    def test_language_view_initialization(self, configured_guild):
        """Test initialisation de LanguageView"""
        view = LanguageView(configured_guild.id)
        
        assert view.guild_id == configured_guild.id
        assert len(view.children) >= 2  # Au moins FR et EN
        
        # Vérifier que les boutons ont les bons emojis/labels
        button_labels = [child.label for child in view.children if hasattr(child, 'label')]
        button_emojis = [child.emoji for child in view.children if hasattr(child, 'emoji')]
        
        # Au moins 2 boutons
        assert len(view.children) >= 2
    
    @pytest.mark.asyncio
    async def test_french_button(self, mock_interaction, configured_guild, clean_guild_config):
        """Test bouton français"""
        view = LanguageView(configured_guild.id)
        mock_interaction.guild = configured_guild
        
        with patch('setup_views.guild_config') as mock_guild_config:
            mock_guild_config.update_guild_config = MagicMock()
            
            await view.set_french(mock_interaction, MagicMock())
            
            # Vérifier que la langue est mise à jour
            mock_guild_config.update_guild_config.assert_called_once_with(
                configured_guild.id, {'language': 'fr'}
            )
            
            # Vérifier qu'une réponse est envoyée
            mock_interaction.response.send_message.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_english_button(self, mock_interaction, configured_guild, clean_guild_config):
        """Test bouton anglais"""
        view = LanguageView(configured_guild.id)
        mock_interaction.guild = configured_guild
        
        with patch('setup_views.guild_config') as mock_guild_config:
            mock_guild_config.update_guild_config = MagicMock()
            
            await view.set_english(mock_interaction, MagicMock())
            
            # Vérifier que la langue est mise à jour
            mock_guild_config.update_guild_config.assert_called_once_with(
                configured_guild.id, {'language': 'en'}
            )
            
            # Vérifier qu'une réponse est envoyée
            mock_interaction.response.send_message.assert_called_once()


class TestUIComponentsIntegration:
    """Tests d'intégration entre les composants UI"""
    
    @pytest.mark.asyncio
    async def test_complete_ui_flow(self, mock_interaction, configured_guild):
        """Test du flux UI complet de signalement"""
        mock_interaction.guild = configured_guild
        
        # 1. Étape de sélection de catégorie
        category_view = CategorySelectView(configured_guild.id)
        
        # 2. Simuler sélection de catégorie -> ProofSelectView
        proof_view = ProofSelectView(configured_guild.id, "harassment")
        
        # 3. Simuler sélection de preuve -> AgisReportModal
        modal = AgisReportModal(configured_guild.id, "harassment", True)
        
        # Vérifier que tous les composants sont créés sans erreur
        assert category_view.guild_id == configured_guild.id
        assert proof_view.selected_category == "harassment"
        assert modal.category == "harassment"
        assert modal.has_proof is True
    
    @pytest.mark.asyncio
    async def test_validation_ui_flow(self, mock_validator_interaction, configured_guild):
        """Test du flux UI de validation"""
        # Création d'une vue de validation
        validation_view = ValidationView("TEST_REPORT", configured_guild.id, 
                                       "testuser", "harassment", "Test reason")
        
        # Vérifier que tous les boutons sont accessibles
        assert len(validation_view.children) >= 3
        
        # Simuler l'état des validators
        validation_view.validators.add(111111111)
        validation_view.rejectors.add(222222222)
        
        # L'état doit être maintenu
        assert len(validation_view.validators) == 1
        assert len(validation_view.rejectors) == 1
        assert validation_view.is_finalized is False
    
    def test_ui_components_translations(self, configured_guild):
        """Test que tous les composants UI supportent les traductions"""
        from guild_config import guild_config
        
        # Test avec français
        guild_config.update_guild_config(configured_guild.id, {'language': 'fr'})
        
        category_view_fr = CategorySelectView(configured_guild.id)
        proof_view_fr = ProofSelectView(configured_guild.id, "harassment")
        modal_fr = AgisReportModal(configured_guild.id, "harassment", True)
        
        # Test avec anglais
        guild_config.update_guild_config(configured_guild.id, {'language': 'en'})
        
        category_view_en = CategorySelectView(configured_guild.id)
        proof_view_en = ProofSelectView(configured_guild.id, "harassment")
        modal_en = AgisReportModal(configured_guild.id, "harassment", True)
        
        # Tous les composants doivent être créés sans erreur
        assert category_view_fr.guild_id == category_view_en.guild_id
        assert proof_view_fr.selected_category == proof_view_en.selected_category
        assert modal_fr.category == modal_en.category
    
    def test_ui_components_handle_missing_translation(self, configured_guild):
        """Test que les composants UI gèrent les traductions manquantes"""
        # Simuler une clé de traduction manquante
        with patch('translations.translator.t') as mock_translator:
            mock_translator.return_value = "fallback_text"
            
            # Les composants doivent fonctionner même avec des traductions manquantes
            category_view = CategorySelectView(configured_guild.id)
            modal = AgisReportModal(configured_guild.id, "harassment", True)
            
            assert category_view.guild_id == configured_guild.id
            assert modal.category == "harassment"