"""
Configuration pytest pour les tests Aegis avec mocks Discord personnalisés
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import os
import sys

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import des mocks Discord personnalisés
from tests.discord_mocks import (
    MockUser, MockGuild, MockChannel, MockForumChannel, MockThread,
    MockInteraction, MockBot, MockRole, create_configured_guild,
    create_test_interaction, mock_discord_utils_get
)

# Import des modules du bot
from config import BOT_CONFIG
from translations import translator
from utils import SecurityValidator, RateLimiter, AuditLogger
from guild_config import guild_config


@pytest.fixture
def event_loop():
    """Fixture pour la boucle d'événements asyncio"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_user():
    """Mock d'un utilisateur Discord"""
    return MockUser(987654321, "testuser", "Test User")


@pytest.fixture
def mock_admin_user():
    """Mock d'un utilisateur administrateur"""
    user = MockUser(111111111, "admin", "Admin User")
    import discord
    user.guild_permissions = discord.Permissions.all()
    return user


@pytest.fixture
def mock_validator_user():
    """Mock d'un utilisateur validateur"""
    user = MockUser(222222222, "validator", "Validator User")
    return user


@pytest.fixture
def mock_guild():
    """Mock d'une guilde Discord basique"""
    return MockGuild(987654321, "Test Guild")


@pytest.fixture
def configured_guild():
    """Mock d'une guilde entièrement configurée"""
    guild = create_configured_guild()
    
    # Configurer dans guild_config
    guild_config.update_guild_config(guild.id, {
        'configured': True,
        'language': 'fr',
        'forum_channel_id': guild.channels[0].id,  # Forum d'alertes
        'validator_role_id': guild.roles[0].id      # Rôle validateur
    })
    
    return guild


@pytest.fixture
def mock_channel():
    """Mock d'un canal Discord"""
    return MockChannel(111222333, "test-channel")


@pytest.fixture
def mock_forum_channel():
    """Mock d'un canal forum Discord"""
    forum = MockForumChannel(444555666, "agis-alerts")
    forum.create_thread = AsyncMock()
    
    # Mock pour create_thread qui retourne un thread
    async def create_thread_side_effect(name, content=None, **kwargs):
        thread = MockThread(999888777, name)
        thread.parent = forum
        return (thread, None)
    
    forum.create_thread.side_effect = create_thread_side_effect
    return forum


@pytest.fixture
def mock_validator_role():
    """Mock du rôle Validateur"""
    return MockRole(777888999, BOT_CONFIG["VALIDATOR_ROLE_NAME"])


@pytest.fixture
def mock_interaction(mock_user, configured_guild):
    """Mock d'une interaction Discord"""
    interaction = create_test_interaction(mock_user, configured_guild)
    return interaction


@pytest.fixture
def mock_admin_interaction(mock_admin_user, configured_guild):
    """Mock d'une interaction avec un admin"""
    return create_test_interaction(mock_admin_user, configured_guild)


@pytest.fixture
def mock_validator_interaction(mock_validator_user, configured_guild):
    """Mock d'une interaction avec un validateur"""
    # Ajouter le rôle validateur à l'utilisateur
    validator_role = configured_guild.roles[0]  # Premier rôle = validateur
    mock_validator_user.roles.append(validator_role)
    return create_test_interaction(mock_validator_user, configured_guild)


@pytest.fixture
def mock_bot():
    """Mock du bot Discord"""
    return MockBot()


@pytest.fixture
def mock_supabase_client():
    """Mock du client Supabase"""
    with patch('supabase_client.supabase_client') as mock:
        mock.is_connected = True
        mock.connect = AsyncMock(return_value=True)
        mock.check_user_flag = AsyncMock(return_value=None)
        mock.add_validated_report = AsyncMock(return_value=True)
        mock.get_guild_stats = AsyncMock(return_value={
            "total_checks": 0,
            "flags_found": 0,
            "flags_contributed": 0
        })
        yield mock


@pytest.fixture
def clean_guild_config():
    """Nettoyer la configuration des guildes après chaque test"""
    original_configs = guild_config.guild_configs.copy()
    yield
    # Restaurer la configuration originale
    guild_config.guild_configs.clear()
    guild_config.guild_configs.update(original_configs)


@pytest.fixture
def mock_discord_utils():
    """Mock de discord.utils.get"""
    with patch('discord.utils.get', side_effect=mock_discord_utils_get) as mock:
        yield mock


@pytest.fixture
def mock_security_validator():
    """Mock du validateur de sécurité"""
    with patch('utils.SecurityValidator') as mock_class:
        validator = MagicMock()
        validator.validate_input.return_value = True
        validator.sanitize_input.side_effect = lambda x: x
        mock_class.return_value = validator
        yield validator


@pytest.fixture
def mock_rate_limiter():
    """Mock du rate limiter"""
    with patch('utils.RateLimiter') as mock_class:
        limiter = MagicMock()
        limiter.check_rate_limit.return_value = True
        mock_class.return_value = limiter
        yield limiter


@pytest.fixture
def mock_report_tracker():
    """Mock du tracker de signalements"""
    with patch('utils.ReportTracker') as mock_class:
        tracker = MagicMock()
        tracker.is_duplicate_report.return_value = False
        tracker.add_report = MagicMock()
        mock_class.return_value = tracker
        yield tracker


@pytest.fixture
def mock_audit_logger():
    """Mock de l'audit logger"""
    with patch('utils.audit_logger') as mock:
        mock.log_security_event = MagicMock()
        mock.log_validation_action = MagicMock()
        yield mock


@pytest.fixture
def mock_evidence_collector():
    """Mock du collecteur de preuves"""
    with patch('bot.evidence_collector') as mock:
        mock.user_thread_mapping = {}
        mock.add_user_mapping = MagicMock()
        mock.remove_user_mapping = MagicMock()
        yield mock