"""
Modèle de données pour les signalements
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Report:
    """Modèle de données pour un signalement"""
    
    id: str
    guild_id: int
    reporter_id: int  # ATTENTION: Ne jamais stocker en base - seulement pour logique locale
    target_username: str
    category: str
    reason: str
    evidence: str = ""
    status: str = "pending"  # pending, validated, rejected
    target_user_id: Optional[int] = None  # ID Discord si disponible
    created_at: Optional[datetime] = None
    validated_by: Optional[int] = None
    validated_at: Optional[datetime] = None
    thread_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Champs pour l'anonymat et l'anti-abus
    reporter_hash: Optional[str] = None  # Hash anonyme du reporter
    uniqueness_hash: Optional[str] = None  # Hash pour détecter doublons
    
    def __post_init__(self):
        """Initialisation post-création"""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
    
    @property
    def is_validated(self) -> bool:
        """Vérifier si le signalement est validé"""
        return self.status == "validated"
    
    @property
    def is_pending(self) -> bool:
        """Vérifier si le signalement est en attente"""
        return self.status == "pending"
    
    @property
    def age_hours(self) -> float:
        """Âge du signalement en heures"""
        if not self.created_at:
            return 0
        return (datetime.utcnow() - self.created_at).total_seconds() / 3600
    
    def to_dict(self, include_reporter_id: bool = False) -> Dict[str, Any]:
        """
        Convertir en dictionnaire pour stockage
        
        Args:
            include_reporter_id: Si True, inclut l'ID du reporter (DANGEREUX - seulement pour usage local)
        """
        data = {
            'id': self.id,
            'guild_id': self.guild_id,
            'target_username': self.target_username,
            'target_user_id': self.target_user_id,
            'category': self.category,
            'reason': self.reason,
            'evidence': self.evidence,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'validated_by': self.validated_by,
            'validated_at': self.validated_at.isoformat() if self.validated_at else None,
            'thread_id': self.thread_id,
            'metadata': self.metadata,
            'reporter_hash': self.reporter_hash,
            'uniqueness_hash': self.uniqueness_hash
        }
        
        # ATTENTION: N'inclure l'ID du reporter que pour usage local temporaire
        if include_reporter_id:
            data['reporter_id'] = self.reporter_id
            
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Report':
        """Créer un Report depuis un dictionnaire"""
        # Convertir les timestamps ISO en datetime
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
            
        validated_at = None
        if data.get('validated_at'):
            validated_at = datetime.fromisoformat(data['validated_at'])
        
        return cls(
            id=data['id'],
            guild_id=data['guild_id'],
            reporter_id=data.get('reporter_id', 0),  # Par défaut 0 si pas présent (anonymisé)
            target_username=data['target_username'],
            target_user_id=data.get('target_user_id'),
            category=data['category'],
            reason=data['reason'],
            evidence=data.get('evidence', ''),
            status=data.get('status', 'pending'),
            created_at=created_at,
            validated_by=data.get('validated_by'),
            validated_at=validated_at,
            thread_id=data.get('thread_id'),
            metadata=data.get('metadata', {}),
            reporter_hash=data.get('reporter_hash'),
            uniqueness_hash=data.get('uniqueness_hash')
        )