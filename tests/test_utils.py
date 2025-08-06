"""
Tests simplifiés pour les utilitaires - uniquement ce qui existe réellement
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
import os

# Import des utilitaires à tester
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import SecurityValidator, create_secure_embed
from translations import translator
import discord


class TestSecurityValidator:
    """Tests pour SecurityValidator avec méthodes réelles"""
    
    def test_sanitize_input_normal(self):
        """Test sanitisation d'un texte normal"""
        result = SecurityValidator.sanitize_input("Texte normal")
        assert result == "Texte normal"
        assert isinstance(result, str)
    
    def test_sanitize_input_with_control_chars(self):
        """Test sanitisation avec caractères de contrôle"""
        result = SecurityValidator.sanitize_input("Texte\x00avec\x1fcontrôle")
        assert "Texte" in result
        assert "\x00" not in result
        assert "\x1f" not in result
    
    def test_sanitize_input_with_mentions(self):
        """Test sanitisation des mentions dangereuses"""
        result = SecurityValidator.sanitize_input("@everyone regardez ça @here")
        assert "@everyone" not in result
        assert "@here" not in result
        assert "@\u200beveryone" in result
        assert "@\u200bhere" in result
    
    def test_sanitize_input_max_length(self):
        """Test limitation de longueur"""
        long_text = "a" * 2000
        result = SecurityValidator.sanitize_input(long_text, max_length=500)
        assert len(result) <= 500
    
    def test_validate_discord_id_valid(self):
        """Test validation ID Discord valide"""
        valid_id = "123456789012345678"  # 18 chiffres
        assert SecurityValidator.validate_discord_id(valid_id) is True
    
    def test_validate_discord_id_invalid(self):
        """Test validation ID Discord invalide"""
        assert SecurityValidator.validate_discord_id("123") is False
        assert SecurityValidator.validate_discord_id("abc123") is False
        assert SecurityValidator.validate_discord_id("") is False
    
    def test_validate_username_valid(self):
        """Test validation nom d'utilisateur valide"""
        assert SecurityValidator.validate_username("normaluser") is True
        assert SecurityValidator.validate_username("user123") is True
    
    def test_validate_username_empty(self):
        """Test validation nom d'utilisateur vide"""
        assert SecurityValidator.validate_username("") is False
        assert SecurityValidator.validate_username(None) is False
    
    def test_validate_username_too_long(self):
        """Test validation nom d'utilisateur trop long"""
        long_username = "a" * 150
        assert SecurityValidator.validate_username(long_username) is False


class TestUtilityFunctions:
    """Tests pour les fonctions utilitaires"""
    
    def test_create_secure_embed_basic(self):
        """Test création d'embed basique"""
        embed = create_secure_embed("Test Title", "Test Description", discord.Color.blue())
        
        assert isinstance(embed, discord.Embed)
        assert embed.title == "Test Title"
        assert embed.description == "Test Description"
        assert embed.color == discord.Color.blue()
    
    def test_create_secure_embed_empty_strings(self):
        """Test création d'embed avec chaînes vides"""
        embed = create_secure_embed("", "", discord.Color.red())
        
        assert isinstance(embed, discord.Embed)
        assert embed.title == ""
        assert embed.description == ""


class TestTranslationIntegration:
    """Tests d'intégration avec le système de traductions"""
    
    def test_sanitize_translated_text(self):
        """Test sanitisation de texte traduit"""
        french_text = translator.t("report_modal_title", language="fr")
        english_text = translator.t("report_modal_title", language="en")
        
        # Les textes traduits doivent pouvoir être sanitisés
        french_sanitized = SecurityValidator.sanitize_input(french_text)
        english_sanitized = SecurityValidator.sanitize_input(english_text)
        
        assert isinstance(french_sanitized, str)
        assert isinstance(english_sanitized, str)
        assert len(french_sanitized) > 0
        assert len(english_sanitized) > 0
    
    def test_create_embed_with_translations(self):
        """Test création d'embed avec texte traduit"""
        title = translator.t("report_modal_title", language="fr")
        description = translator.t("report_modal_description", language="fr")
        
        embed = create_secure_embed(title, description, discord.Color.green())
        
        assert isinstance(embed, discord.Embed)
        assert embed.title == title
        assert embed.description == description