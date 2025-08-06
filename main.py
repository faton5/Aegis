#!/usr/bin/env python3
"""
Point d'entrée principal pour Aegis Bot
Version refactorisée - Architecture modulaire
"""
import sys
import asyncio
from pathlib import Path

# Ajouter le répertoire du projet au path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.bot_config import bot_settings, validate_config
from config.logging_config import setup_logging
from core.bot import AegisBot


async def main():
    """Fonction principale"""
    
    # Configuration du logging
    logger = setup_logging(debug_mode=bot_settings.debug_enabled)
    logger.info("=" * 50)
    logger.info("🤖 Démarrage d'Aegis Bot (Version Refactorisée)")
    logger.info("=" * 50)
    
    # Validation de la configuration
    if not validate_config():
        logger.error("❌ Erreur de configuration. Arrêt du bot.")
        return 1
    
    logger.info(f"✅ Configuration validée")
    logger.info(f"🔧 Mode test: {'Activé' if bot_settings.test_mode_enabled else 'Désactivé'}")
    logger.info(f"🔧 Mode debug: {'Activé' if bot_settings.debug_enabled else 'Désactivé'}")
    logger.info(f"🗃️  Supabase: {'Activé' if bot_settings.supabase_enabled else 'Désactivé'}")
    
    try:
        # Créer et démarrer le bot
        bot = AegisBot()
        await bot.setup()
        
        logger.info("🚀 Bot initialisé avec succès")
        
        # Démarrer le bot
        await bot.start(bot_settings.token)
        
    except KeyboardInterrupt:
        logger.info("⏹️  Arrêt demandé par l'utilisateur")
        return 0
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Bot arrêté par l'utilisateur")
        sys.exit(0)