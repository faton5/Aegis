"""
Service de gestion des configurations de serveurs (guildes)
"""
import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

from config.logging_config import get_logger

logger = get_logger('guild_service')


class GuildService:
    """Service pour la gestion des configurations de serveurs"""
    
    def __init__(self, config_dir: str = "guild_configs"):
        self.config_dir = Path(config_dir)
        self.old_config_file = "guild_configs.json"
        
        # Créer le dossier s'il n'existe pas
        self.config_dir.mkdir(exist_ok=True)
        
        # Migrer l'ancien fichier s'il existe
        self._migrate_old_config()
    
    def _migrate_old_config(self):
        """Migre l'ancien fichier guild_configs.json vers des fichiers séparés"""
        old_file = Path(self.old_config_file)
        
        if old_file.exists():
            try:
                with open(old_file, 'r', encoding='utf-8') as f:
                    old_configs = json.load(f)
                
                # Créer un fichier pour chaque serveur
                for guild_id, config in old_configs.items():
                    self._save_guild_config(guild_id, config)
                
                # Renommer l'ancien fichier pour backup
                backup_name = f"{self.old_config_file}.backup"
                old_file.rename(backup_name)
                logger.info(f"Migration terminée. Ancien fichier sauvé en {backup_name}")
                
            except Exception as e:
                logger.error(f"Erreur lors de la migration: {e}")
    
    def _get_config_path(self, guild_id: str) -> Path:
        """Obtient le chemin du fichier de config pour un serveur"""
        return self.config_dir / f"{guild_id}.json"
    
    def _load_guild_config(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Charge la configuration d'un serveur depuis son fichier"""
        config_path = self._get_config_path(guild_id)
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Erreur lors du chargement de la config {guild_id}: {e}")
        
        return None
    
    def _save_guild_config(self, guild_id: str, config: Dict[str, Any]):
        """Sauvegarde la configuration d'un serveur"""
        config_path = self._get_config_path(guild_id)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la config {guild_id}: {e}")
    
    def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """
        Obtenir la configuration d'un serveur
        
        Args:
            guild_id: ID du serveur Discord
            
        Returns:
            Configuration du serveur (ou configuration par défaut)
        """
        guild_str = str(guild_id)
        config = self._load_guild_config(guild_str)
        
        if config is None:
            # Créer la config par défaut
            config = self.get_default_config()
            self._save_guild_config(guild_str, config)
            logger.info(f"Configuration par défaut créée pour guild {guild_id}")
        
        return config
    
    def update_guild_config(self, guild_id: int, updates: Dict[str, Any]):
        """
        Mettre à jour la configuration d'un serveur
        
        Args:
            guild_id: ID du serveur Discord
            updates: Mises à jour à appliquer
        """
        guild_str = str(guild_id)
        config = self.get_guild_config(guild_id)  # Charge ou crée la config
        config.update(updates)
        self._save_guild_config(guild_str, config)
        logger.info(f"Configuration mise à jour pour guild {guild_id}: {list(updates.keys())}")
    
    def list_configured_guilds(self) -> List[str]:
        """
        Liste tous les serveurs ayant une configuration
        
        Returns:
            Liste des IDs de serveurs configurés
        """
        if not self.config_dir.exists():
            return []
        
        guild_ids = []
        for config_file in self.config_dir.glob("*.json"):
            guild_ids.append(config_file.stem)  # Nom sans extension
        
        return guild_ids
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Configuration par défaut pour un nouveau serveur
        
        Returns:
            Configuration par défaut
        """
        return {
            # Actions automatiques par niveau de flag
            "auto_actions": {
                "critical": "ban",      # ban, kick, quarantine, alert, none
                "high": "quarantine",   
                "medium": "alert",      
                "low": "none"
            },
            
            # Seuils de validation
            "validation_thresholds": {
                "quorum_percentage": 80,        # % de validateurs nécessaires
                "min_validators": 2,            # Minimum de validateurs
                "validation_timeout_hours": 24  # Timeout avant auto-rejet
            },
            
            # Limites de taux
            "rate_limits": {
                "reports_per_user_per_hour": 3,
                "reports_per_guild_per_hour": 20
            },
            
            # Notifications
            "notifications": {
                "new_report_ping_role": True,       # Ping le rôle validateur
                "validation_dm_reporter": False,    # DM au rapporteur
                "daily_summary": True,              # Résumé quotidien
                "weekly_stats": False               # Stats hebdomadaires
            },
            
            # Configuration de base
            "language": "fr",           # Langue par défaut
            "configured": False,        # Premier setup terminé
            "debug_enabled": False,     # Commandes debug activées (par défaut: NON)
            
            # IDs des éléments Discord configurés
            "forum_channel_id": None,   # ID du forum d'alertes
            "validator_role_id": None,  # ID du rôle validateur
            "log_channel_id": None,     # ID du canal de logs
            
            # Métadonnées
            "created_at": None,         # Date de création
            "last_updated": None,       # Dernière mise à jour
            "version": "2.0"            # Version de config
        }
    
    def is_guild_configured(self, guild_id: int) -> bool:
        """
        Vérifier si un serveur est configuré
        
        Args:
            guild_id: ID du serveur Discord
            
        Returns:
            True si configuré
        """
        config = self.get_guild_config(guild_id)
        return config.get('configured', False)
    
    def mark_guild_configured(self, guild_id: int):
        """
        Marquer un serveur comme configuré
        
        Args:
            guild_id: ID du serveur Discord
        """
        from datetime import datetime
        
        self.update_guild_config(guild_id, {
            'configured': True,
            'last_updated': datetime.utcnow().isoformat()
        })
    
    def get_guild_language(self, guild_id: int) -> str:
        """
        Obtenir la langue configurée pour un serveur
        
        Args:
            guild_id: ID du serveur Discord
            
        Returns:
            Code de langue (ex: 'fr', 'en')
        """
        config = self.get_guild_config(guild_id)
        return config.get('language', 'fr')
    
    def set_guild_language(self, guild_id: int, language: str):
        """
        Définir la langue pour un serveur
        
        Args:
            guild_id: ID du serveur Discord
            language: Code de langue
        """
        self.update_guild_config(guild_id, {
            'language': language
        })
    
    def delete_guild_config(self, guild_id: int) -> bool:
        """
        Supprimer la configuration d'un serveur
        
        Args:
            guild_id: ID du serveur Discord
            
        Returns:
            True si supprimé avec succès
        """
        guild_str = str(guild_id)
        config_path = self._get_config_path(guild_str)
        
        try:
            if config_path.exists():
                config_path.unlink()
                logger.info(f"Configuration supprimée pour guild {guild_id}")
                return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la config {guild_id}: {e}")
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtenir les statistiques des configurations
        
        Returns:
            Dictionnaire des statistiques
        """
        configured_guilds = self.list_configured_guilds()
        configured_count = 0
        
        # Compter les guildes réellement configurées
        for guild_id in configured_guilds:
            config = self._load_guild_config(guild_id)
            if config and config.get('configured', False):
                configured_count += 1
        
        return {
            'total_configs': len(configured_guilds),
            'configured_guilds': configured_count,
            'unconfigured_guilds': len(configured_guilds) - configured_count,
            'config_directory': str(self.config_dir)
        }


# Instance globale du service
guild_service = GuildService()

# Alias pour compatibilité avec l'ancien code
guild_config = guild_service