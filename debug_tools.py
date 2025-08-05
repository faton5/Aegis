# Outils de debug pour le bot Aegis
import discord
from discord import app_commands
import os
import sys
from datetime import datetime
from config import BOT_CONFIG
from utils import create_secure_embed, logger
from supabase_client import supabase_client
import traceback

class DebugCommands:
    """Commandes de debug pour diagnostiquer les problèmes"""

@app_commands.command(name="debug", description="🔧 Diagnostics système du bot Aegis")
@app_commands.describe(component="Composant à tester")
@app_commands.choices(component=[
    app_commands.Choice(name="🔍 État général", value="general"),
    app_commands.Choice(name="🗄️ Connexion Supabase", value="supabase"),
    app_commands.Choice(name="⚙️ Configuration", value="config"),
    app_commands.Choice(name="🏠 Structure serveur", value="server"),
    app_commands.Choice(name="🔑 Permissions", value="permissions"),
    app_commands.Choice(name="📋 Toute la config avancée", value="advanced_config")
])
async def debug_system(interaction: discord.Interaction, component: str = "general"):
    """Commande de debug pour diagnostiquer les problèmes"""
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        if component == "general":
            embed = await debug_general_status(interaction)
        elif component == "supabase":
            embed = await debug_supabase_connection(interaction)
        elif component == "config":
            embed = await debug_configuration(interaction)
        elif component == "server":
            embed = await debug_server_structure(interaction)
        elif component == "permissions":
            embed = await debug_permissions(interaction)
        elif component == "advanced_config":
            embed = await debug_advanced_config(interaction)
        else:
            embed = await debug_general_status(interaction)
            
        await interaction.followup.send(embed=embed, ephemeral=True)
        
    except Exception as e:
        error_embed = create_secure_embed(
            "❌ Erreur de debug",
            f"Erreur lors du diagnostic: {str(e)}",
            discord.Color.red()
        )
        error_embed.add_field(
            name="🔍 Traceback", 
            value=f"```{traceback.format_exc()[:1000]}```", 
            inline=False
        )
        await interaction.followup.send(embed=error_embed, ephemeral=True)

