-- Extension du schéma Supabase pour le système anti-abus anonyme
-- Ce fichier étend le schéma existant avec les nouvelles fonctionnalités

-- ====================================
-- 1. Mise à jour de la table user_flags
-- ====================================

-- Ajouter les nouvelles colonnes pour l'anonymat
ALTER TABLE user_flags 
ADD COLUMN IF NOT EXISTS reporter_hash TEXT,
ADD COLUMN IF NOT EXISTS uniqueness_hash TEXT UNIQUE,
ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '6 months');

-- Index pour les hash (performance et unicité)
CREATE INDEX IF NOT EXISTS idx_user_flags_reporter_hash ON user_flags(reporter_hash);
CREATE INDEX IF NOT EXISTS idx_user_flags_uniqueness_hash ON user_flags(uniqueness_hash);
CREATE INDEX IF NOT EXISTS idx_user_flags_expires_at ON user_flags(expires_at);

-- ====================================
-- 2. Nouvelle table pour les signalements anonymes 
-- ====================================

CREATE TABLE IF NOT EXISTS anonymous_reports (
    id TEXT PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    target_username TEXT NOT NULL,
    target_user_id BIGINT,
    category TEXT NOT NULL,
    reason TEXT NOT NULL,
    evidence TEXT DEFAULT '',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'validated', 'rejected')),
    reporter_hash TEXT NOT NULL,  -- Hash anonyme du reporter
    uniqueness_hash TEXT NOT NULL UNIQUE,  -- Hash pour détecter doublons
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    validated_by BIGINT,
    validated_at TIMESTAMP WITH TIME ZONE,
    thread_id BIGINT,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_anonymous_reports_guild_id ON anonymous_reports(guild_id);
CREATE INDEX IF NOT EXISTS idx_anonymous_reports_status ON anonymous_reports(status);
CREATE INDEX IF NOT EXISTS idx_anonymous_reports_created_at ON anonymous_reports(created_at);
CREATE INDEX IF NOT EXISTS idx_anonymous_reports_reporter_hash ON anonymous_reports(reporter_hash);
CREATE INDEX IF NOT EXISTS idx_anonymous_reports_uniqueness_hash ON anonymous_reports(uniqueness_hash);

-- ====================================
-- 3. Table d'audit transparent
-- ====================================

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    action TEXT NOT NULL,
    guild_id BIGINT NOT NULL,
    moderator_id BIGINT NOT NULL,
    moderator_name TEXT NOT NULL,
    report_id TEXT,
    target_user_id BIGINT,
    target_username TEXT,
    details JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour les requêtes d'audit
