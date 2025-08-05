# Configuration par serveur pour Aegis
import json
import os
from typing import Dict, Any, Optional
from utils import logger

class GuildConfigManager:
    """Gestionnaire de configuration par serveur"""
    
    def __init__(self):
        self.config_dir = "guild_configs"
        self.old_config_file = "guild_configs.json"
        # Créer le dossier s'il n'existe pas
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        # Migrer l'ancien fichier s'il existe
        self._migrate_old_config()
    
    def _migrate_old_config(self):
        """Migre l'ancien fichier guild_configs.json vers des fichiers séparés"""
        if os.path.exists(self.old_config_file):
            try:
                with open(self.old_config_file, 'r', encoding='utf-8') as f:
                    old_configs = json.load(f)
                
                # Créer un fichier pour chaque serveur
                for guild_id, config in old_configs.items():
                    self._save_guild_config(guild_id, config)
                
                # Renommer l'ancien fichier pour backup
                backup_name = f"{self.old_config_file}.backup"
                os.rename(self.old_config_file, backup_name)
                logger.info(f"Migration terminée. Ancien fichier sauvé en {backup_name}")
                
            except Exception as e:
                logger.error(f"Erreur lors de la migration: {e}")
    
    def _get_config_path(self, guild_id: str) -> str:
        """Obtient le chemin du fichier de config pour un serveur"""
        return os.path.join(self.config_dir, f"{guild_id}.json")
    
    def _load_guild_config(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Charge la configuration d'un serveur depuis son fichier"""
        config_path = self._get_config_path(guild_id)
        try:
            if os.path.exists(config_path):
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
        """Obtenir la configuration d'un serveur"""
        guild_str = str(guild_id)
        config = self._load_guild_config(guild_str)
        
        if config is None:
            # Créer la config par défaut
            config = self.get_default_config()
            self._save_guild_config(guild_str, config)
        
        return config
    
    def update_guild_config(self, guild_id: int, updates: Dict[str, Any]):
        """Mettre à jour la configuration d'un serveur"""
        guild_str = str(guild_id)
        config = self.get_guild_config(guild_id)  # Charge ou crée la config
        config.update(updates)
        self._save_guild_config(guild_str, config)
    
    def list_configured_guilds(self) -> list[str]:
        """Liste tous les serveurs ayant une configuration"""
        if not os.path.exists(self.config_dir):
            return []
        
        guild_ids = []
        for filename in os.listdir(self.config_dir):
            if filename.endswith('.json'):
                guild_ids.append(filename[:-5])  # Enlever .json
        return guild_ids
    
    def get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut pour un nouveau serveur"""
        return {
            # Actions automatiques par niveau de flag
            "auto_actions": {
                "critical": "ban",      # ban, kick, quarantine, alert, none
                "high": "quarantine",   
                "medium": "alert",      
                "low": "none"
            },
            
            # Paramètres de quarantaine
            "quarantine": {
                "enabled": True,
                "role_name": "Quarantaine Aegis",
                "duration_hours": 24,
                "remove_roles": True,  # Enlever tous les autres rôles
                "restricted_channels": []  # Canaux accessibles en quarantaine
            },
            
            # Seuils et limites
            "thresholds": {
                "auto_action_min_validations": 2,  # Minimum de validations pour auto-action
                "alert_admins_on_critical": True,
                "alert_admins_on_high": False,
                "require_manual_review_for_ban": True
            },
            
            # Canaux de notification
            "channels": {
                "flag_alerts": None,        # Canal pour alertes de flags
                "critical_alerts": None,    # Canal pour flags critiques uniquement
                "ban_logs": None,          # Canal pour logs de bannissements
                "admin_notifications": None # Canal pour notifications admin
            },
            
            # Notifications
            "notifications": {
                "dm_admins_on_critical": True,
                "ping_admins_on_critical": True,
                "webhook_url": None  # Webhook Discord pour notifications externes
            },
            
            # Permissions
            "permissions": {
                "check_command_roles": ["Validateur"],  # Rôles autorisés pour /check
                "config_command_roles": ["Administrateur"],  # Rôles pour config avancée
                "bypass_auto_actions": ["Modérateur", "Administrateur"]  # Rôles exempts
            },
            
            # Journalisation
            "logging": {
                "log_all_checks": False,      # Logger toutes les vérifications
                "log_auto_actions": True,     # Logger les actions automatiques
                "retention_days": 30          # Durée de conservation des logs
            }
        }

# Instance globale
guild_config = GuildConfigManager()