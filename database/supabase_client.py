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
            
            # Test de connexion
            test_query = self.client.table("flagged_users").select("id").limit(1).execute()
            
            self.is_connected = True
            logger.info("✅ Connexion Supabase établie")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion Supabase: {e}")
            self.is_connected = False
            return False
    
    async def check_user_flag(self, user_id: int, guild_id: int, guild_name: str = None) -> Optional[Dict]:
        """Vérifier si un utilisateur est flagué globalement"""
        if not self.is_connected:
            return None
            
        try:
            # Appeler la fonction SQL pour vérifier et logger
            result = self.client.rpc(
                "check_user_flag",
                {
                    "check_user_id": user_id,
                    "requesting_guild_id": guild_id,
                    "requesting_guild_name": guild_name
                }
            ).execute()
            
            if result.data and len(result.data) > 0:
                flag_data = result.data[0]
                if flag_data["is_flagged"]:
                    logger.info(f"🚩 Utilisateur {user_id} flagué: {flag_data['flag_level']}")
                    return flag_data
                    
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la vérification utilisateur {user_id}: {e}")
            return None
    
    async def add_validated_report(self, user_id: int, username: str, flag_level: str, 
                                 reason: str, category: str, guild_id: int, guild_name: str) -> bool:
        """Ajouter un signalement validé à la base centralisée"""
        if not self.is_connected:
            return False
            
        try:
            # Appeler la fonction SQL pour ajouter le flag
            result = self.client.rpc(
                "add_user_flag",
                {
                    "flag_user_id": user_id,
                    "flag_username": username,
                    "flag_level": flag_level,
                    "flag_reason": reason,
                    "flag_category": category,
                    "flagging_guild_id": guild_id,
                    "flagging_guild_name": guild_name
                }
            ).execute()
            
            if result.data:
                logger.info(f"✅ Flag ajouté pour utilisateur {user_id} (niveau: {flag_level})")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du flag pour {user_id}: {e}")
            return False
    
    async def get_guild_stats(self, guild_id: int) -> Dict[str, int]:
        """Obtenir les statistiques de vérification pour un serveur"""
        if not self.is_connected:
            return {}
            
        try:
            # Statistiques des requêtes
            query_stats = self.client.table("query_logs")\
                .select("flag_found")\
                .eq("querying_guild_id", guild_id)\
                .execute()
            
            total_checks = len(query_stats.data) if query_stats.data else 0
            flags_found = len([q for q in query_stats.data if q["flag_found"]]) if query_stats.data else 0
            
            # Statistiques des flags contribués
            contributed_flags = self.client.table("flagged_users")\
                .select("id")\
                .eq("flagged_by_guild_id", guild_id)\
                .execute()
            
            flags_contributed = len(contributed_flags.data) if contributed_flags.data else 0
            
            return {
                "total_checks": total_checks,
                "flags_found": flags_found,
                "flags_contributed": flags_contributed
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats pour {guild_id}: {e}")
            return {}
    
    async def get_recent_flags(self, limit: int = 10) -> List[Dict]:
        """Obtenir les flags récents pour surveillance"""
        if not self.is_connected:
            return []
            
        try:
            result = self.client.table("flagged_users")\
                .select("user_id, username, flag_level, flag_category, flagged_by_guild_name, created_at")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des flags récents: {e}")
            return []

# Instance globale du client Supabase
supabase_client = SupabaseClient()