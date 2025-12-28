# 🎵 Spotify Data Engineering Pipeline (End-to-End)

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![Metabase](https://img.shields.io/badge/Metabase-BI-509EE3?style=for-the-badge&logo=metabase&logoColor=white)

Este projeto é um pipeline de dados completo (**ETL**) que extrai o histórico de reprodução do usuário via API do Spotify, processa e enriquece os dados com Python/Pandas, armazena em um Data Warehouse estruturado (MySQL) e disponibiliza dashboards analíticos via Metabase.

---

## 🏗️ Arquitetura da Solução

O projeto foi construído simulando um ambiente de produção moderno, utilizando containers para garantir portabilidade.

1.  **Ingestão (Extract):**
    * Conexão segura com a **Spotify API** (OAuth 2.0).
    * Paginação automática para extração de grandes volumes de histórico.
2.  **Transformação (Transform):**
    * Limpeza e tipagem de dados com **Pandas**.
    * **Enriquecimento:** Cruzamento de dados para buscar os Gêneros Musicais dos artistas (dado não disponível na rota padrão).
3.  **Carga (Load):**
    * Armazenamento em banco de dados **MySQL** rodando em container Docker.
    * Conceito de **Idempotência**: O pipeline pode rodar múltiplas vezes sem duplicar ou corromper a estrutura (modo `replace`).
4.  **Analytics (Modelagem):**
    * Criação de **Views SQL** para regras de negócio (Top Artists, Heatmap de Horários, Análise de Conteúdo Explícito).
5.  **Visualização (Dataviz):**
    * Dashboards interativos no **Metabase**.

---

## 🚀 Como Executar

### Pré-requisitos
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado.
* [Python 3.x](https://www.python.org/) instalado.
* Conta no [Spotify for Developers](https://developer.spotify.com/) para obter as credenciais.

### 1. Configuração de Ambiente
Clone este repositório e crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
SPOTIPY_CLIENT_ID='seu_client_id'
SPOTIPY_CLIENT_SECRET='seu_client_secret'
SPOTIPY_REDIRECT_URI='[http://127.0.0.1:8080](http://127.0.0.1:8080)'

# Banco de Dados
DB_HOST='127.0.0.1'
DB_USER='root'
DB_PASSWORD='SuaSenhaForteAqui'
DB_NAME='spotify_db'

## Subir a Infraestrutura (Docker)
Execute o comando abaixo para iniciar os containers do MySQL e Metabase:

docker-compose up -d

## Instalar Dependências

pip install -r requirements.txt

## Executar o Pipeline ETL
Rode os scripts na ordem para atualizar os dados:

# 1. Extração e Enriquecimento (Gera CSV na pasta /data)
python src/extract.py

# 2. Carga no Banco de Dados (Lê o CSV mais recente e envia para o MySQL)
python src/load.py

## 📊 Estrutura de Análise (SQL Views)
Após a carga, as seguintes Views são criadas no banco para facilitar a análise:

View                             Descrição
vw_top_artists            Ranking de artistas mais ouvidos por tempo e quantidade de plays.vw_top_tracks             As músicas favoritas, agrupadas por artista e álbum.vw_daily_activity         Mapa de calor de atividade (Plays por Hora do Dia e Período).vw_explicit_content       Percentual de consumo de conteúdo explícito vs. limpo.

## 📈 Visualização (Metabase)

Acesse http://localhost:3000.

Conecte o banco de dados MySQL usando o host: db e porta: 3306.

Explore os dados através das Views criadas.


# 📞 Contato
Desenvolvido por Fagner Rezende.