CREATE INDEX IF NOT EXISTS idx_audit_logs_guild_id ON audit_logs(guild_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_moderator_id ON audit_logs(moderator_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);

-- ====================================
-- 4. Fonction de nettoyage automatique des flags expirés
-- ====================================

CREATE OR REPLACE FUNCTION cleanup_expired_flags()
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    cleanup_count INTEGER;
BEGIN
    -- Supprimer les flags expirés (plus de 6 mois)
    DELETE FROM user_flags 
    WHERE expires_at IS NOT NULL AND expires_at < NOW();
    
    GET DIAGNOSTICS cleanup_count = ROW_COUNT;
    
    -- Log l'opération
    IF cleanup_count > 0 THEN
        RAISE NOTICE 'Nettoyage automatique: % flags expirés supprimés', cleanup_count;
    END IF;
    
    RETURN cleanup_count;
END;
$$;

-- ====================================
-- 5. Fonction check_user_flag mise à jour (avec niveaux automatiques et expiration)
-- ====================================

CREATE OR REPLACE FUNCTION check_user_flag(
    check_user_id BIGINT,
    requesting_guild_id BIGINT,
    requesting_guild_name TEXT
)
RETURNS TABLE (
    is_flagged BOOLEAN,
    current_level TEXT,
    active_flags INTEGER,
    total_flags INTEGER,
    highest_severity TEXT,
    most_recent_flag TIMESTAMP WITH TIME ZONE,
    expired_flags_cleaned INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    cleanup_count INTEGER := 0;
    active_count INTEGER := 0;
    total_count INTEGER := 0;
    highest_level TEXT := NULL;
    recent_flag TIMESTAMP WITH TIME ZONE := NULL;
BEGIN
    -- 1. Nettoyer les flags expirés pour cet utilisateur
    DELETE FROM user_flags 
    WHERE user_id = check_user_id 
    AND expires_at IS NOT NULL 
    AND expires_at < NOW();
    
    GET DIAGNOSTICS cleanup_count = ROW_COUNT;
    
    -- 2. Compter les flags actifs et totaux
    SELECT COUNT(*), MAX(created_at) INTO active_count, recent_flag
    FROM user_flags
    WHERE user_id = check_user_id;
    
    total_count := active_count; -- Après nettoyage
    
    -- 3. Déterminer le niveau le plus élevé
    SELECT flag_level INTO highest_level
    FROM user_flags
    WHERE user_id = check_user_id
    ORDER BY 
        CASE flag_level
            WHEN 'critical' THEN 4
            WHEN 'high' THEN 3  
            WHEN 'medium' THEN 2
            WHEN 'low' THEN 1
            ELSE 0
        END DESC,
        created_at DESC
    LIMIT 1;
    
    -- 4. Logger l'accès
    INSERT INTO access_logs (
        check_user_id, 
        requesting_guild_id, 
        requesting_guild_name, 
        is_flagged, 
        flag_level
    )
    VALUES (
        check_user_id, 
        requesting_guild_id, 
        requesting_guild_name, 
        active_count > 0, 
        highest_level
    );
    
    -- 5. Retourner le résultat enrichi
    RETURN QUERY SELECT 
        active_count > 0 as is_flagged,
        CASE 
            WHEN active_count >= 5 THEN 'critical'
            WHEN active_count >= 3 THEN 'high'
            WHEN active_count >= 2 THEN 'medium'
            WHEN active_count >= 1 THEN 'low'
            ELSE NULL
        END as current_level,
        active_count as active_flags,
        total_count as total_flags,
        highest_level as highest_severity,
        recent_flag as most_recent_flag,
        cleanup_count as expired_flags_cleaned;
END;
$$;

-- ====================================
-- 6. Fonction add_user_flag mise à jour (sans niveau manuel)
-- ====================================

CREATE OR REPLACE FUNCTION add_user_flag(
    flag_user_id BIGINT,
    flag_username TEXT,
    flag_reason TEXT,
    flag_category TEXT,
    flagging_guild_id BIGINT,
    flagging_guild_name TEXT
)
RETURNS TABLE (
    success BOOLEAN,
    new_level TEXT,
    total_flags INTEGER,
    message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    current_flags INTEGER := 0;
    new_flag_level TEXT;
    expires_date TIMESTAMP WITH TIME ZONE;
BEGIN
    -- 1. Nettoyer les anciens flags expirés
    DELETE FROM user_flags 
    WHERE user_id = flag_user_id 
    AND expires_at IS NOT NULL 
    AND expires_at < NOW();
    
    -- 2. Compter les flags actuels
    SELECT COUNT(*) INTO current_flags
    FROM user_flags
    WHERE user_id = flag_user_id;
    
    -- 3. Déterminer le niveau du nouveau flag basé sur la catégorie
    new_flag_level := CASE flag_category
        WHEN 'child_safety' THEN 'critical'
        WHEN 'threats' THEN 'critical'
        WHEN 'harassment' THEN 'high'
        WHEN 'scam' THEN 'high'
        WHEN 'inappropriate_content' THEN 'medium'
        WHEN 'suspicious_behavior' THEN 'medium'
        WHEN 'spam' THEN 'low'
        ELSE 'low'
    END;
    
    -- 4. Date d'expiration (6 mois)
    expires_date := NOW() + INTERVAL '6 months';
    
    -- 5. Insérer le nouveau flag
    INSERT INTO user_flags (
        user_id, username, flag_level, flag_reason, flag_category,
        flagging_guild_id, flagging_guild_name, expires_at
    )
    VALUES (
        flag_user_id, flag_username, new_flag_level, flag_reason, flag_category,
        flagging_guild_id, flagging_guild_name, expires_date
    );
    
    current_flags := current_flags + 1;
    
    -- 6. Retourner le résultat
    RETURN QUERY SELECT 
        TRUE as success,
        CASE 
            WHEN current_flags >= 5 THEN 'critical'
            WHEN current_flags >= 3 THEN 'high'
            WHEN current_flags >= 2 THEN 'medium'
            ELSE 'low'
        END as new_level,
        current_flags as total_flags,
        format('Flag ajouté avec succès. Niveau: %s (%s flags)', new_flag_level, current_flags) as message;
        
EXCEPTION
    WHEN OTHERS THEN
        RETURN QUERY SELECT 
            FALSE as success,
            NULL::TEXT as new_level,
            0 as total_flags,
            format('Erreur: %s', SQLERRM) as message;
END;
$$;

-- ====================================
-- 7. Fonctions pour les signalements anonymes
-- ====================================

-- Sauvegarder un signalement anonyme
CREATE OR REPLACE FUNCTION save_anonymous_report(
    report_data JSONB
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO anonymous_reports (
        id, guild_id, target_username, target_user_id, category, reason,
        evidence, status, reporter_hash, uniqueness_hash, created_at,
        validated_by, validated_at, thread_id, metadata
    )
    VALUES (
        report_data->>'id',
        (report_data->>'guild_id')::BIGINT,
        report_data->>'target_username',
        CASE WHEN report_data->>'target_user_id' != '' THEN (report_data->>'target_user_id')::BIGINT ELSE NULL END,
        report_data->>'category',
        report_data->>'reason',
        COALESCE(report_data->>'evidence', ''),
        COALESCE(report_data->>'status', 'pending'),
        report_data->>'reporter_hash',
        report_data->>'uniqueness_hash',
        COALESCE((report_data->>'created_at')::TIMESTAMP WITH TIME ZONE, NOW()),
        CASE WHEN report_data->>'validated_by' != '' THEN (report_data->>'validated_by')::BIGINT ELSE NULL END,
        CASE WHEN report_data->>'validated_at' != '' THEN (report_data->>'validated_at')::TIMESTAMP WITH TIME ZONE ELSE NULL END,
        CASE WHEN report_data->>'thread_id' != '' THEN (report_data->>'thread_id')::BIGINT ELSE NULL END,
        COALESCE(report_data->'metadata', '{}'::jsonb)
    );
    
    RETURN TRUE;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Erreur sauvegarde signalement anonyme: %', SQLERRM;
        RETURN FALSE;
END;
$$;

-- Vérifier l'existence d'un doublon
CREATE OR REPLACE FUNCTION check_duplicate_report(
    uniqueness_hash_param TEXT
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    existing_report_id TEXT;
BEGIN
    SELECT id INTO existing_report_id
    FROM anonymous_reports
    WHERE uniqueness_hash = uniqueness_hash_param
    LIMIT 1;
    
    RETURN existing_report_id;
END;
$$;

-- ====================================
-- 8. Fonction d'audit
-- ====================================

CREATE OR REPLACE FUNCTION log_audit_action(
    action_param TEXT,
    guild_id_param BIGINT,
    moderator_id_param BIGINT,
    moderator_name_param TEXT,
    report_id_param TEXT DEFAULT NULL,
    target_user_id_param BIGINT DEFAULT NULL,
    target_username_param TEXT DEFAULT NULL,
    details_param JSONB DEFAULT '{}'::jsonb
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO audit_logs (
        action, guild_id, moderator_id, moderator_name, report_id,
        target_user_id, target_username, details
    )
    VALUES (
        action_param, guild_id_param, moderator_id_param, moderator_name_param,
        report_id_param, target_user_id_param, target_username_param, details_param
    );
    
    RETURN TRUE;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE WARNING 'Erreur enregistrement audit: %', SQLERRM;
        RETURN FALSE;
END;
$$;

-- ====================================
-- 9. Mise à jour des politiques RLS
-- ====================================

-- Politiques pour les nouvelles tables
ALTER TABLE anonymous_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow service role access" ON anonymous_reports FOR ALL USING (true);
CREATE POLICY "Allow service role access" ON audit_logs FOR ALL USING (true);

-- ====================================
-- 10. Vues pour le monitoring
-- ====================================

-- Vue des statistiques anti-abus
CREATE OR REPLACE VIEW anti_abuse_stats AS
SELECT 
    COUNT(*) as total_reports,
    COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_reports,
    COUNT(CASE WHEN status = 'validated' THEN 1 END) as validated_reports,
    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected_reports,
    COUNT(DISTINCT reporter_hash) as unique_reporters,
    COUNT(DISTINCT guild_id) as active_guilds
FROM anonymous_reports;

-- Vue des signalements suspects (même reporter, cibles multiples)
CREATE OR REPLACE VIEW suspicious_reporting_patterns AS
SELECT 
    reporter_hash,
    COUNT(*) as report_count,
    COUNT(DISTINCT target_username) as unique_targets,
    COUNT(DISTINCT guild_id) as guilds_used,
    MIN(created_at) as first_report,
    MAX(created_at) as last_report
FROM anonymous_reports
GROUP BY reporter_hash
HAVING COUNT(*) > 5 OR COUNT(DISTINCT guild_id) > 3
ORDER BY report_count DESC;

-- ====================================
-- 11. Tâche de maintenance automatique
-- ====================================

-- Créer une extension pour les tâches programmées si pas déjà fait
-- CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Programmer le nettoyage automatique (chaque jour à 3h du matin)
-- SELECT cron.schedule('cleanup-expired-flags', '0 3 * * *', 'SELECT cleanup_expired_flags();');

-- ====================================
-- Commentaires de documentation
-- ====================================

COMMENT ON TABLE anonymous_reports IS 'Signalements anonymes sans exposition de l''identité du reporter';
COMMENT ON TABLE audit_logs IS 'Journal d''audit transparent des actions de modération';
COMMENT ON COLUMN user_flags.reporter_hash IS 'Hash anonyme du reporter (non réversible)';
COMMENT ON COLUMN user_flags.uniqueness_hash IS 'Hash pour détecter les doublons (reporter+serveur+cible)';
COMMENT ON COLUMN user_flags.expires_at IS 'Date d''expiration automatique du flag (6 mois par défaut)';
COMMENT ON FUNCTION cleanup_expired_flags() IS 'Nettoyage automatique des flags expirés';
COMMENT ON FUNCTION save_anonymous_report(jsonb) IS 'Sauvegarde un signalement de manière anonyme';
COMMENT ON FUNCTION check_duplicate_report(text) IS 'Vérifie l''existence d''un signalement en doublon';