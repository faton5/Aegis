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
    
    # Messages de démarrage informatifs
    print("🤖 Démarrage d'Aegis Bot...")
    print("📋 Vérification de la configuration...")
    
    # Validation de la configuration
    if not validate_config():
        print("❌ Erreur de configuration. Arrêt du bot.")
        return 1
        
    print("✅ Configuration validée")
    print("🔌 Connexion à Discord...")
    
    try:
        # Créer et démarrer le bot
        bot = AegisBot()
        await bot.setup()
        
        # Pas de message ici - sera affiché dans on_ready
        
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