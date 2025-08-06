"""
Configuration centralisée du logging pour Aegis
"""
import logging
import sys
import codecs
from datetime import datetime
from pathlib import Path


def setup_logging(debug_mode: bool = False) -> logging.Logger:
    """
    Configure le système de logging centralisé
    
    Args:
        debug_mode: Activer le mode debug
        
    Returns:
        Logger configuré
    """
    
    # Configuration de l'encodage pour Windows
    if sys.platform == "win32":
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())
    
    # Niveau de logging
    log_level = logging.DEBUG if debug_mode else logging.INFO
    
    # Format des messages
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Logger principal
    logger = logging.getLogger('aegis')
    logger.setLevel(log_level)
    
    # Éviter la duplication des handlers
    if logger.handlers:
        return logger
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler pour fichier
    log_file = Path('aegis_bot.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Réduire le niveau des loggers externes
    logging.getLogger('discord').setLevel(logging.WARNING)
    logging.getLogger('discord.http').setLevel(logging.WARNING)
    logging.getLogger('aiohttp').setLevel(logging.WARNING)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Obtenir un logger spécifique
    
    Args:
        name: Nom du logger (optionnel)
        
    Returns:
        Logger configuré
    """
    if name:
        return logging.getLogger(f'aegis.{name}')
    return logging.getLogger('aegis')