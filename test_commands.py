# Commandes de test et diagnostic pour Aegis
import discord
from discord import app_commands
import asyncio
import traceback
from datetime import datetime
from config import BOT_CONFIG, REPORT_CATEGORIES, ERROR_MESSAGES
from utils import SecurityValidator, RateLimiter, ReportTracker, AuditLogger, logger
from supabase_client import supabase_client
from guild_config import guild_config
from translations import translator


class TestBugLogger:
    """Logger spécialisé pour capturer et enregistrer les bugs durant les tests"""
    
    def __init__(self):
        self.bugs_found = []
        
    def log_bug(self, test_name: str, error: Exception, context: str = ""):
        """Enregistre un bug trouvé durant les tests"""
        bug_entry = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc()
        }
        self.bugs_found.append(bug_entry)
        
        # Logger dans le fichier aegis_bot.log
        logger.error(translator.t("bug_detected_log", fallback="🐛 BUG DÉTECTÉ - Test: {test_name} | Erreur: {error} | Contexte: {context}").format(test_name=test_name, error=error, context=context))
        logger.error(translator.t("traceback_log", fallback="🐛 TRACEBACK: {traceback}").format(traceback=traceback.format_exc()))
        
        return bug_entry
    
    def get_bugs_summary(self):
        """Retourne un résumé des bugs trouvés"""
        if not self.bugs_found:
            return translator.t("no_bugs_detected_summary", fallback="✅ Aucun bug détecté lors des tests !")
        
        summary = translator.t("bugs_detected_summary", fallback="🐛 **{count} bug(s) détecté(s):**\n\n").format(count=len(self.bugs_found))
        for i, bug in enumerate(self.bugs_found, 1):
            summary += translator.t("bug_entry_name", fallback="**{i}.** `{test_name}`\n").format(i=i, test_name=bug['test_name'])
            summary += translator.t("bug_entry_error", fallback="   • Erreur: `{error_type}: {error_message}`\n").format(error_type=bug['error_type'], error_message=bug['error_message'])
            if bug['context']:
                summary += translator.t("bug_entry_context", fallback="   • Contexte: {context}\n").format(context=bug['context'])
            summary += translator.t("bug_entry_timestamp", fallback="   • Horodatage: {timestamp}\n\n").format(timestamp=bug['timestamp'])
        
        return summary


# Instance globale du logger de bugs
test_bug_logger = TestBugLogger()


async def test_security_validator():
    """Test du validateur de sécurité"""
    validator = SecurityValidator()
    test_cases = [
        ("Test normal", "Utilisateur normal"),
        ("Test script", "<script>alert('xss')</script>"),
        ("Test SQL", "'; DROP TABLE users; --"),
        ("Test longueur", "a" * 2000),
        ("Test caractères spéciaux", "Test avec émojis 🚨🔞"),
    ]
    
    results = []
    for name, input_text in test_cases:
        try:
            is_valid = validator.validate_input(input_text)
            sanitized = validator.sanitize_input(input_text)
            results.append(translator.t("test_valid_sanitized", fallback="✅ {name}: Valide={is_valid}, Longueur sanitisée={length}").format(name=name, is_valid=is_valid, length=len(sanitized)))
        except Exception as e:
            test_bug_logger.log_bug("security_validator", e, f"Input: {input_text[:50]}...")
            results.append(translator.t("test_error", fallback="❌ {name}: ERREUR - {error}").format(name=name, error=e))
    
    return results


async def test_rate_limiter():
    """Test du système de rate limiting"""
    rate_limiter = RateLimiter()
    user_id = 123456789  # ID de test
    
    results = []
    try:
        # Test des limites normales
        for i in range(BOT_CONFIG["MAX_REPORTS_PER_USER_PER_HOUR"] + 2):
            allowed = rate_limiter.check_rate_limit(user_id)
            if i < BOT_CONFIG["MAX_REPORTS_PER_USER_PER_HOUR"]:
                if allowed:
                    results.append(f"✅ Tentative {i+1}: Autorisée")
                else:
                    test_bug_logger.log_bug("rate_limiter", Exception("Rate limit prématuré"), f"Tentative {i+1}")
                    results.append(f"❌ Tentative {i+1}: Rate limit prématuré")
            else:
                if not allowed:
                    results.append(f"✅ Tentative {i+1}: Correctement bloquée")
                else:
                    test_bug_logger.log_bug("rate_limiter", Exception("Rate limit non appliqué"), f"Tentative {i+1}")
                    results.append(f"❌ Tentative {i+1}: Devrait être bloquée")
                    
    except Exception as e:
        test_bug_logger.log_bug("rate_limiter", e, "Test général du rate limiter")
        results.append(f"❌ Erreur générale: {e}")
    
    return results


