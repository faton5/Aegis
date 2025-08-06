"""
Système de limitation de taux pour Aegis
"""
from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict, deque

from config.logging_config import get_logger

logger = get_logger('rate_limiter')


class RateLimiter:
    """Gestionnaire de limitation de taux pour les actions utilisateurs"""
    
    def __init__(self, max_actions: int = 3, time_window: int = 3600):
        """
        Initialiser le rate limiter
        
        Args:
            max_actions: Nombre maximum d'actions par fenêtre
            time_window: Fenêtre de temps en secondes (défaut: 1 heure)
        """
        self.max_actions = max_actions
        self.time_window = time_window
        
        # Stockage des actions par utilisateur et serveur
        # Structure: {(user_id, guild_id): deque([timestamps...])}
        self.user_actions: Dict[tuple, deque] = defaultdict(deque)
        
        # Dernière action de nettoyage
        self.last_cleanup = datetime.utcnow()
        self.cleanup_interval = timedelta(hours=1)
    
    def check_rate_limit(self, user_id: int, guild_id: int = None) -> bool:
        """
        Vérifier si l'utilisateur peut effectuer une action
        
        Args:
            user_id: ID de l'utilisateur
            guild_id: ID du serveur (optionnel)
            
        Returns:
            True si l'action est autorisée
        """
        try:
            # Nettoyer périodiquement
            self._cleanup_if_needed()
            
            key = (user_id, guild_id)
            now = datetime.utcnow()
            cutoff_time = now - timedelta(seconds=self.time_window)
            
            # Nettoyer les anciennes entrées pour cet utilisateur
            actions = self.user_actions[key]
            while actions and actions[0] < cutoff_time:
                actions.popleft()
            
            # Vérifier si la limite est dépassée
            if len(actions) >= self.max_actions:
                logger.warning(f"Rate limit dépassé pour user {user_id} (guild {guild_id})")
                return False
            
            # Enregistrer l'action
            actions.append(now)
            return True
            
        except Exception as e:
            logger.error(f"Erreur dans check_rate_limit: {e}")
            return True  # En cas d'erreur, on autorise (fail-open)
    
    def get_remaining_time(self, user_id: int, guild_id: int = None) -> int:
        """
        Obtenir le temps restant avant la prochaine action autorisée
        
        Args:
            user_id: ID de l'utilisateur
            guild_id: ID du serveur
            
        Returns:
            Secondes restantes (0 si action autorisée)
        """
        key = (user_id, guild_id)
        actions = self.user_actions.get(key)
        
        if not actions or len(actions) < self.max_actions:
            return 0
        
        # Temps depuis la première action dans la fenêtre
        oldest_action = actions[0]
        time_since_oldest = (datetime.utcnow() - oldest_action).total_seconds()
        
        return max(0, int(self.time_window - time_since_oldest))
    
    def reset_user_limit(self, user_id: int, guild_id: int = None):
        """
        Réinitialiser la limite pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            guild_id: ID du serveur
        """
        key = (user_id, guild_id)
        if key in self.user_actions:
            del self.user_actions[key]
            logger.info(f"Rate limit réinitialisé pour user {user_id} (guild {guild_id})")
    
    def get_user_action_count(self, user_id: int, guild_id: int = None) -> int:
        """
        Obtenir le nombre d'actions récentes pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            guild_id: ID du serveur
            
        Returns:
            Nombre d'actions dans la fenêtre
        """
        key = (user_id, guild_id)
        actions = self.user_actions.get(key, deque())
        
        # Nettoyer les anciennes entrées
        now = datetime.utcnow()
        cutoff_time = now - timedelta(seconds=self.time_window)
        
        while actions and actions[0] < cutoff_time:
            actions.popleft()
            
        return len(actions)
    
    def _cleanup_if_needed(self):
        """Nettoyer les anciennes entrées si nécessaire"""
        now = datetime.utcnow()
        
        if now - self.last_cleanup < self.cleanup_interval:
            return
        
        self.last_cleanup = now
        cutoff_time = now - timedelta(seconds=self.time_window)
        
        # Nettoyer toutes les entrées expirées
        keys_to_remove = []
        
        for key, actions in self.user_actions.items():
            # Nettoyer les anciennes actions
            while actions and actions[0] < cutoff_time:
                actions.popleft()
            
            # Marquer les clés vides pour suppression
            if not actions:
                keys_to_remove.append(key)
        
        # Supprimer les clés vides
        for key in keys_to_remove:
            del self.user_actions[key]
        
        if keys_to_remove:
            logger.debug(f"Nettoyage rate limiter: {len(keys_to_remove)} entrées supprimées")
    
    def get_stats(self) -> Dict[str, int]:
        """Obtenir les statistiques du rate limiter"""
        return {
            'active_users': len(self.user_actions),
            'total_tracked_actions': sum(len(actions) for actions in self.user_actions.values()),
            'max_actions_per_window': self.max_actions,
            'time_window_seconds': self.time_window
        }