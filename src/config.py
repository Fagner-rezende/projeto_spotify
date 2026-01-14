import os
import logging
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env apenas uma vez
load_dotenv()

class Config:
    # Credenciais Spotify
    SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
    SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
    SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
    
    # Banco de Dados
    DB_HOST = os.getenv('DB_HOST')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_NAME = os.getenv('DB_NAME')

    # Validação simples para garantir que não suba sem credenciais
    @classmethod
    def validate(cls):
        if not cls.SPOTIPY_CLIENT_ID or not cls.DB_PASSWORD:
            raise ValueError("As variáveis de ambiente obrigatórias não foram configuradas.")
        
    # Configuração de logging
    @staticmethod
    def setup_logging():
        """
        Configura o padrão de logs para o projeto.
        Exibe no console e salva em arquivo 'app.log'.
        """
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(), # Mostra no terminal
                logging.FileHandler("pipeline.log", mode='a') # Salva em arquivo
            ]
        )