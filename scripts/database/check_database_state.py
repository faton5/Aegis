#!/usr/bin/env python3
"""
Script de vérification de l'état de la base de données Supabase
"""
import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

async def check_database_state():
    """Vérifier l'état actuel de la base de données"""
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Variables d'environnement Supabase manquantes")
        return
    
    try:
        client = create_client(supabase_url, supabase_key)
        print("✅ Client Supabase créé")
        
        # Vérifier les tables existantes
        tables_to_check = [
            "user_flags",      # Nouvelle structure
            "access_logs",     # Nouvelle structure
            "flagged_users",   # Ancienne structure
            "query_logs"       # Ancienne structure
        ]
        
        existing_tables = []
        missing_tables = []
        
        for table_name in tables_to_check:
            try:
                result = client.table(table_name).select("id").limit(1).execute()
                existing_tables.append(table_name)
                count = len(result.data) if result.data else 0
                print(f"✅ Table '{table_name}' existe (test: {count} entrées)")
            except Exception as e:
                missing_tables.append(table_name)
                print(f"❌ Table '{table_name}' n'existe pas: {str(e)[:100]}")
        
        print("\n" + "="*50)
        print("📊 RÉSUMÉ DE L'ÉTAT:")
        
        if "user_flags" in existing_tables and "access_logs" in existing_tables:
            print("🎉 NOUVELLE STRUCTURE: Base de données déjà migrée")
            
            # Tester les fonctions RPC
            print("\n🔧 Test des fonctions RPC:")
            try:
                # Test check_user_flag
                result = client.rpc("check_user_flag", {
                    "check_user_id": 123456789,
                    "requesting_guild_id": 987654321,
                    "requesting_guild_name": "Test Server"
                }).execute()
                print("✅ Fonction check_user_flag OK")
                
                # Test get_guild_stats
                result = client.rpc("get_guild_stats", {
                    "guild_id_param": 987654321,
                    "days_param": 30
                }).execute()
                print("✅ Fonction get_guild_stats OK")
                
                # Test get_recent_flags
                result = client.rpc("get_recent_flags", {
                    "days_param": 7
                }).execute()
                print("✅ Fonction get_recent_flags OK")
                
            except Exception as e:
                print(f"❌ Erreur fonctions RPC: {e}")
                print("👉 Les fonctions RPC doivent être créées")
            
        elif "flagged_users" in existing_tables:
            print("⚠️  ANCIENNE STRUCTURE: Migration nécessaire")
            print("👉 Exécutez le script 'database/migration_update.sql' dans Supabase")
            
        else:
            print("🆕 BASE VIERGE: Première installation nécessaire") 
            print("👉 Exécutez le script 'database/supabase_schema.sql' dans Supabase")
        
        print("\n📋 ACTIONS RECOMMANDÉES:")
        if missing_tables:
            print("1. Ouvrir l'éditeur SQL Supabase")
            print("2. Copier/coller le contenu de 'database/migration_update.sql'")
            print("3. Exécuter le script")
            print("4. Relancer ce test pour vérifier")
        else:
            print("✅ Aucune action nécessaire - Base de données à jour")
            
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")

if __name__ == "__main__":
    asyncio.run(check_database_state())