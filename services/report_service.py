"""
Service de gestion des signalements
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid

from config.logging_config import get_logger
from utils.security import SecurityValidator
from utils.rate_limiter import RateLimiter
from database.models.report import Report

logger = get_logger('report_service')


class ReportService:
    """Service principal pour la gestion des signalements"""
    
    def __init__(self, db_client=None, validator: SecurityValidator = None, rate_limiter: RateLimiter = None):
        self.db = db_client
        self.validator = validator or SecurityValidator()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.active_reports: Dict[str, Report] = {}
        
    async def create_report(self, 
                          user_id: int, 
                          guild_id: int, 
                          target_username: str,
                          category: str,
                          reason: str,
                          evidence: str = "") -> Optional[Report]:
        """
        Créer un nouveau signalement
        
        Args:
            user_id: ID de l'utilisateur qui signale
            guild_id: ID du serveur Discord
            target_username: Nom d'utilisateur signalé
            category: Catégorie du signalement
            reason: Raison du signalement
            evidence: Preuves (optionnel)
            
        Returns:
            Report créé ou None si échec
        """
        try:
            # Vérifier le rate limiting
            if not self.rate_limiter.check_rate_limit(user_id, guild_id):
                logger.warning(f"Rate limit dépassé pour user {user_id} sur guild {guild_id}")
                return None
            
            # Valider les entrées
            if not self.validator.validate_input(target_username, max_length=32):
                logger.warning(f"Username invalide: {target_username}")
                return None
                
            if not self.validator.validate_input(reason, max_length=500):
                logger.warning(f"Raison invalide pour user {user_id}")
                return None
            
            # Créer le signalement
            report = Report(
                id=self._generate_report_id(),
                guild_id=guild_id,
                reporter_id=user_id,
                target_username=self.validator.sanitize_input(target_username),
                category=category,
                reason=self.validator.sanitize_input(reason),
                evidence=self.validator.sanitize_input(evidence),
                created_at=datetime.utcnow()
            )
            
            # Sauvegarder
            self.active_reports[report.id] = report
            
            # Enregistrer dans la DB si disponible
            if self.db and hasattr(self.db, 'save_report'):
                await self.db.save_report(report)
            
            logger.info(f"Signalement créé: {report.id} par user {user_id}")
            return report
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du signalement: {e}")
            return None
    
    async def get_report(self, report_id: str) -> Optional[Report]:
        """Récupérer un signalement par ID"""
        return self.active_reports.get(report_id)
    
    async def update_report_status(self, report_id: str, status: str, validator_id: int = None) -> bool:
        """
        Mettre à jour le statut d'un signalement
        
        Args:
            report_id: ID du signalement
            status: Nouveau statut
            validator_id: ID du validateur (optionnel)
            
        Returns:
            True si succès
        """
        try:
            report = self.active_reports.get(report_id)
            if not report:
                return False
                
            report.status = status
            if validator_id:
                report.validated_by = validator_id
                report.validated_at = datetime.utcnow()
            
            # Mettre à jour en DB
            if self.db and hasattr(self.db, 'update_report'):
                await self.db.update_report(report)
            
            logger.info(f"Signalement {report_id} mis à jour: statut={status}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du signalement {report_id}: {e}")
            return False
    
    async def get_guild_reports(self, guild_id: int, status: str = None) -> List[Report]:
        """
        Récupérer tous les signalements d'un serveur
        
        Args:
            guild_id: ID du serveur
            status: Filtrer par statut (optionnel)
            
        Returns:
            Liste des signalements
        """
        reports = [r for r in self.active_reports.values() if r.guild_id == guild_id]
        
        if status:
            reports = [r for r in reports if r.status == status]
            
        return sorted(reports, key=lambda r: r.created_at, reverse=True)
    
    def _generate_report_id(self) -> str:
        """Générer un ID unique pour un signalement"""
        return str(uuid.uuid4())[:8].upper()
    
    async def cleanup_old_reports(self, days: int = 30):
        """Nettoyer les anciens signalements"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_reports = [
            report_id for report_id, report in self.active_reports.items()
            if report.created_at < cutoff_date and report.status in ['validated', 'rejected']
        ]
        
        for report_id in old_reports:
            del self.active_reports[report_id]
            
        if old_reports:
            logger.info(f"Nettoyage: {len(old_reports)} anciens signalements supprimés")