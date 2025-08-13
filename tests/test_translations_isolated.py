"""
Test isolé pour le système de traduction sans dépendances Discord
"""
import pytest
import sys
import os

# Import du système de traduction uniquement
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from translations import translator


class TestTranslationSystemIsolated:
    """Tests isolés pour le système de traduction"""
    
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

    def test_basic_string_operations(self):
        """Test basique pour vérifier que pytest fonctionne"""
        assert "aegis".upper() == "AEGIS"
        assert len("test") == 4