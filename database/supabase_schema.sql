-- Schema et fonctions Supabase pour Aegis Bot
-- Ce fichier doit être exécuté dans l'éditeur SQL Supabase

-- ====================================
-- 1. Création de la table user_flags
-- ====================================

CREATE TABLE IF NOT EXISTS user_flags (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username TEXT NOT NULL,
    flag_level TEXT NOT NULL CHECK (flag_level IN ('low', 'medium', 'high', 'critical')),
    flag_reason TEXT NOT NULL,
    flag_category TEXT NOT NULL,
    flagging_guild_id BIGINT NOT NULL,
    flagging_guild_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_user_flags_user_id ON user_flags(user_id);
CREATE INDEX IF NOT EXISTS idx_user_flags_created_at ON user_flags(created_at);
CREATE INDEX IF NOT EXISTS idx_user_flags_level ON user_flags(flag_level);

-- ====================================
-- 2. Création de la table access_logs
-- ====================================

CREATE TABLE IF NOT EXISTS access_logs (
    id BIGSERIAL PRIMARY KEY,
    check_user_id BIGINT NOT NULL,
    requesting_guild_id BIGINT NOT NULL,
    requesting_guild_name TEXT NOT NULL,
    is_flagged BOOLEAN NOT NULL,
    flag_level TEXT,
    accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_access_logs_accessed_at ON access_logs(accessed_at);
CREATE INDEX IF NOT EXISTS idx_access_logs_guild_id ON access_logs(requesting_guild_id);

-- ====================================
-- 3. Fonction check_user_flag
-- ====================================

CREATE OR REPLACE FUNCTION check_user_flag(
    check_user_id BIGINT,
    requesting_guild_id BIGINT,
    requesting_guild_name TEXT
)
RETURNS TABLE (
    is_flagged BOOLEAN,
    flag_level TEXT,
    flag_reason TEXT,
    flag_category TEXT,
    flagged_at TIMESTAMP WITH TIME ZONE,
    flagging_guild_name TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    flag_record RECORD;
BEGIN
    -- Rechercher le flag le plus récent pour cet utilisateur
    SELECT uf.flag_level, uf.flag_reason, uf.flag_category, uf.created_at, uf.flagging_guild_name
    INTO flag_record
    FROM user_flags uf
    WHERE uf.user_id = check_user_id
    ORDER BY uf.created_at DESC
    LIMIT 1;
    
    -- Logger l'accès
    INSERT INTO access_logs (check_user_id, requesting_guild_id, requesting_guild_name, is_flagged, flag_level)
    VALUES (check_user_id, requesting_guild_id, requesting_guild_name, 
            flag_record.flag_level IS NOT NULL, flag_record.flag_level);
    
    -- Retourner le résultat
    IF flag_record.flag_level IS NOT NULL THEN
        RETURN QUERY SELECT 
            TRUE as is_flagged,
            flag_record.flag_level,
            flag_record.flag_reason,
            flag_record.flag_category,
            flag_record.created_at as flagged_at,
            flag_record.flagging_guild_name;
    ELSE
        RETURN QUERY SELECT 
            FALSE as is_flagged,
            NULL::TEXT as flag_level,
            NULL::TEXT as flag_reason,
            NULL::TEXT as flag_category,
            NULL::TIMESTAMP WITH TIME ZONE as flagged_at,
            NULL::TEXT as flagging_guild_name;
    END IF;
END;
$$;

-- ====================================
-- 4. Fonction add_user_flag
-- ====================================

CREATE OR REPLACE FUNCTION add_user_flag(
    flag_user_id BIGINT,
    flag_username TEXT,
    flag_level TEXT,
    flag_reason TEXT,
    flag_category TEXT,
    flagging_guild_id BIGINT,
    flagging_guild_name TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    -- Vérifier le niveau de flag
    IF flag_level NOT IN ('low', 'medium', 'high', 'critical') THEN
        RAISE EXCEPTION 'Invalid flag_level: %', flag_level;
    END IF;
    
    -- Insérer ou mettre à jour le flag
    INSERT INTO user_flags (
        user_id, username, flag_level, flag_reason, flag_category,
        flagging_guild_id, flagging_guild_name
    )
    VALUES (
        flag_user_id, flag_username, flag_level, flag_reason, flag_category,
        flagging_guild_id, flagging_guild_name
    );
    
    RETURN TRUE;
    
EXCEPTION
    WHEN OTHERS THEN
        -- Log l'erreur et retourner FALSE
        RAISE WARNING 'Error adding user flag: %', SQLERRM;
        RETURN FALSE;
END;
$$;

-- ====================================
-- 5. Fonction get_guild_stats
-- ====================================

CREATE OR REPLACE FUNCTION get_guild_stats(guild_id_param BIGINT, days_param INTEGER DEFAULT 30)
RETURNS TABLE (
    total_checks BIGINT,
    flagged_users BIGINT,
    recent_flags BIGINT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY 
    SELECT 
        (SELECT COUNT(*) FROM access_logs 
         WHERE requesting_guild_id = guild_id_param 
         AND accessed_at >= NOW() - INTERVAL '1 day' * days_param) as total_checks,
         
        (SELECT COUNT(DISTINCT check_user_id) FROM access_logs 
         WHERE requesting_guild_id = guild_id_param 
         AND is_flagged = true
         AND accessed_at >= NOW() - INTERVAL '1 day' * days_param) as flagged_users,
         
        (SELECT COUNT(*) FROM user_flags 
         WHERE flagging_guild_id = guild_id_param
         AND created_at >= NOW() - INTERVAL '1 day' * days_param) as recent_flags;
END;
$$;

-- ====================================
-- 6. Fonction get_recent_flags  
-- ====================================

CREATE OR REPLACE FUNCTION get_recent_flags(days_param INTEGER DEFAULT 7)
RETURNS TABLE (
    user_id BIGINT,
    username TEXT,
    flag_level TEXT,
    flag_reason TEXT,
    flag_category TEXT,
    flagging_guild_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY 
    SELECT uf.user_id, uf.username, uf.flag_level, uf.flag_reason, 
           uf.flag_category, uf.flagging_guild_name, uf.created_at
    FROM user_flags uf
    WHERE uf.created_at >= NOW() - INTERVAL '1 day' * days_param
    ORDER BY uf.created_at DESC
    LIMIT 50;
END;
$$;

-- ====================================
-- 7. Politiques RLS (Row Level Security)
-- ====================================

-- Activer RLS sur les tables
ALTER TABLE user_flags ENABLE ROW LEVEL SECURITY;
ALTER TABLE access_logs ENABLE ROW LEVEL SECURITY;

-- Politique pour permettre la lecture/écriture aux utilisateurs authentifiés
-- (à adapter selon vos besoins de sécurité)
CREATE POLICY "Allow service role access" ON user_flags
    FOR ALL USING (true);
    
CREATE POLICY "Allow service role access" ON access_logs  
    FOR ALL USING (true);

-- ====================================
-- 8. Données de test (optionnel)
-- ====================================

-- Exemple de données de test (à supprimer en production)
-- INSERT INTO user_flags (user_id, username, flag_level, flag_reason, flag_category, flagging_guild_id, flagging_guild_name)
-- VALUES (123456789, 'testuser', 'medium', 'Suspicious behavior', 'suspicious_behavior', 987654321, 'Test Server');

-- ====================================
-- 9. Vues utiles (optionnel)
-- ====================================

-- Vue pour les statistiques globales
CREATE OR REPLACE VIEW global_stats AS
SELECT 
    COUNT(*) as total_flags,
    COUNT(DISTINCT user_id) as unique_users_flagged,
    COUNT(DISTINCT flagging_guild_id) as guilds_participating,
    flag_level,
    COUNT(*) as flags_by_level
FROM user_flags
GROUP BY flag_level;

-- Vue pour les utilisateurs les plus signalés
CREATE OR REPLACE VIEW most_flagged_users AS
SELECT 
    user_id,
    username,
    COUNT(*) as flag_count,
    MAX(created_at) as last_flagged,
    STRING_AGG(DISTINCT flag_level, ', ') as flag_levels
FROM user_flags
GROUP BY user_id, username
HAVING COUNT(*) > 1
ORDER BY flag_count DESC;

COMMENT ON TABLE user_flags IS 'Stockage des flags utilisateurs validés par les modérateurs';
COMMENT ON TABLE access_logs IS 'Logs des vérifications d''utilisateurs par les serveurs';
COMMENT ON FUNCTION check_user_flag IS 'Vérifie si un utilisateur est flagué et log l''accès';
COMMENT ON FUNCTION add_user_flag IS 'Ajoute un nouveau flag utilisateur';