# Client Supabase pour la base de données centralisée
import os
import asyncio
from typing import Optional, Dict, List, Any
from supabase import create_client, Client
from config.logging_config import get_logger
from config.bot_config import bot_settings

logger = get_logger('supabase')

class SupabaseClient:
    """Client pour interactions avec la base de données centralisée Supabase"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.is_connected = False
        
    async def connect(self) -> bool:
        """Se connecter à Supabase"""
        if not bot_settings.supabase_enabled:
            logger.info("Supabase désactivé dans la configuration")
            return False
            
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")
            
            if not supabase_url or not supabase_key:
                logger.error("Variables d'environnement Supabase manquantes")
                return False
                
            self.client = create_client(supabase_url, supabase_key)
            
            # Test de connexion avec nouvelle structure
            test_query = self.client.table("user_flags").select("id").limit(1).execute()
            
            self.is_connected = True
            logger.info("✅ Connexion Supabase établie")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion Supabase: {e}")
            self.is_connected = False
            return False
    
    async def check_user_flag(self, user_id: int, guild_id: int, guild_name: str = None) -> Optional[Dict]:
        """Vérifier si un utilisateur est flagué globalement avec nouveau système de niveaux"""
        if not self.is_connected:
            return None
            
        try:
            # Appeler la fonction SQL pour vérifier et logger (avec nettoyage automatique)
            result = self.client.rpc(
                "check_user_flag",
                {
                    "check_user_id": user_id,
                    "requesting_guild_id": guild_id,
                    "requesting_guild_name": guild_name or "Unknown"
                }
            ).execute()
            
            if result.data and len(result.data) > 0:
                flag_data = result.data[0]
                
                # Log avec nouveau format de niveaux
                if flag_data["is_flagged"]:
                    logger.info(f"🚩 Utilisateur {user_id} flagué: niveau {flag_data['current_level']} "
                              f"({flag_data['active_flags']}/{flag_data['total_flags']} flags actifs/total)")
                    
                    # Nettoyer les flags expirés si nécessaire
                    if flag_data.get("expired_flags_cleaned", 0) > 0:
                        logger.info(f"🧹 {flag_data['expired_flags_cleaned']} flags expirés nettoyés pour utilisateur {user_id}")
                
                return flag_data
                    
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification utilisateur {user_id}: {e}")
            return None
    
    async def add_validated_report(self, user_id: int, username: str, 
                                 reason: str, category: str, guild_id: int, guild_name: str) -> Dict[str, Any]:
        """Ajouter un signalement validé à la base centralisée (nouveau système sans level manuel)"""
        if not self.is_connected:
            return {"success": False, "error": "Not connected to Supabase"}
            
        try:
            # Utiliser la nouvelle fonction qui retourne plus d'informations
            result = self.client.rpc(
                "add_user_flag",
                {
                    "flag_user_id": user_id,
                    "flag_username": username,
                    "flag_reason": reason,
                    "flag_category": category,
                    "flagging_guild_id": guild_id,
                    "flagging_guild_name": guild_name
                }
            ).execute()
            
            # Gestion du retour de la nouvelle fonction
            if result.data and isinstance(result.data, list) and len(result.data) > 0:
                flag_result = result.data[0]  # La fonction retourne une table
                
                if flag_result.get('success'):
                    logger.info(f"✅ Flag ajouté: utilisateur {user_id}, niveau {flag_result.get('new_level')}, total: {flag_result.get('total_flags')}")
                    return {
                        "success": True,
                        "level": flag_result.get('new_level'),
                        "total_flags": flag_result.get('total_flags'),
                        "message": flag_result.get('message', 'Flag ajouté avec succès')
                    }
                else:
                    logger.warning(f"❌ Échec ajout flag: {flag_result.get('message')}")
                    return {"success": False, "error": flag_result.get('message', 'Erreur inconnue')}
            else:
                logger.error("Format de retour Supabase inattendu")
                return {"success": False, "error": "Format de retour inattendu"}
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du flag pour {user_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_guild_stats(self, guild_id: int, days: int = 30) -> Dict[str, Any]:
        """Obtenir les statistiques de vérification pour un serveur (nouveau format avec niveaux)"""
        if not self.is_connected:
            return {}
            
        try:
            # Utiliser la fonction RPC mise à jour
            result = self.client.rpc(
                "get_guild_stats",
                {
                    "guild_id_param": guild_id,
                    "days_param": days
                }
            ).execute()
            
            if result.data and len(result.data) > 0:
                stats = result.data[0]
                return {
                    "total_checks": stats.get("total_checks", 0),
                    "flagged_users_found": stats.get("flagged_users_found", 0),
                    "flags_created_by_guild": stats.get("flags_created_by_guild", 0),
                    "active_flagged_users": stats.get("active_flagged_users", 0),
                    "level_breakdown": stats.get("level_breakdown", {})
                }
                
            return {
                "total_checks": 0,
                "flagged_users_found": 0,
                "flags_created_by_guild": 0,
                "active_flagged_users": 0,
                "level_breakdown": {}
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats pour {guild_id}: {e}")
            return {}
    
    async def get_recent_flags(self, days: int = 7) -> List[Dict]:
        """Obtenir les flags récents pour surveillance"""
        if not self.is_connected:
            return []
            
        try:
            # Utiliser la fonction RPC du nouveau schéma
            result = self.client.rpc(
                "get_recent_flags",
                {"days_param": days}
            ).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des flags récents: {e}")
            return []
    
    async def save_report_anonymized(self, report_data: Dict[str, Any]) -> bool:
        """Sauvegarder un signalement de manière anonyme (sans ID du reporter)"""
        if not self.is_connected:
            return False
            
        try:
            result = self.client.rpc(
                "save_anonymous_report",
                {"report_data": report_data}
            ).execute()
            
            if result.data:
                logger.debug(f"Signalement anonyme sauvé: {report_data.get('id')}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde signalement anonyme: {e}")
            return False
    
    async def check_duplicate_report(self, uniqueness_hash: str) -> Optional[str]:
        """Vérifier l'existence d'un signalement en doublon"""
        if not self.is_connected:
            return None
            
        try:
            result = self.client.rpc(
                "check_duplicate_report",
                {"uniqueness_hash_param": uniqueness_hash}
            ).execute()
            
            return result.data if result.data else None
            
        except Exception as e:
            logger.error(f"Erreur vérification doublon: {e}")
            return None
    
    async def log_audit_action(self, action: str, guild_id: int, moderator_id: int, 
                              moderator_name: str, details: Dict[str, Any],
                              report_id: Optional[str] = None,
                              target_user_id: Optional[int] = None,
                              target_username: Optional[str] = None) -> bool:
        """Enregistrer une action d'audit"""
        if not self.is_connected:
            return False
            
        try:
            result = self.client.rpc(
                "log_audit_action",
                {
                    "action_param": action,
                    "guild_id_param": guild_id,
                    "moderator_id_param": moderator_id,
                    "moderator_name_param": moderator_name,
                    "report_id_param": report_id,
                    "target_user_id_param": target_user_id,
                    "target_username_param": target_username,
                    "details_param": details
                }
            ).execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Erreur enregistrement audit: {e}")
            return False

# Instance globale du client Supabase
supabase_client = SupabaseClient()