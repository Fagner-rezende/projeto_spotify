import pandas as pd
import os
import glob
from sqlalchemy import create_engine
from dotenv import load_dotenv
import urllib.parse

# 1. Carrega variáveis de ambiente
load_dotenv()

def get_db_connection():
    """
    Cria a string de conexão (Engine) para o SQLAlchemy.
    Trata caracteres especiais na senha.
    """
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    # Importante: Codifica a senha para evitar erros com caracteres especiais (@, !, etc)
    encoded_pass = urllib.parse.quote_plus(db_pass)

    # String de conexão padrão do MySQL
    connection_string = f"mysql+mysqlconnector://{db_user}:{encoded_pass}@{db_host}:3306/{db_name}"
    
    return create_engine(connection_string)

def get_latest_file():
    """
    Busca na pasta 'data/' o arquivo CSV mais recente que começa com 'spotify_enriched'.
    """
    # Lista todos os arquivos que batem com o padrão
    list_of_files = glob.glob('data/spotify_enriched_*.csv') 
    
    if not list_of_files:
        return None
        
    # Pega o arquivo com a data de criação mais recente
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def load_data_to_sql():
    print("🚀 Iniciando processo de Carga (Load)...")

    # 1. Encontrar o arquivo
    csv_file = get_latest_file()
    if not csv_file:
        print("❌ Nenhum arquivo CSV encontrado em data/")
        return

    print(f"📂 Arquivo selecionado: {csv_file}")

    # 2. Ler o CSV com Pandas
    try:
        df = pd.read_csv(csv_file)
        print(f"📊 Dados carregados: {len(df)} linhas.")
    except Exception as e:
        print(f"❌ Erro ao ler CSV: {e}")
        return

    # 3. Tratamento final antes do banco
    # O Pandas lê datas como string. Vamos converter para objeto de data real.
    if 'played_at' in df.columns:
        df['played_at'] = pd.to_datetime(df['played_at'])
    
    # 4. Conectar e Salvar
    engine = get_db_connection()
    
    try:
        print("🔌 Conectando ao MySQL...")
        # 'replace': Apaga a tabela antiga e cria uma nova. 
        # 'append': Adiciona dados no final. 
        # Para este projeto, vamos usar 'replace' para garantir que a estrutura esteja sempre certa.
        # Em produção real, usaríamos 'append' com verificação de duplicatas.
        df.to_sql(name='play_history', con=engine, if_exists='replace', index=False)
        
        print("✅ Sucesso! Dados salvos na tabela 'play_history' do MySQL.")
        
    except Exception as e:
        print(f"❌ Erro ao salvar no banco: {e}")

if __name__ == "__main__":
    load_data_to_sql()