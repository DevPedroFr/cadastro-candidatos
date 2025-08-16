import psycopg2
from psycopg2.extras import RealDictCursor

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
        return cursor, conn
    except:
        return None, None
    
def desconectar_banco(conn, cursor):
    if conn:
        conn.close()
    if cursor:
        cursor.close()


