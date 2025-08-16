"""
Mocks personnalisés pour Discord.py - Simule toutes les interactions Discord
"""
import asyncio
from unittest.mock import AsyncMock, MagicMock
import discord
from typing import Optional, List, Dict, Any


class MockUser:
    """Mock d'un utilisateur Discord"""
    def __init__(self, user_id: int = 987654321, name: str = "testuser", display_name: str = "Test User"):
        self.id = user_id
        self.name = name
        self.display_name = display_name
        self.mention = f"<@{user_id}>"
        self.avatar = None
        self.bot = False
        self.system = False
        self.roles = []
        self.guild_permissions = discord.Permissions.all()
        self.dm_channel = None
        
    def __str__(self):
        return f"{self.name}#{1234}"
    
    def __repr__(self):
        return f"<MockUser id={self.id} name='{self.name}'>"


class MockRole:
    """Mock d'un rôle Discord"""
    def __init__(self, role_id: int = 777888999, name: str = "Test Role"):
        self.id = role_id
        self.name = name
        self.permissions = discord.Permissions.all()
        self.color = discord.Color.blue()
        self.hoist = False
        self.mentionable = True
        self.position = 1
        
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return f"<MockRole id={self.id} name='{self.name}'>"


class MockChannel:
    """Mock d'un canal Discord"""
    def __init__(self, channel_id: int = 111222333, name: str = "test-channel"):
        self.id = channel_id
        self.name = name
        self.type = discord.ChannelType.text
        self.guild = None
        self.position = 0
        self.send = AsyncMock()
        self.history = AsyncMock()
        
    def __str__(self):
        return f"#{self.name}"
        
    def __repr__(self):
        return f"<MockChannel id={self.id} name='{self.name}'>"


class MockForumChannel(MockChannel):
    """Mock d'un canal forum Discord"""
    def __init__(self, channel_id: int = 444555666, name: str = "agis-alerts"):
        super().__init__(channel_id, name)
        self.type = discord.ChannelType.forum
        self.create_thread = AsyncMock()
        
    async def create_thread_mock(self, name: str, content: str = None, **kwargs):
        """Mock de création de thread dans un forum"""
        thread = MockThread(999888777, name)
        thread.parent = self
        return (thread, None)  # Thread, Message initial
        
    def __post_init__(self):
        self.create_thread.side_effect = self.create_thread_mock


class MockThread:
    """Mock d'un thread Discord"""
    def __init__(self, thread_id: int = 999888777, name: str = "Test Thread"):
        self.id = thread_id
        self.name = name
        self.parent = None
        self.guild = None
        self.send = AsyncMock()
        self.edit = AsyncMock()
        
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return f"<MockThread id={self.id} name='{self.name}'>"


class MockGuild:
    """Mock d'une guilde (serveur) Discord"""
    def __init__(self, guild_id: int = 987654321, name: str = "Test Guild"):
        self.id = guild_id
        self.name = name
        self.channels = []
        self.roles = []
        self.members = []
        self.me = None
        self.owner = None
        
    def get_channel(self, channel_id: int):
        """Récupère un canal par ID"""
        for channel in self.channels:
            if channel.id == channel_id:
                return channel
        return None
        
    def get_role(self, role_id: int):
        """Récupère un rôle par ID"""
        for role in self.roles:
            if role.id == role_id:
                return role
        return None
        
    def get_member(self, user_id: int):
        """Récupère un membre par ID"""
        for member in self.members:
            if member.id == user_id:
                return member
        return None
        
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return f"<MockGuild id={self.id} name='{self.name}'>"


class MockInteractionResponse:
    """Mock de la réponse d'une interaction"""
    def __init__(self):
        self.send_message = AsyncMock()
        self.edit_message = AsyncMock()
        self.defer = AsyncMock()
        self.send_modal = AsyncMock()
        self.is_done = MagicMock(return_value=False)
        
    def mark_done(self):
        """Marque la réponse comme terminée"""
        self.is_done.return_value = True


class MockInteractionFollowup:
    """Mock du followup d'une interaction"""
    def __init__(self):
        self.send = AsyncMock()
        self.edit = AsyncMock()


class MockInteraction:
    """Mock d'une interaction Discord"""
    def __init__(self, user: MockUser = None, guild: MockGuild = None, channel: MockChannel = None):
        self.user = user or MockUser()
        self.guild = guild or MockGuild()
        self.channel = channel or MockChannel()
        self.client = AsyncMock()
        self.response = MockInteractionResponse()
        self.followup = MockInteractionFollowup()
        self.data = {}
        self.custom_id = None
        self.values = []
        
        # Lier le canal à la guilde
        if self.channel:
            self.channel.guild = self.guild
            
        # Ajouter l'utilisateur aux membres de la guilde s'il n'y est pas
        if self.user not in self.guild.members:
            self.guild.members.append(self.user)
    
    def __repr__(self):
        return f"<MockInteraction user={self.user.name} guild={self.guild.name}>"


