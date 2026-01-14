import pandas as pd
import os
import glob
from sqlalchemy import create_engine
from config import Config 
import urllib.parse
import logging

# Configuração de Logging
Config.setup_logging() 

try:
    Config.validate()
except ValueError as e:
    logging.error(f"Erro de Configuração: {e}")
    exit(1)

def get_db_connection():
    """
    Cria a string de conexão (Engine) para o SQLAlchemy.
    """
    db_host = Config.DB_HOST
    db_user = Config.DB_USER
    db_pass = Config.DB_PASSWORD
    db_name = Config.DB_NAME

    encoded_pass = urllib.parse.quote_plus(str(db_pass))

    connection_string = f"mysql+mysqlconnector://{db_user}:{encoded_pass}@{db_host}:3306/{db_name}"

    return create_engine(connection_string)


def get_latest_file():
    """
    Busca na pasta 'data/' o arquivo CSV mais recente.
    """
    list_of_files = glob.glob('data/spotify_enriched_*.csv')

    if not list_of_files:
        return None

    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def load_data_to_sql():
    logging.info("Iniciando processo de Carga (Load)...")

    # 1. Encontrar o arquivo
    csv_file = get_latest_file()
    if not csv_file:
        logging.error("Nenhum arquivo CSV encontrado na pasta data/")
        return

    logging.info(f"Arquivo selecionado para carga: {csv_file}")

    # 2. Ler o CSV
    try:
        df = pd.read_csv(csv_file)
        logging.info(f"Dados carregados do CSV: {len(df)} linhas.")
    except Exception as e:
        logging.error(f"Erro ao ler CSV: {e}")
        return

    # 3. Tratamento
    if 'played_at' in df.columns:
        df['played_at'] = pd.to_datetime(df['played_at'])

    # 4. Conectar e Salvar
    try:
        engine = get_db_connection()
        logging.info("Conectando ao MySQL...")
        
        df.to_sql(name='play_history', con=engine,
                  if_exists='replace', index=False)

        logging.info("Sucesso! Dados salvos na tabela 'play_history' do MySQL.")

    except Exception as e:
        logging.error(f"Erro fatal ao salvar no banco: {e}")


if __name__ == "__main__":
    load_data_to_sql()