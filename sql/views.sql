USE spotify_db;

-- 1. View: Top Artistas
CREATE OR REPLACE VIEW vw_top_artists AS
SELECT 
    artist_name,
    artist_genre,
    COUNT(*) as total_plays,
    SUM(duration_ms) / 60000 as minutes_listened,
    MAX(album_image) as artist_image 
FROM play_history
GROUP BY artist_name, artist_genre
ORDER BY total_plays DESC;

-- 2. View: Top Músicas
CREATE OR REPLACE VIEW vw_top_tracks AS
SELECT 
    track_name,
    artist_name,
    album_name,
    COUNT(*) as plays,
    album_image
FROM play_history
GROUP BY track_name, artist_name, album_name, album_image
ORDER BY plays DESC;

-- 3. View: Atividade Diária
CREATE OR REPLACE VIEW vw_daily_activity AS
SELECT 
    DATE(played_at) as listening_date,
    COUNT(*) as tracks_played,
    HOUR(played_at) as hour_of_day,
    CASE 
        WHEN HOUR(played_at) BETWEEN 6 AND 12 THEN 'Manhã'
        WHEN HOUR(played_at) BETWEEN 12 AND 18 THEN 'Tarde'
        WHEN HOUR(played_at) BETWEEN 18 AND 23 THEN 'Noite'
        ELSE 'Madrugada'
    END as period_of_day
FROM play_history
GROUP BY DATE(played_at), HOUR(played_at)
ORDER BY listening_date DESC, hour_of_day;

-- 4. View: Conteúdo Explícito
CREATE OR REPLACE VIEW vw_explicit_content AS
SELECT 
    explicit as is_explicit,
    COUNT(*) as total,
    (COUNT(*) * 100.0 / (SELECT COUNT(*) FROM play_history)) as percentage
FROM play_history
GROUP BY explicit;