from db import conectar_banco, desconectar_banco
import psycopg2

def criar_database():
    try:
        conn = psycopg2.connect(
            host="localhost",
            dbname="postgres",
            user="postgres",
            password="090407",
            port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname='candidatos_db'")
        existe = cursor.fetchone()

        if not existe:
            cursor.execute("CREATE DATABASE candidatos_db")
            print('db criado')
        else:
            print('db já existente')
        
        cursor.close()
        conn.close()
        return True

    except psycopg2.Error as e:
        print(f'Erro {e}')
        return False
    
def criar_tabela_candidatos():
    conn, cursor = conectar_banco()

    if not conn or not cursor:
        print ('Erro na conexão')
        return False
    
    sql_candidatos = """
        CREATE TABLE IF NOT EXISTS candidatos (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL, 
        telefone VARCHAR(20),
        email VARCHAR(100) NOT NULL,
        experiencia TEXT,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    try:
        cursor.execute(sql_candidatos)
        conn.commit()
        print('Tabela criada')
        return True
    except psycopg2.Error as e:
        print(e)
        return False
    finally:
        desconectar_banco(conn, cursor)

def verificar_estrutura():
    conn, cursor = conectar_banco()

    if not conn:
        return False
    
    try:
        cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        """)
        tabelas = cursor.fetchall()

        print('tabelas no banco:')
        for tabela in tabelas:
            print(f" - {tabela['table_name']}")
    
        if not tabelas:
            print("Nenhuma tabela encontrada")

        return True
    
    except psycopg2.Error as e:
        print(f'Erro {e}')
        return False
    finally:
        desconectar_banco(conn, cursor)

def main():
    print('Preparando ambiente...')
    
    print('Criando db...')
    if not criar_database():
        print('falha ao criar db')
        return False
    
    print('criando tabela...')
    if not criar_tabela_candidatos():
        print('Falha ao criar tabela')
        return False

    print('verificando...')
    verificar_estrutura()

    print('concluído')
    return True

if __name__ == "__main__":
    main()

