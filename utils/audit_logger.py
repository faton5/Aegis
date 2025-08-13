"""
Système d'audit log transparent pour les actions de validation
Enregistre les actions des modérateurs sans exposer les reporters
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import json
from pathlib import Path

from config.logging_config import get_logger

logger = get_logger('audit_logger')


class AuditAction(Enum):
    """Types d'actions auditées"""
    REPORT_VALIDATED = "report_validated"
    REPORT_REJECTED = "report_rejected"
    USER_FLAGGED = "user_flagged"
    FLAG_REMOVED = "flag_removed"
    SETUP_GUILD = "setup_guild"
    PURGE_REPORTS = "purge_reports"


class AuditLogger:
    """Logger d'audit transparent pour les actions de modération"""
    
    def __init__(self, audit_dir: str = "audit_logs"):
        self.audit_dir = Path(audit_dir)
        self.audit_dir.mkdir(exist_ok=True)
        
    def _get_audit_file_path(self, guild_id: int) -> Path:
        """Obtenir le chemin du fichier d'audit pour un serveur"""
        date_str = datetime.utcnow().strftime("%Y-%m")
        return self.audit_dir / f"audit_{guild_id}_{date_str}.jsonl"
    
    async def log_action(self, 
                        action: AuditAction,
                        guild_id: int,
                        moderator_id: int,
                        moderator_name: str,
                        details: Dict[str, Any],
                        report_id: Optional[str] = None) -> bool:
        """
        Enregistrer une action dans l'audit log
        
        Args:
            action: Type d'action effectuée
            guild_id: ID du serveur Discord
            moderator_id: ID du modérateur qui a effectué l'action
            moderator_name: Nom du modérateur
            details: Détails de l'action (SANS informations sur le reporter)
            report_id: ID du signalement concerné (optionnel)
            
        Returns:
            True si succès
        """
        try:
            audit_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "action": action.value,
                "guild_id": guild_id,
                "moderator": {
                    "id": moderator_id,
                    "name": moderator_name
                },
                "report_id": report_id,
                "details": details
            }
            
            # Écrire dans le fichier d'audit (format JSONL pour faciliter le parsing)
            audit_file = self._get_audit_file_path(guild_id)
            
            with open(audit_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
            
            logger.info(f"📋 Action auditée: {action.value} par {moderator_name} dans guild {guild_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur enregistrement audit: {e}")
            return False
    
    async def log_report_validation(self,
                                  report_id: str,
                                  guild_id: int, 
                                  moderator_id: int,
                                  moderator_name: str,
                                  target_username: str,
                                  category: str,
                                  decision: bool,
                                  reason: str = "") -> bool:
        """
        Logger la validation/rejet d'un signalement
        
        Args:
            report_id: ID du signalement
            guild_id: ID du serveur
            moderator_id: ID du modérateur
            moderator_name: Nom du modérateur
            target_username: Utilisateur signalé
            category: Catégorie du signalement
            decision: True = validé, False = rejeté
            reason: Raison du modérateur (optionnel)
        """
        action = AuditAction.REPORT_VALIDATED if decision else AuditAction.REPORT_REJECTED
        
        details = {
            "target_username": target_username,
            "category": category,
            "decision": "approved" if decision else "rejected",
            "moderator_reason": reason,
            "validation_timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log_action(
            action=action,
            guild_id=guild_id,
            moderator_id=moderator_id,
            moderator_name=moderator_name,
            details=details,
            report_id=report_id
        )
    
    async def log_user_flagged(self,
                             guild_id: int,
                             moderator_id: int, 
                             moderator_name: str,
                             flagged_user_id: int,
                             flagged_username: str,
                             flag_level: int,
                             category: str) -> bool:
        """
        Logger l'ajout d'un flag officiel à un utilisateur
        
        Args:
            guild_id: ID du serveur
            moderator_id: ID du modérateur
            moderator_name: Nom du modérateur
            flagged_user_id: ID de l'utilisateur flagué
            flagged_username: Nom de l'utilisateur flagué
            flag_level: Niveau du flag assigné
            category: Catégorie du signalement validé
        """
        details = {
            "flagged_user": {
                "id": flagged_user_id,
                "username": flagged_username
            },
            "flag_level": flag_level,
            "category": category,
            "action_timestamp": datetime.utcnow().isoformat()
        }
        
        return await self.log_action(
            action=AuditAction.USER_FLAGGED,
            guild_id=guild_id,
            moderator_id=moderator_id,
            moderator_name=moderator_name,
            details=details
        )
    
    async def get_audit_history(self,
                              guild_id: int,
                              days: int = 30,
                              action_filter: Optional[AuditAction] = None) -> List[Dict[str, Any]]:
        """
        Récupérer l'historique d'audit d'un serveur
        
        Args:
            guild_id: ID du serveur
            days: Nombre de jours à récupérer
            action_filter: Filtrer par type d'action
            
        Returns:
            Liste des entrées d'audit
        """
        try:
            audit_entries = []
            
            # Parcourir les fichiers d'audit des derniers mois
            for month_offset in range((days // 30) + 2):  # +2 pour couvrir les mois partiels
                date = datetime.utcnow().replace(day=1) - timedelta(days=month_offset * 30)
                date_str = date.strftime("%Y-%m")
                audit_file = self.audit_dir / f"audit_{guild_id}_{date_str}.jsonl"
                
                if not audit_file.exists():
                    continue
                
                with open(audit_file, "r", encoding="utf-8") as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            entry_date = datetime.fromisoformat(entry["timestamp"])
                            
                            # Vérifier si dans la période demandée
                            if (datetime.utcnow() - entry_date).days <= days:
                                # Filtrer par action si demandé
                                if not action_filter or entry["action"] == action_filter.value:
                                    audit_entries.append(entry)
                                    
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.warning(f"Entrée d'audit malformée ignorée: {e}")
            
            # Trier par timestamp décroissant
            return sorted(audit_entries, key=lambda x: x["timestamp"], reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Erreur récupération audit: {e}")
            return []
    
    async def get_moderator_actions(self,
                                  guild_id: int,
                                  moderator_id: int,
                                  days: int = 30) -> List[Dict[str, Any]]:
        """
        Récupérer les actions d'un modérateur spécifique
        
        Args:
            guild_id: ID du serveur
            moderator_id: ID du modérateur
            days: Période à analyser
            
        Returns:
            Liste des actions du modérateur
        """
        all_entries = await self.get_audit_history(guild_id, days)
        return [entry for entry in all_entries if entry["moderator"]["id"] == moderator_id]
    
    def get_audit_stats(self, guild_id: int, days: int = 7) -> Dict[str, Any]:
        """
        Statistiques d'audit pour un serveur
        
        Args:
            guild_id: ID du serveur
            days: Période d'analyse
            
        Returns:
            Statistiques d'activité de modération
        """
        try:
            # Import local pour éviter les imports circulaires
            from datetime import timedelta
            
            # Cette méthode est synchrone pour les statistiques rapides
            stats = {
                "period_days": days,
                "total_actions": 0,
                "actions_by_type": {},
                "active_moderators": set(),
                "reports_processed": 0
            }
            
            # Pour une version complète, implémenter une version async
            # Pour l'instant, retourner les stats de base
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur calcul stats audit: {e}")
            return {"error": str(e)}


# Instance globale
audit_logger = AuditLogger()