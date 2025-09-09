# Client Supabase pour la nouvelle structure de base de données
import os
import asyncio
from typing import Optional, Dict, List, Any
from supabase import create_client, Client
from config.logging_config import get_logger
from config.bot_config import bot_settings

logger = get_logger('supabase')

class SupabaseClientNew:
    """Client pour interactions avec la nouvelle structure DB Supabase"""
    
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
            test_query = self.client.table("reports").select("id").limit(1).execute()
            
            self.is_connected = True
            logger.info("✅ Connexion Supabase établie")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur connexion Supabase: {e}")
            self.is_connected = False
            return False
    
    async def check_user(self, user_id: int, guild_id: int, guild_name: str = None) -> Optional[Dict]:
        """Vérifier un utilisateur avec la nouvelle structure DB"""
        if not self.is_connected:
            return None
            
        try:
            # Log de l'activité check
            await self._log_activity("check", user_id, None, guild_id, {"checked_user": user_id})
            
            # Chercher l'utilisateur dans la table users
            user_result = self.client.table("users").select("*").eq("user_id", user_id).execute()
            
            if not user_result.data:
                # Utilisateur propre (pas dans la DB)
                return {
                    "is_flagged": False,
                    "risk_level": "clean",
                    "total_flags": 0,
                    "active_flags": 0,
                    "last_flagged_at": None,
                    "last_flagged_guild": None,
                    "expires_at": None
                }
            
            user_data = user_result.data[0]
            
            # Récupérer les rapports récents pour cet utilisateur
            reports_result = self.client.table("reports").select("*").eq("target_user_id", user_id).eq("status", "validated").execute()
            
            return {
                "is_flagged": user_data.get("total_flags", 0) > 0,
                "risk_level": user_data.get("risk_level", "clean"),
                "total_flags": user_data.get("total_flags", 0),
                "active_flags": user_data.get("active_flags", 0),
                "last_flagged_at": user_data.get("last_flagged_at"),
                "last_flagged_guild": user_data.get("last_flagged_guild"),
                "expires_at": user_data.get("expires_at"),
                "reports": reports_result.data if reports_result.data else []
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur check_user: {e}")
            return None
    
    async def add_report(self, target_user_id: int, target_username: str, reason: str, 
                        category: str, guild_id: int, guild_name: str, 
                        reporter_hash: str, uniqueness_hash: str) -> Optional[Dict]:
        """Ajouter un nouveau signalement"""
        if not self.is_connected:
            return None
            
        try:
            # Générer un ID unique pour le rapport
            import uuid
            report_id = str(uuid.uuid4())
            
            # Insérer le rapport
            report_data = {
                "id": report_id,
                "target_user_id": target_user_id,
                "target_username": target_username,
                "category": category,
                "reason": reason,
                "guild_id": guild_id,
                "guild_name": guild_name,
                "reporter_hash": reporter_hash,
                "uniqueness_hash": uniqueness_hash,
                "status": "pending"
            }
            
            result = self.client.table("reports").insert(report_data).execute()
            
            if result.data:
                # Log de l'activité
                await self._log_activity("report", None, target_username, guild_id, {
                    "target_user_id": target_user_id,
                    "category": category,
                    "report_id": report_id
                })
                
                # Mettre à jour les stats du serveur
                await self._update_server_stats(guild_id, guild_name, "report")
                
                return {"success": True, "report_id": report_id}
            
            return {"success": False, "error": "Échec insertion"}
            
        except Exception as e:
            logger.error(f"❌ Erreur add_report: {e}")
            return {"success": False, "error": str(e)}
    
    async def validate_report(self, report_id: str, validator_id: int, status: str) -> bool:
        """Valider ou rejeter un signalement"""
        if not self.is_connected:
            return False
            
        try:
            # Mettre à jour le statut du rapport
            result = self.client.table("reports").update({
                "status": status,
                "validated_by": validator_id,
                "validated_at": "now()"
            }).eq("id", report_id).execute()
            
            if result.data and status == "validated":
                # Si validé, mettre à jour l'utilisateur flagué
                report = result.data[0]
                await self._update_user_flags(
                    report["target_user_id"], 
                    report["target_username"],
                    report["guild_name"]
                )
            
            # Log de l'activité
            await self._log_activity(status, validator_id, None, result.data[0]["guild_id"] if result.data else 0, {
                "report_id": report_id,
                "target_user_id": result.data[0]["target_user_id"] if result.data else 0
            })
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"❌ Erreur validate_report: {e}")
            return False

    async def update_report(self, report) -> bool:
        """Compatibilité: met à jour un rapport à partir de l'objet Report.
        Redirige vers validate_report du nouveau client.
        """
        try:
            if not self.is_connected:
                return False
            report_id = getattr(report, 'id', None)
            status = getattr(report, 'status', 'pending')
            validator_id = getattr(report, 'validated_by', 0) or 0
            if not report_id:
                return False
            return await self.validate_report(report_id=report_id, validator_id=validator_id, status=status)
        except Exception as e:
            logger.error(f"Erreur update_report (shim compat): {e}")
            return False
    
    async def add_validated_report(self, user_id: int, username: str,
                                   reason: str, category: str,
                                   guild_id: int, guild_name: str) -> dict:
        """Compat: méthode legacy appelée par certaines vues.
        Le flux officiel passe par validate_report; on renvoie un succès neutre
        pour éviter les doubles insertions et garder la compatibilité UI.
        """
        try:
            logger.info("Compat add_validated_report: géré via validate_report/update_report.")
            # Optionnel: recalculer les flags utilisateur si ID fourni
            if user_id:
                await self._update_user_flags(user_id=user_id, username=username, guild_name=guild_name)
            return {"success": True, "new_level": "", "new_active_flags": 0}
        except Exception as e:
            logger.error(f"Erreur compat add_validated_report: {e}")
            return {"success": False, "error": str(e)}

    async def get_guild_stats(self, guild_id: int, days: int = 30) -> Optional[Dict]:
        """Obtenir les statistiques d'un serveur"""
        if not self.is_connected:
            return None
            
        try:
            # Stats du serveur depuis la table servers
            server_result = self.client.table("servers").select("*").eq("guild_id", guild_id).execute()
            
            # Stats d'activité récente
            from datetime import datetime, timedelta
            since_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            activity_result = self.client.table("activity").select("*").eq("guild_id", guild_id).gte("created_at", since_date).execute()
            
            # Compter par type d'action
            activity_counts = {}
            for activity in activity_result.data if activity_result.data else []:
                action = activity.get("action", "unknown")
                activity_counts[action] = activity_counts.get(action, 0) + 1
            
            server_data = server_result.data[0] if server_result.data else {}
            
            return {
                "guild_id": guild_id,
                "total_reports": server_data.get("total_reports", 0),
                "total_checks": server_data.get("total_checks", 0),
                "flags_found": server_data.get("flags_found", 0),
                "first_seen": server_data.get("first_seen"),
                "last_active": server_data.get("last_active"),
                "recent_activity": activity_counts,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur get_guild_stats: {e}")
            return None
    
    async def _update_user_flags(self, user_id: int, username: str, guild_name: str):
        """Mettre à jour les flags d'un utilisateur après validation"""
        try:
            # Compter les rapports validés pour cet utilisateur
            reports_result = self.client.table("reports").select("*").eq("target_user_id", user_id).eq("status", "validated").execute()
            
            total_flags = len(reports_result.data) if reports_result.data else 0
            
            # Calculer le niveau de risque
            if total_flags == 0:
                risk_level = "clean"
            elif total_flags == 1:
                risk_level = "low"
            elif total_flags <= 3:
                risk_level = "medium"
            elif total_flags <= 5:
                risk_level = "high"
            else:
                risk_level = "critical"
            
            # Upsert dans la table users
            user_data = {
                "user_id": user_id,
                "username": username,
                "risk_level": risk_level,
                "total_flags": total_flags,
                "active_flags": total_flags,  # Pour l'instant tous actifs
                "last_flagged_at": "now()",
                "last_flagged_guild": guild_name,
                "updated_at": "now()"
            }
            
            self.client.table("users").upsert(user_data).execute()
            
        except Exception as e:
            logger.error(f"❌ Erreur _update_user_flags: {e}")
    
    async def _update_server_stats(self, guild_id: int, guild_name: str, action: str):
        """Mettre à jour les statistiques du serveur"""
        try:
            # Récupérer ou créer l'entrée serveur
            server_result = self.client.table("servers").select("*").eq("guild_id", guild_id).execute()
            
            if server_result.data:
                # Mettre à jour
                updates = {"last_active": "now()"}
                if action == "report":
                    updates["total_reports"] = server_result.data[0].get("total_reports", 0) + 1
                elif action == "check":
                    updates["total_checks"] = server_result.data[0].get("total_checks", 0) + 1
                
                self.client.table("servers").update(updates).eq("guild_id", guild_id).execute()
            else:
                # Créer nouvelle entrée
                server_data = {
                    "guild_id": guild_id,
                    "guild_name": guild_name,
                    "total_reports": 1 if action == "report" else 0,
                    "total_checks": 1 if action == "check" else 0,
                    "flags_found": 0
                }
                self.client.table("servers").insert(server_data).execute()
                
        except Exception as e:
            logger.error(f"❌ Erreur _update_server_stats: {e}")
    
    async def _log_activity(self, action: str, user_id: Optional[int], username: Optional[str], 
                          guild_id: int, result: Dict):
        """Logger une activité dans la table activity"""
        try:
            activity_data = {
                "action": action,
                "user_id": user_id,
                "username": username,
                "guild_id": guild_id,
                "result": result
            }
            
            self.client.table("activity").insert(activity_data).execute()
            
        except Exception as e:
            logger.error(f"❌ Erreur _log_activity: {e}")

# Instance globale
supabase_client_new = SupabaseClientNew()
