import psycopg2
from psycopg2.extras import RealDictCursor
import os

IS_DOCKER = os.getenv('DOCKER_ENV', 'false').lower() == 'true'

if IS_DOCKER:
    DATABASE_CONFIG = {
        "host": os.getenv('DB_HOST', 'db'),  
        "dbname": os.getenv('DB_NAME', 'candidatos_db'),
        "user": os.getenv('DB_USER', 'postgres'),
        "password": os.getenv('DB_PASSWORD', '090407'),
        "port": os.getenv('DB_PORT', '5432')
    }
else:
    DATABASE_CONFIG = {
        "host": "localhost",
        "dbname": "candidatos_db",
        "user": "postgres",
        "password": "090407",
        "port": "5432"
    }

def conectar_banco():
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        return conn, cursor
    except psycopg2.OperationalError as e:
        print(f"Erro ao conectar ao banco: {e}")
        print(f"Tentando conectar em: {DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}")
        return None, None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None, None
    
def desconectar_banco(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()