class MockBot:
    """Mock du bot Discord"""
    def __init__(self):
        self.user = MockUser(555666777, "Aegis Bot", "Aegis Bot")
        self.get_user = MagicMock()
        self.get_guild = MagicMock()
        self.get_channel = MagicMock()
        self.tree = MagicMock()
        
    def get_user_mock(self, user_id: int):
        """Mock pour récupérer un utilisateur"""
        return MockUser(user_id, f"user_{user_id}", f"User {user_id}")
        
    def __post_init__(self):
        self.get_user.side_effect = self.get_user_mock


class MockMessage:
    """Mock d'un message Discord"""
    def __init__(self, content: str = "Test message", author: MockUser = None):
        self.id = 123456789012345678
        self.content = content
        self.author = author or MockUser()
        self.channel = None
        self.guild = None
        self.attachments = []
        self.embeds = []
        self.edit = AsyncMock()
        self.delete = AsyncMock()
        self.add_reaction = AsyncMock()
        
    def __str__(self):
        return self.content
        
    def __repr__(self):
        return f"<MockMessage id={self.id} content='{self.content[:20]}...'>"


class MockView:
    """Mock d'une vue Discord (UI)"""
    def __init__(self):
        self.children = []
        self.timeout = 180
        self.is_finished = MagicMock(return_value=False)
        self.stop = MagicMock()
        
    def add_item(self, item):
        """Ajoute un composant à la vue"""
        self.children.append(item)
        
    def remove_item(self, item):
        """Retire un composant de la vue"""
        if item in self.children:
            self.children.remove(item)
            
    def clear_items(self):
        """Retire tous les composants"""
        self.children.clear()


class MockModal:
    """Mock d'un modal Discord"""
    def __init__(self, title: str = "Test Modal"):
        self.title = title
        self.children = []
        self.custom_id = "test_modal"
        
    def add_item(self, item):
        """Ajoute un champ au modal"""
        self.children.append(item)
        
    async def on_submit(self, interaction: MockInteraction):
        """Callback de soumission du modal"""
        pass


class MockTextInput:
    """Mock d'un champ de texte dans un modal"""
    def __init__(self, label: str = "Test Input", placeholder: str = None):
        self.label = label
        self.placeholder = placeholder
        self.value = ""
        self.required = True
        self.max_length = 1000
        
    def __str__(self):
        return self.value


class MockSelect:
    """Mock d'un menu de sélection"""
    def __init__(self, placeholder: str = "Select..."):
        self.placeholder = placeholder
        self.values = []
        self.options = []
        self.callback = AsyncMock()
        
    def add_option(self, label: str, value: str, description: str = None):
        """Ajoute une option au select"""
        option = MagicMock()
        option.label = label
        option.value = value
        option.description = description
        self.options.append(option)


class MockButton:
    """Mock d'un bouton Discord"""
    def __init__(self, label: str = "Test Button", style=discord.ButtonStyle.primary):
        self.label = label
        self.style = style
        self.disabled = False
        self.callback = AsyncMock()
        self.custom_id = f"button_{label.lower().replace(' ', '_')}"


def create_configured_guild() -> MockGuild:
    """Crée une guilde mockée entièrement configurée"""
    guild = MockGuild(987654321, "Test Configured Guild")
    
    # Ajouter le forum d'alertes
    forum = MockForumChannel(444555666, "agis-alerts")
    forum.guild = guild
    guild.channels.append(forum)
    
    # Ajouter le rôle validateur
    validator_role = MockRole(777888999, "Validateur")
    guild.roles.append(validator_role)
    
    # Ajouter quelques membres avec rôles
    admin_user = MockUser(111111111, "admin", "Admin User")
    admin_user.guild_permissions = discord.Permissions.all()
    guild.members.append(admin_user)
    
    validator_user = MockUser(222222222, "validator", "Validator User")
    validator_user.roles.append(validator_role)
    guild.members.append(validator_user)
    
    regular_user = MockUser(333333333, "regular", "Regular User")
    guild.members.append(regular_user)
    
    return guild


def create_test_interaction(user: MockUser = None, guild: MockGuild = None, 
                          channel: MockChannel = None) -> MockInteraction:
    """Crée une interaction mockée pour les tests"""
    if not user:
        user = MockUser()
    if not guild:
        guild = create_configured_guild()
    if not channel:
        channel = guild.channels[0] if guild.channels else MockChannel()
        
    interaction = MockInteraction(user, guild, channel)
    return interaction


# Fonctions utilitaires pour les tests
def mock_discord_utils_get(collection, **kwargs):
    """Mock de discord.utils.get"""
    if not collection:
        return None
        
    for item in collection:
        match = True
        for key, value in kwargs.items():
            if not hasattr(item, key) or getattr(item, key) != value:
                match = False
                break
        if match:
            return item
    return None


# Export des classes principales
__all__ = [
    'MockUser', 'MockRole', 'MockChannel', 'MockForumChannel', 'MockThread',
    'MockGuild', 'MockInteraction', 'MockBot', 'MockMessage', 'MockView',
    'MockModal', 'MockTextInput', 'MockSelect', 'MockButton',
    'create_configured_guild', 'create_test_interaction', 'mock_discord_utils_get'
]