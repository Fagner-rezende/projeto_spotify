import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import time

load_dotenv()

# Verifica chaves no arquivo env
if not os.getenv("SPOTIPY_CLIENT_ID"):
    raise ValueError("❌ Erro: .env não carregado.")

SCOPE = "user-read-recently-played"


def get_auth_manager():
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope=SCOPE,
        open_browser=True
    )


def extract_recently_played(limit=150):
    """
    Busca o histórico paginando de 50 em 50 até atingir o limite.
    """
    print(f"🔄 Iniciando extração de {limit} músicas...")
    sp = spotipy.Spotify(auth_manager=get_auth_manager())

    all_tracks = []
    before_cursor = None

    while len(all_tracks) < limit:
        try:
            results = sp.current_user_recently_played(
                limit=50, before=before_cursor)
        except Exception as e:
            print(f"❌ Erro na API: {e}")
            break

        if not results or not results['items']:
            print("⚠️ Sem mais dados disponíveis.")
            break

        # Processa o lote atual
        for item in results['items']:
            track = item['track']
            played_at = item['played_at']

            # Coleta dados
            track_data = {
                "played_at": played_at,
                "track_id": track['id'],
                "track_name": track['name'],
                "popularity": track['popularity'],
                "duration_ms": track['duration_ms'],
                "explicit": track['explicit'],
                # ID para buscar gênero depois
                "artist_id": track['artists'][0]['id'],
                "artist_name": track['artists'][0]['name'],
                "album_name": track['album']['name'],
                # Imagem do album
                "album_image": track['album']['images'][0]['url'] if track['album']['images'] else None,
                "release_date": track['album']['release_date']
            }
            all_tracks.append(track_data)

        # O cursor 'before' deve ser o timestamp da ÚLTIMA música desse lote
        last_played_at = results['items'][-1]['played_at']
        played_at_dt = datetime.strptime(
            last_played_at, "%Y-%m-%dT%H:%M:%S.%fZ")
        before_cursor = int(played_at_dt.timestamp() * 1000)

        print(f"✅ Lote processado. Total coletado: {len(all_tracks)}")

        # Se atingiu o limite, para
        if len(all_tracks) >= limit:
            break

    # Corta o excesso se passou de 150
    return pd.DataFrame(all_tracks[:limit])


def enrich_artist_genres(df, sp):
    """
    Recebe o DataFrame, pega os artist_ids únicos e busca os gêneros na API.
    """
    print("🎨 Enriquecendo dados com Gêneros Musicais...")

    # Pega lista única de IDs de artistas para não chamar API repetido
    artist_ids = df['artist_id'].unique().tolist()

    artist_genres = {}

    # A API só aceita buscar até 50 artistas de uma vez. Então, faz em lotes de 50.
    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i + 50]
        try:
            artists_info = sp.artists(batch)
            for artist in artists_info['artists']:
                # Se tiver gênero, pega o primeiro, senão 'Unknown'
                genre = artist['genres'][0] if artist['genres'] else "Pop"
                artist_genres[artist['id']] = genre
        except Exception as e:
            print(f"⚠️ Erro ao buscar artistas: {e}")

    # Aplica o gênero no DataFrame original usando map
    df['artist_genre'] = df['artist_id'].map(artist_genres)
    return df


def save_data(df):
    if not df.empty:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("data", exist_ok=True)
        filename = f"data/spotify_enriched_{timestamp}.csv"
        df.to_csv(filename, index=False)
        print(f"💾 Arquivo Enriquecido salvo: {filename}")
    else:
        print("⚠️ DataFrame vazio.")


if __name__ == "__main__":
    # 1. Extração (Paginação)
    df_raw = extract_recently_played(limit=150)

    if df_raw is not None and not df_raw.empty:
        # 2. Enriquecimento (Join com API de Artistas)
        sp = spotipy.Spotify(auth_manager=get_auth_manager())
        df_enriched = enrich_artist_genres(df_raw, sp)

        # 3. Carga
        save_data(df_enriched)
