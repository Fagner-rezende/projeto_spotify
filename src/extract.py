import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
import logging
import os
from config import Config  

# Configuração de Logging
Config.setup_logging() 
try:
    Config.validate()
except ValueError as e:
    logging.error(f"Erro de Configuração: {e}") 
    exit(1)

SCOPE = "user-read-recently-played"

def get_auth_manager():
    """
    Configura a autenticação usando as variáveis da classe Config.
    """
    return SpotifyOAuth(
        client_id=Config.SPOTIPY_CLIENT_ID,         
        client_secret=Config.SPOTIPY_CLIENT_SECRET, 
        redirect_uri=Config.SPOTIPY_REDIRECT_URI,   
        scope=SCOPE,
        open_browser=True
    )

def extract_recently_played(limit=150):
    logging.info(f"Iniciando extração de {limit} músicas...") # <--- logging.info
    sp = spotipy.Spotify(auth_manager=get_auth_manager())

    all_tracks = []
    before_cursor = None

    while len(all_tracks) < limit:
        try:
            results = sp.current_user_recently_played(limit=50, before=before_cursor)
        except Exception as e:
            logging.error(f"Erro na API do Spotify: {e}") # <--- logging.error
            break

        if not results or not results['items']:
            logging.warning("Sem mais dados disponíveis na API.") # <--- logging.warning
            break

        for item in results['items']:
            track = item['track']
            played_at = item['played_at']
            
            track_data = {
                "played_at": played_at,
                "track_id": track['id'],
                "track_name": track['name'],
                "popularity": track['popularity'],
                "duration_ms": track['duration_ms'],
                "explicit": track['explicit'],
                "artist_id": track['artists'][0]['id'],
                "artist_name": track['artists'][0]['name'],
                "album_name": track['album']['name'],
                "album_image": track['album']['images'][0]['url'] if track['album']['images'] else None,
                "release_date": track['album']['release_date']
            }
            all_tracks.append(track_data)

        last_played_at = results['items'][-1]['played_at']
        played_at_dt = datetime.strptime(last_played_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        before_cursor = int(played_at_dt.timestamp() * 1000)

        logging.info(f"Lote processado. Total coletado até agora: {len(all_tracks)}")

        if len(all_tracks) >= limit:
            break

    return pd.DataFrame(all_tracks[:limit])

def enrich_artist_genres(df, sp):
    logging.info("Enriquecendo dados com Gêneros Musicais...")
    
    artist_ids = df['artist_id'].unique().tolist()
    artist_genres = {}

    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i + 50]
        try:
            artists_info = sp.artists(batch)
            for artist in artists_info['artists']:
                genre = artist['genres'][0] if artist['genres'] else "Pop"
                artist_genres[artist['id']] = genre
        except Exception as e:
            logging.error(f"Erro ao buscar artistas: {e}")

    df['artist_genre'] = df['artist_id'].map(artist_genres)
    return df

def save_data(df):
    if not df.empty:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        import os
        os.makedirs("data", exist_ok=True)
        filename = f"data/spotify_enriched_{timestamp}.csv"
        df.to_csv(filename, index=False)
        logging.info(f"Arquivo salvo com sucesso: {filename}")
    else:
        logging.warning("DataFrame vazio. Nenhum arquivo salvo.")

if __name__ == "__main__":
    df_raw = extract_recently_played(limit=150)

    if df_raw is not None and not df_raw.empty:
        sp = spotipy.Spotify(auth_manager=get_auth_manager())
        df_enriched = enrich_artist_genres(df_raw, sp)
        save_data(df_enriched)