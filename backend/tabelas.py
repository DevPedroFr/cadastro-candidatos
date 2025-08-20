import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os

IS_DOCKER = os.getenv('DOCKER_ENV', 'false').lower() == 'true'

def criar_banco_se_nao_existir():
    try:
        if IS_DOCKER:
            host = os.getenv('DB_HOST', 'db')
        else:
            host = 'localhost'
            
        conn = psycopg2.connect(
            host=host,
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '090407'),
            port=os.getenv('DB_PORT', '5432')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'candidatos_db'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute("CREATE DATABASE candidatos_db")
            print("Banco de dados 'candidatos_db' criado com sucesso!")
        else:
            print("Banco de dados 'candidatos_db' já existe.")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erro ao criar/verificar banco: {e}")
        return False

def criar_tabela_candidatos():
    try:
        from db import conectar_banco, desconectar_banco
        
        conn, cursor = conectar_banco()
        
        if not conn:
            print("Não foi possível conectar ao banco para criar tabelas")
            return False
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidatos (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                telefone VARCHAR(20),
                experiencia TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_candidatos_email 
            ON candidatos(email)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_candidatos_nome 
            ON candidatos(nome)
        """)
        
        conn.commit()
        print("Tabela 'candidatos' criada/verificada com sucesso!")
        
        desconectar_banco(conn, cursor)
        return True
        
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")
        return False

def main():
    print("Preparando ambiente...")
    
    print("Criando db...")
    if not criar_banco_se_nao_existir():
        print("falha ao criar db")
        return False
    
    print("Criando tabelas...")
    if not criar_tabela_candidatos():
        print("Falha ao criar tabelas")
        return False
    
    print("Ambiente preparado com sucesso!")
    return True

def testar_tabela():
    try:
        from db import conectar_banco, desconectar_banco
        
        conn, cursor = conectar_banco()
        
        if not conn:
            print("Não foi possível conectar para testar tabelas")
            return False
        
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'candidatos'
            )
        """)
        
        exists = cursor.fetchone()['exists']
        
        if exists:
            cursor.execute("SELECT COUNT(*) as total FROM candidatos")
            total = cursor.fetchone()['total']
            print(f"Tabela 'candidatos' existe com {total} registros")
        else:
            print("Tabela 'candidatos' não existe!")
            
        desconectar_banco(conn, cursor)
        return exists
        
    except Exception as e:
        print(f"Erro ao testar tabela: {e}")
        return False

if __name__ == "__main__":
    main()