async def debug_general_status(interaction: discord.Interaction):
    """Debug de l'état général du système"""
    embed = create_secure_embed(
        "🔍 Debug - État général",
        "Diagnostic complet du système Aegis",
        discord.Color.blue()
    )
    
    # Informations Python
    embed.add_field(
        name="🐍 Python",
        value=f"Version: {sys.version.split()[0]}\nChemin: {sys.executable}",
        inline=True
    )
    
    # Informations Discord.py
    embed.add_field(
        name="🤖 Discord.py",
        value=f"Version: {discord.__version__}\nLatence: {round(interaction.client.latency * 1000)}ms",
        inline=True
    )
    
    # État du bot
    embed.add_field(
        name="🟢 Bot Status",
        value=f"Connecté: ✅\nServeurs: {len(interaction.client.guilds)}\nUtilisateurs: {len(set(interaction.client.get_all_members()))}",
        inline=True
    )
    
    # Variables d'environnement
    env_status = []
    env_vars = ["DISCORD_TOKEN", "SUPABASE_URL", "SUPABASE_KEY"]
    for var in env_vars:
        status = "✅" if os.getenv(var) else "❌"
        # Masquer les valeurs sensibles
        value = "***DÉFINI***" if os.getenv(var) else "MANQUANT"
        env_status.append(f"{var}: {status} {value}")
    
    embed.add_field(
        name="🔐 Variables d'environnement",
        value="\n".join(env_status),
        inline=False
    )
    
    # Configuration Supabase
    supabase_status = "✅ Activé" if BOT_CONFIG["SUPABASE_ENABLED"] else "❌ Désactivé"
    embed.add_field(
        name="🗄️ Supabase",
        value=f"État: {supabase_status}\nConnexion: {'✅' if supabase_client.is_connected else '❌'}",
        inline=True
    )
    
    embed.set_footer(text=f"Debug effectué le {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    return embed

async def debug_supabase_connection(interaction: discord.Interaction):
    """Debug spécifique de la connexion Supabase"""
    embed = create_secure_embed(
        "🗄️ Debug - Connexion Supabase",
        "Test détaillé de la base de données centralisée",
        discord.Color.green()
    )
    
    # État de la configuration
    embed.add_field(
        name="⚙️ Configuration",
        value=f"Activé: {'✅' if BOT_CONFIG['SUPABASE_ENABLED'] else '❌'}\nURL: {'✅' if os.getenv('SUPABASE_URL') else '❌'}\nClé: {'✅' if os.getenv('SUPABASE_KEY') else '❌'}",
        inline=True
    )
    
    # Test de connexion
    try:
        if not supabase_client.is_connected:
            connection_result = await supabase_client.connect()
        else:
            connection_result = True
            
        embed.add_field(
            name="🔗 Connexion",
            value="✅ Connecté" if connection_result else "❌ Échec",
            inline=True
        )
        
        # Test des tables
        if connection_result:
            try:
                # Test table flagged_users
                result = supabase_client.client.table("flagged_users").select("id").limit(1).execute()
                flagged_users_status = "✅ OK"
            except Exception as e:
                flagged_users_status = f"❌ {str(e)[:50]}"
            
            try:
                # Test table audit_logs
                result = supabase_client.client.table("audit_logs").select("id").limit(1).execute()
                audit_logs_status = "✅ OK"
            except Exception as e:
                audit_logs_status = f"❌ {str(e)[:50]}"
                
            embed.add_field(
                name="📊 Tables",
                value=f"flagged_users: {flagged_users_status}\naudit_logs: {audit_logs_status}",
                inline=False
            )
            
            # Test des fonctions
            try:
                # Test de la fonction check_user_flag
                result = supabase_client.client.rpc("check_user_flag", {
                    "check_user_id": 123456789,
                    "requesting_guild_id": interaction.guild.id,
                    "requesting_guild_name": interaction.guild.name
                }).execute()
                function_status = "✅ Fonctions OK"
            except Exception as e:
                function_status = f"❌ Fonction: {str(e)[:50]}"
                
            embed.add_field(
                name="⚙️ Fonctions SQL",
                value=function_status,
                inline=True
            )
            
    except Exception as e:
        embed.add_field(
            name="❌ Erreur",
            value=f"```{str(e)[:200]}```",
            inline=False
        )
    
    return embed

async def debug_configuration(interaction: discord.Interaction):
    """Debug de la configuration du bot"""
    embed = create_secure_embed(
        "⚙️ Debug - Configuration",
        "État de la configuration du bot",
        discord.Color.orange()
    )
    
    # Configuration principale
    config_info = []
    important_configs = [
        "ALERTS_CHANNEL_NAME", "VALIDATOR_ROLE_NAME", "QUORUM_PERCENTAGE",
        "MAX_REPORTS_PER_USER_PER_HOUR", "SUPABASE_ENABLED", "AUTO_CHECK_NEW_MEMBERS"
    ]
    
    for key in important_configs:
        value = BOT_CONFIG.get(key, "NON DÉFINI")
        config_info.append(f"{key}: {value}")
    
    embed.add_field(
        name="🔧 Configuration principale",
        value="```\n" + "\n".join(config_info) + "```",
        inline=False
    )
    
    # Configuration avancée (si elle existe)
    try:
        from guild_config import guild_config
        guild_settings = guild_config.get_guild_config(interaction.guild.id)
        
        auto_actions = guild_settings.get("auto_actions", {})
        embed.add_field(
            name="⚔️ Actions automatiques",
            value=f"Critical: {auto_actions.get('critical', 'Non défini')}\nHigh: {auto_actions.get('high', 'Non défini')}\nMedium: {auto_actions.get('medium', 'Non défini')}",
            inline=True
        )
        
        quarantine = guild_settings.get("quarantine", {})
        embed.add_field(
            name="🛡️ Quarantaine",
            value=f"Activé: {quarantine.get('enabled', False)}\nDurée: {quarantine.get('duration_hours', 24)}h\nRôle: {quarantine.get('role_name', 'Non défini')}",
            inline=True
        )
        
    except Exception as e:
        embed.add_field(
            name="❌ Config avancée",
            value=f"Erreur: {str(e)[:100]}",
            inline=False
        )
    
    return embed

async def debug_server_structure(interaction: discord.Interaction):
    """Debug de la structure du serveur Discord"""
    embed = create_secure_embed(
        "🏠 Debug - Structure serveur",
        f"Analyse du serveur {interaction.guild.name}",
        discord.Color.purple()
    )
    
    # Forum d'alertes
    alerts_forum = discord.utils.get(interaction.guild.channels, name=BOT_CONFIG["ALERTS_CHANNEL_NAME"])
    forum_status = "✅ Trouvé" if alerts_forum else "❌ Manquant"
    forum_type = type(alerts_forum).__name__ if alerts_forum else "N/A"
    
    embed.add_field(
        name="📋 Forum d'alertes",
        value=f"Canal: {BOT_CONFIG['ALERTS_CHANNEL_NAME']}\nStatut: {forum_status}\nType: {forum_type}",
        inline=True
    )
    
    # Canal de flags
    flag_channel = discord.utils.get(interaction.guild.channels, name=BOT_CONFIG["FLAG_ALERT_CHANNEL"])
    flag_status = "✅ Trouvé" if flag_channel else "❌ Manquant"
    
    embed.add_field(
        name="🚨 Canal de flags",
        value=f"Canal: {BOT_CONFIG['FLAG_ALERT_CHANNEL']}\nStatut: {flag_status}",
        inline=True
    )
    
    # Rôle validateur
    validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
    role_status = "✅ Trouvé" if validator_role else "❌ Manquant"
    role_members = len([m for m in interaction.guild.members if validator_role in m.roles]) if validator_role else 0
    
    embed.add_field(
        name="👥 Rôle validateur",
        value=f"Rôle: {BOT_CONFIG['VALIDATOR_ROLE_NAME']}\nStatut: {role_status}\nMembres: {role_members}",
        inline=True
    )
    
    # Statistiques générales
    embed.add_field(
        name="📊 Statistiques",
        value=f"Membres: {interaction.guild.member_count}\nCanaux: {len(interaction.guild.channels)}\nRôles: {len(interaction.guild.roles)}",
        inline=False
    )
    
    # Permissions du bot
    bot_member = interaction.guild.get_member(interaction.client.user.id)
    bot_perms = bot_member.guild_permissions if bot_member else None
    
    if bot_perms:
        important_perms = {
            "Gérer les canaux": bot_perms.manage_channels,
            "Gérer les rôles": bot_perms.manage_roles,
            "Gérer les threads": bot_perms.manage_threads,
            "Envoyer des messages": bot_perms.send_messages,
            "Utiliser applications": bot_perms.use_application_commands
        }
        
        perms_status = []
        for perm, has_perm in important_perms.items():
            status = "✅" if has_perm else "❌"
            perms_status.append(f"{perm}: {status}")
        
        embed.add_field(
            name="🔑 Permissions du bot",
            value="\n".join(perms_status),
            inline=False
        )
    
    return embed

async def debug_permissions(interaction: discord.Interaction):
    """Debug des permissions de l'utilisateur"""
    embed = create_secure_embed(
        "🔑 Debug - Permissions",
        f"Permissions de {interaction.user.display_name}",
        discord.Color.gold()
    )
    
    # Permissions de l'utilisateur
    user_perms = interaction.user.guild_permissions
    
    embed.add_field(
        name="👑 Statut administrateur",
        value="✅ Administrateur" if user_perms.administrator else "❌ Pas administrateur",
        inline=True
    )
    
    # Rôle validateur
    validator_role = discord.utils.get(interaction.guild.roles, name=BOT_CONFIG["VALIDATOR_ROLE_NAME"])
    has_validator_role = validator_role and validator_role in interaction.user.roles
    
    embed.add_field(
        name="🛡️ Rôle validateur",
        value="✅ Validateur" if has_validator_role else "❌ Pas validateur",
        inline=True
    )
    
    # Rôles de l'utilisateur
    user_roles = [role.name for role in interaction.user.roles if role.name != "@everyone"]
    
    embed.add_field(
        name="🎭 Rôles",
        value=", ".join(user_roles[:10]) if user_roles else "Aucun rôle",
        inline=False
    )
    
    # Permissions importantes
    important_perms = {
        "Gérer le serveur": user_perms.manage_guild,
        "Gérer les canaux": user_perms.manage_channels,
        "Gérer les rôles": user_perms.manage_roles,
        "Bannir des membres": user_perms.ban_members,
        "Expulser des membres": user_perms.kick_members
    }
    
    perms_status = []
    for perm, has_perm in important_perms.items():
        status = "✅" if has_perm else "❌"
        perms_status.append(f"{perm}: {status}")
    
    embed.add_field(
        name="⚙️ Permissions spéciales",
        value="\n".join(perms_status),
        inline=False
    )
    
    return embed

async def debug_advanced_config(interaction: discord.Interaction):
    """Debug complet de la configuration avancée"""
    embed = create_secure_embed(
        "📋 Debug - Configuration avancée complète",
        "État détaillé de toute la configuration",
        discord.Color.dark_blue()
    )
    
    try:
        from guild_config import guild_config
        guild_settings = guild_config.get_guild_config(interaction.guild.id)
        
        # Actions automatiques
        auto_actions = guild_settings.get("auto_actions", {})
        embed.add_field(
            name="⚔️ Actions automatiques",
            value=f"```json\n{auto_actions}```",
            inline=False
        )
        
        # Quarantaine
        quarantine = guild_settings.get("quarantine", {})
        embed.add_field(
            name="🛡️ Quarantaine",
            value=f"```json\n{quarantine}```",
            inline=False
        )
        
        # Seuils
        thresholds = guild_settings.get("thresholds", {})
        embed.add_field(
            name="📊 Seuils",
            value=f"```json\n{thresholds}```",
            inline=False
        )
        
        # Permissions
        permissions = guild_settings.get("permissions", {})
        embed.add_field(
            name="🔑 Permissions",
            value=f"```json\n{permissions}```",
            inline=False
        )
        
    except Exception as e:
        embed.add_field(
            name="❌ Erreur",
            value=f"Impossible de charger la config avancée: {str(e)}",
            inline=False
        )
    
    return embed

@app_commands.command(name="test-supabase", description="🧪 Test manuel de Supabase")
async def test_supabase_manual(interaction: discord.Interaction):
    """Test manuel de toutes les fonctions Supabase"""
    
    await interaction.response.defer(ephemeral=True)
    
    embed = create_secure_embed(
        "🧪 Test Supabase",
        "Test en cours des fonctionnalités Supabase...",
        discord.Color.yellow()
    )
    
    results = []
    
    # Test 1: Connexion
    try:
        if not supabase_client.is_connected:
            await supabase_client.connect()
        results.append("✅ Connexion: OK")
    except Exception as e:
        results.append(f"❌ Connexion: {str(e)[:50]}")
    
    # Test 2: Vérification utilisateur (utilisateur fictif)
    try:
        flag_data = await supabase_client.check_user_flag(
            123456789,  # ID fictif
            interaction.guild.id,
            interaction.guild.name
        )
        results.append("✅ Vérification utilisateur: OK")
    except Exception as e:
        results.append(f"❌ Vérification: {str(e)[:50]}")
    
    # Test 3: Statistiques serveur
    try:
        stats = await supabase_client.get_guild_stats(interaction.guild.id)
        results.append(f"✅ Statistiques: {stats}")
    except Exception as e:
        results.append(f"❌ Statistiques: {str(e)[:50]}")
    
    embed.description = "\n".join(results)
    await interaction.followup.send(embed=embed, ephemeral=True)

# Fonction pour ajouter les logs de debug
def setup_debug_logging():
    """Configure les logs de debug avancés"""
    import logging
    
    # Créer un handler spécial pour debug
    debug_handler = logging.StreamHandler()
    debug_handler.setLevel(logging.DEBUG)
    
    # Format détaillé pour debug
    debug_formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    debug_handler.setFormatter(debug_formatter)
    
    # Ajouter aux loggers importants
    loggers = ['AegisBot', 'discord', 'httpx']
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
            logger.addHandler(debug_handler)
    
    print("[DEBUG] Système de debug activé")