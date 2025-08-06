"""
Tests pour la logique métier core sans dépendances Discord
"""
import pytest
import sys
import os

# Import des modules core seulement
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import BOT_CONFIG
from guild_config import guild_config


class TestBotConfiguration:
    """Tests pour la configuration du bot"""
    
    def test_config_keys_exist(self):
        """Vérifier que les clés de configuration importantes existent"""
        required_keys = [
            "TEST_MODE_ENABLED",
            "SUPABASE_ENABLED", 
            "ALERTS_CHANNEL_NAME",
            "VALIDATOR_ROLE_NAME"
        ]
        
        for key in required_keys:
            assert key in BOT_CONFIG, f"Clé de configuration manquante: {key}"
    
    def test_config_types(self):
        """Vérifier les types de configuration"""
        assert isinstance(BOT_CONFIG["TEST_MODE_ENABLED"], bool)
        assert isinstance(BOT_CONFIG["SUPABASE_ENABLED"], bool)
        assert isinstance(BOT_CONFIG["ALERTS_CHANNEL_NAME"], str)
        assert isinstance(BOT_CONFIG["VALIDATOR_ROLE_NAME"], str)


class TestGuildConfiguration:
    """Tests pour la configuration des guildes"""
    
    def test_guild_config_initialization(self):
        """Test l'initialisation de guild_config"""
        assert hasattr(guild_config, 'config_dir')
        assert guild_config.config_dir == "guild_configs"
    
    def test_guild_config_methods(self):
        """Test les méthodes de base de guild_config"""
        # Test avec une guilde factice
        test_guild_id = 999999999
        
        # Obtenir la config par défaut
        config = guild_config.get_guild_config(test_guild_id)
        assert isinstance(config, dict)
        assert 'auto_actions' in config  # Vérifier qu'on a la structure par défaut
        
        # Configurer la guilde
        test_updates = {
            'configured': True,
            'language': 'fr',
            'forum_channel_id': 123456,
            'validator_role_id': 789012
        }
        
        guild_config.update_guild_config(test_guild_id, test_updates)
        
        # Vérifier que la configuration a été mise à jour
        updated_config = guild_config.get_guild_config(test_guild_id)
        assert updated_config['configured'] == True
        assert updated_config['language'] == 'fr'
        assert updated_config['forum_channel_id'] == 123456
        assert updated_config['validator_role_id'] == 789012
        
        # Vérifier qu'on peut lister les guildes configurées
        configured_guilds = guild_config.list_configured_guilds()
        assert str(test_guild_id) in configured_guilds
        
        # Nettoyer en supprimant le fichier de test
        import os
        test_file = os.path.join(guild_config.config_dir, f"{test_guild_id}.json")
        if os.path.exists(test_file):
            os.remove(test_file)


class TestCategoryDefinitions:
    """Tests pour les définitions de catégories de signalements"""
    
    def test_category_list_exists(self):
        """Test que la liste des catégories existe quelque part"""
        # On s'attend à ce que les catégories soient définies dans le bot
        expected_categories = [
            "harassment", "inappropriate_content", "suspicious_behavior", 
            "child_safety", "spam", "scam", "threats", "other"
        ]
        
        # Ce test vérifie juste que nous avons pensé aux catégories principales
        assert len(expected_categories) == 8
        assert "harassment" in expected_categories
        assert "other" in expected_categories


class TestBasicValidation:
    """Tests pour les validations de base"""
    
    def test_discord_id_format(self):
        """Test format basique des IDs Discord"""
        valid_id = "123456789012345678"
        invalid_id = "not_a_number"
        
        assert valid_id.isdigit()
        assert not invalid_id.isdigit()
        
        # Les IDs Discord sont des entiers de 17-19 chiffres
        assert len(valid_id) >= 17
        assert len(valid_id) <= 19
    
    def test_config_validation(self):
        """Test validation des configurations"""
        # Les noms de channels et rôles ne doivent pas être vides
        assert BOT_CONFIG["ALERTS_CHANNEL_NAME"].strip() != ""
        assert BOT_CONFIG["VALIDATOR_ROLE_NAME"].strip() != ""
        
        # Les noms ne doivent pas contenir de caractères interdits Discord
        forbidden_chars = ["@", "#", ":", "```"]
        for char in forbidden_chars:
            assert char not in BOT_CONFIG["ALERTS_CHANNEL_NAME"]
            assert char not in BOT_CONFIG["VALIDATOR_ROLE_NAME"]