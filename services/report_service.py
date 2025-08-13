"""
Service de gestion des signalements
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import uuid

from config.logging_config import get_logger
from config.bot_config import ERROR_MESSAGES
from utils.security import SecurityValidator
from utils.rate_limiter import RateLimiter
from utils.anonymous_hasher import anonymous_hasher
from database.models.report import Report

logger = get_logger('report_service')


class ReportService:
    """Service principal pour la gestion des signalements"""
    
    def __init__(self, db_client=None, validator: SecurityValidator = None, rate_limiter: RateLimiter = None):
        self.db = db_client
        self.validator = validator or SecurityValidator()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.active_reports: Dict[str, Report] = {}
        
        # Cache des hash d'unicité pour détection de doublons rapide
        self.uniqueness_cache: Dict[str, str] = {}  # {uniqueness_hash: report_id}
        
    async def create_report(self, 
                          user_id: int, 
                          guild_id: int, 
                          target_username: str,
                          category: str,
                          reason: str,
                          evidence: str = "",
                          target_user_id: int = None) -> Optional[Report]:
        """
        Créer un nouveau signalement avec système anti-abus anonyme
        
        Args:
            user_id: ID de l'utilisateur qui signale
            guild_id: ID du serveur Discord
            target_username: Nom d'utilisateur signalé
            category: Catégorie du signalement
            reason: Raison du signalement
            evidence: Preuves (optionnel)
            target_user_id: ID Discord de l'utilisateur signalé (si disponible)
            
        Returns:
            Report créé ou None si échec (doublon, rate limit, etc.)
        """
        try:
            # 1. Vérifier que le service de hachage est disponible
            if not anonymous_hasher.is_configured():
                logger.error("Service de hachage anonyme non configuré")
                return None
            
            # 2. Vérifier le rate limiting
            if not self.rate_limiter.check_rate_limit(user_id, guild_id):
                logger.warning(f"Rate limit dépassé pour user {user_id} sur guild {guild_id}")
                return None
            
            # 3. Valider les entrées
            if not self.validator.validate_input(target_username, max_length=32):
                logger.warning(f"Username invalide: {target_username}")
                return None
                
            if not self.validator.validate_input(reason, max_length=500):
                logger.warning(f"Raison invalide pour user {user_id}")
                return None
            
            # 4. Générer les hash anonymes
            reporter_hash = anonymous_hasher.generate_reporter_hash(user_id, guild_id)
            uniqueness_hash = anonymous_hasher.generate_report_uniqueness_hash(user_id, guild_id, target_username)
            
            if not reporter_hash or not uniqueness_hash:
                logger.error("Erreur génération des hash anonymes")
                return None
            
            # 5. Vérifier les doublons
            duplicate_report_id = await self._check_duplicate_report(uniqueness_hash)
            if duplicate_report_id:
                logger.info(f"Doublon détecté: utilisateur a déjà signalé '{target_username}' dans guild {guild_id}")
                return None
            
            # 6. Créer le signalement avec hash anonymes
            report = Report(
                id=self._generate_report_id(),
                guild_id=guild_id,
                reporter_id=user_id,  # Gardé temporairement pour la logique locale seulement
                target_username=self.validator.sanitize_input(target_username),
                target_user_id=target_user_id,
                category=category,
                reason=self.validator.sanitize_input(reason),
                evidence=self.validator.sanitize_input(evidence),
                created_at=datetime.utcnow(),
                reporter_hash=reporter_hash,
                uniqueness_hash=uniqueness_hash
            )
            
            # 7. Sauvegarder localement
            self.active_reports[report.id] = report
            self.uniqueness_cache[uniqueness_hash] = report.id
            
            # 8. Enregistrer dans la DB (SANS l'ID du reporter)
            if self.db and hasattr(self.db, 'save_report'):
                # Créer une copie anonymisée pour la DB
                anonymized_data = report.to_dict(include_reporter_id=False)
                await self.db.save_report_anonymized(anonymized_data)
            
            logger.info(f"✅ Signalement anonyme créé: {report.id} dans guild {guild_id}")
            logger.debug(f"Hash reporter: {reporter_hash[:8]}... Hash unicité: {uniqueness_hash[:8]}...")
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
        import time
        
        # Générer un ID et vérifier qu'il n'existe pas déjà
        max_attempts = 10
        for _ in range(max_attempts):
            # Combinaison timestamp + uuid pour plus d'unicité
            timestamp_part = hex(int(time.time() * 1000000))[-6:].upper()  # 6 chars du timestamp
            uuid_part = str(uuid.uuid4())[:2].upper()  # 2 chars de l'UUID
            report_id = timestamp_part + uuid_part
            
            # Vérifier que l'ID n'existe pas
            if report_id not in self.active_reports:
                return report_id
        
        # Fallback si collision (très improbable)
        return str(uuid.uuid4()).replace('-', '').upper()[:8]
    
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
    
    async def _check_duplicate_report(self, uniqueness_hash: str) -> Optional[str]:
        """
        Vérifier si un signalement avec le même hash d'unicité existe déjà
        
        Args:
            uniqueness_hash: Hash d'unicité à vérifier
            
        Returns:
            ID du rapport existant ou None si pas de doublon
        """
        # Vérifier dans le cache local
        cached_report_id = self.uniqueness_cache.get(uniqueness_hash)
        if cached_report_id and cached_report_id in self.active_reports:
            return cached_report_id
        
        # Vérifier dans la base de données si disponible
        if self.db and hasattr(self.db, 'check_duplicate_report'):
            try:
                existing_report_id = await self.db.check_duplicate_report(uniqueness_hash)
                if existing_report_id:
                    # Mettre à jour le cache
                    self.uniqueness_cache[uniqueness_hash] = existing_report_id
                    return existing_report_id
            except Exception as e:
                logger.error(f"Erreur vérification doublon en DB: {e}")
        
        return None
    
    def check_duplicate_by_hash(self, uniqueness_hash: str) -> bool:
        """
        Vérification synchrone de doublon (pour les erreurs utilisateur)
        
        Args:
            uniqueness_hash: Hash d'unicité à vérifier
            
        Returns:
            True si c'est un doublon
        """
        return uniqueness_hash in self.uniqueness_cache
    
    def get_anti_abuse_stats(self) -> Dict[str, Any]:
        """Statistiques du système anti-abus"""
        return {
            'total_reports': len(self.active_reports),
            'uniqueness_cache_size': len(self.uniqueness_cache),
            'anonymous_hasher_configured': anonymous_hasher.is_configured(),
            'anonymous_hasher_info': anonymous_hasher.get_security_info()
        }