async def test_supabase_connection():
    """Test de la connexion Supabase"""
    results = []
    try:
        if not BOT_CONFIG["SUPABASE_ENABLED"]:
            results.append("⚠️ Supabase désactivé dans la configuration")
            return results
            
        # Test de connexion basique
        response = await supabase_client.test_connection()
        if response:
            results.append("✅ Connexion Supabase: OK")
        else:
            test_bug_logger.log_bug("supabase_connection", Exception("Connexion échouée"), "Test de base")
            results.append("❌ Connexion Supabase: ÉCHEC")
            
    except Exception as e:
        test_bug_logger.log_bug("supabase_connection", e, "Test de connexion")
        results.append(f"❌ Erreur Supabase: {e}")
    
    return results


async def test_guild_config():
    """Test de la configuration des guildes"""
    results = []
    try:
        # Test des guildes configurées
        guilds = guild_config.list_configured_guilds()
        results.append(f"✅ Guildes configurées: {len(guilds)}")
        
        for guild_id in guilds[:3]:  # Tester les 3 premières seulement
            try:
                config = guild_config.get_guild_config(guild_id)
                if config:
                    results.append(f"✅ Guild {guild_id}: Configuration OK")
                else:
                    test_bug_logger.log_bug("guild_config", Exception("Configuration vide"), f"Guild {guild_id}")
                    results.append(f"❌ Guild {guild_id}: Configuration vide")
            except Exception as e:
                test_bug_logger.log_bug("guild_config", e, f"Guild {guild_id}")
                results.append(f"❌ Guild {guild_id}: Erreur - {e}")
                
    except Exception as e:
        test_bug_logger.log_bug("guild_config", e, "Test général guild config")
        results.append(f"❌ Erreur générale guild config: {e}")
    
    return results


@app_commands.command(name="test_diagnostics", description="🔧 Exécute des tests de diagnostic du système (mode test uniquement)")
async def test_diagnostics(interaction: discord.Interaction):
    """Commande de diagnostic complète - disponible uniquement en mode test"""
    
    try:
        # Vérifier si le mode test est activé
        if not BOT_CONFIG["TEST_MODE_ENABLED"]:
            await interaction.response.send_message(
                "❌ Cette commande n'est disponible qu'en mode test.\n"
                "Pour l'activer, définissez la variable d'environnement `AEGIS_TEST_MODE=true`",
                ephemeral=True
            )
            return
        
        # Vérifier les permissions (administrateur ou validateur)
        if not any(role.name in ["Validateur", "Administrator"] or role.permissions.administrator 
                   for role in interaction.user.roles):
            await interaction.response.send_message(ERROR_MESSAGES["no_permission"], ephemeral=True)
            return
        
        # Tests basiques rapides
        security_ok = "✅" if hasattr(SecurityValidator(), 'validate_input') else "❌"
        rate_limiter_ok = "✅" if hasattr(RateLimiter(), 'check_rate_limit') else "❌"
        supabase_ok = "✅" if BOT_CONFIG["SUPABASE_ENABLED"] else "⚠️"
        
        embed = discord.Embed(
            title="🔧 Diagnostic Rapide - Système Aegis",
            description="Résultats des tests de base",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="🔒 Validateur sécurité", value=security_ok, inline=True)
        embed.add_field(name="⏰ Rate limiter", value=rate_limiter_ok, inline=True)
        embed.add_field(name="🗄️ Supabase", value=supabase_ok, inline=True)
        
        embed.add_field(
            name="📋 Statut général", 
            value="✅ Système opérationnel" if all([security_ok == "✅", rate_limiter_ok == "✅"]) else "⚠️ Vérifications nécessaires",
            inline=False
        )
        
        embed.set_footer(text="Diagnostic rapide terminé • Version simplifiée")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        logger.error(f"Erreur diagnostic: {e}")
        try:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    f"❌ Erreur lors du diagnostic: {str(e)[:100]}",
                    ephemeral=True
                )
        except:
            pass


def register_test_commands(tree: app_commands.CommandTree):
    """Enregistre les commandes de test si le mode test est activé"""
    import os
    # Debug : vérifier les valeurs
    env_var = os.getenv("AEGIS_TEST_MODE", "false")
    config_value = BOT_CONFIG["TEST_MODE_ENABLED"]
    logger.info(f"🔧 DEBUG - AEGIS_TEST_MODE env: '{env_var}', config: {config_value}")
    
    if BOT_CONFIG["TEST_MODE_ENABLED"]:
        tree.add_command(test_diagnostics)
        logger.info("🔧 Mode test activé - Commandes de diagnostic enregistrées")
    else:
        logger.info("🔧 Mode test désactivé - Commandes de diagnostic non disponibles")