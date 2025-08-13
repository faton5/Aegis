#!/usr/bin/env python3
"""
Script de debug pour vérifier et nettoyer les flags utilisateurs
"""
import asyncio
import sys
sys.path.insert(0, '.')

from database.supabase_client import supabase_client

async def debug_user_flags():
    print("=== DEBUG FLAGS UTILISATEURS ===\n")
    
    connected = await supabase_client.connect()
    if not connected:
        print("Echec connexion Supabase")
        return
    
    print("✅ Connexion OK\n")
    
    # Demander l'ID utilisateur à vérifier
    user_id = input("ID utilisateur à vérifier (ou ENTER pour voir tous les flags): ")
    
    if user_id.strip():
        # Vérifier un utilisateur spécifique
        print(f"\n--- Vérification utilisateur {user_id} ---")
        result = await supabase_client.check_user_flag(int(user_id), 999, "Debug Server")
        
        if result:
            print(f"Flagué: {result['is_flagged']}")
            print(f"Niveau: {result['current_level']}")
            print(f"Flags actifs: {result['active_flags']}")
            print(f"Total flags: {result['total_flags']}")
            print(f"Historique: {result['flag_history']}")
            
            if result.get('expired_flags_cleaned', 0) > 0:
                print(f"Flags expirés nettoyés: {result['expired_flags_cleaned']}")
        else:
            print("Utilisateur propre (pas de flags)")
    else:
        # Voir tous les utilisateurs flagués
        print("--- Tous les utilisateurs flagués ---")
        flags = await supabase_client.get_recent_flags(365)  # 1 an
        
        if flags:
            for flag in flags:
                print(f"User {flag['user_id']} ({flag['username']}): "
                      f"{flag['current_level']} - {flag['active_flags']} flags actifs")
        else:
            print("Aucun utilisateur flagué trouvé")

if __name__ == "__main__":
    asyncio.run(debug_user_flags())