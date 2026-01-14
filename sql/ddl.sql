USE spotify_db;

-- Tabela Principal: Histórico de Reprodução
CREATE TABLE IF NOT EXISTS play_history (
    played_at TIMESTAMP PRIMARY KEY,
    track_name VARCHAR(255),
    artist_name VARCHAR(255),
    album_name VARCHAR(255),
    album_image VARCHAR(500),
    track_id VARCHAR(50),
    artist_genre VARCHAR(255),
    duration_ms INT,
    explicit BOOLEAN,
    popularity INT,
    danceability FLOAT,
    energy FLOAT,
    valence FLOAT,
    tempo FLOAT,
    load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para otimizar as Views
CREATE INDEX idx_artist ON play_history(artist_name);
CREATE INDEX idx_played_at ON play_history(played_at);