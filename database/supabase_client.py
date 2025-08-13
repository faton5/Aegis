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
            # Appel direct Supabase (contournement temporaire du problème de format)
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
            
            # Gestion directe du retour Supabase
            if result.data and isinstance(result.data, dict):
                flag_result = result.data
                
                if flag_result.get("success"):
                    logger.info(f"✅ Flag ajouté pour utilisateur {user_id} - "
                              f"Nouveau niveau: {flag_result.get('new_level', 'unknown')} "
                              f"({flag_result.get('new_active_flags', 0)} flags actifs)")
                    return flag_result
                else:
                    logger.error(f"❌ Échec ajout flag: {flag_result.get('error', 'Unknown error')}")
                    return flag_result
            else:
                logger.error(f"❌ Retour inattendu de Supabase: {result.data} (type: {type(result.data)})")
                return {"success": False, "error": f"Unexpected Supabase response: {result.data}"}
            
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

# Instance globale du client Supabase
supabase_client = SupabaseClient()