from db import conectar_banco, desconectar_banco
import psycopg2

def cadastar_candidato(nome, email, telefone=None, experiencia=None):
    conn, cursor = conectar_banco()

    if not conn:
        return {"erro": "Falha ao se conectar"}
    
    sql = """
    INSERT INTO candidatos (nome, email, telefone, experiencia)
    VALUES (%s, %s, %s, %s)
    RETURNING id, nome, email, telefone, experiencia, data_cadastro
    """
    try:
        cursor.execute(sql, (nome, email, telefone, experiencia))
        resultado = cursor.fetchone()
        conn.commit()

        print(f'candidato {nome} cadstrado com id {resultado ['id']}')
        return dict(resultado)
    
    except psycopg2.Error as e:
       conn.rollback()
       print(f'erro {e}') 
    finally:
        desconectar_banco(conn.cursor)

def listar_candidatos():
    conn, cursor = conectar_banco()

    if not conn:
        return []

    try:
        cursor.execute("SELECT * FROM candidatos ORDER BY data_cadastro DESC")

        candidatos = cursor.fetchall()

        lista = [dict(candidato) for candidato in candidatos]

        print(f'encontrados {len(lista)} candidatos')
        return lista
    
    except psycopg2.Error as e:
        print(f'erro: {e}')
        return []
    finally:
        desconectar_banco(conn,cursor)

def buscar_candidato_por_id(candidato_id):
    conn, cursor = conectar_banco()

    if not conn:
        return None

    try:
        cursor.execute("SELECT * FROM candidatos WHERE id = %s", (candidato_id))

        candidato =  cursor.fetchone()

        if candidato:
            print('sucesso')
            return dict(candidato)
        
        else:
            print('erro')
            return None
    
    except psycopg2.Error as e:
        print(f'erro: {e}')
    
    finally:
        desconectar_banco(conn,cursor)

def atualizar_candidato(candidato_id, nome=None, email=None, telefone=None, experiencia=None ):
    conn, cursor = conectar_banco()

    if not conn:
        return False

    campos_atualizacao = []
    valores =[]

    if nome is not None:
        campos_atualizacao.append("nome = %s")
        valores.append(nome)
    if email is not None:
        campos_atualizacao.append("email=%s")
    if telefone is not None:
        campos_atualizacao.append("telefone = %s")
    if experiencia is not None:
        campos_atualizacao.append("experiencia = %s")

    if not campos_atualizacao:
        print('nenhum campo para atualizar')
        desconectar_banco(conn,cursor)
        return False

    valores.append(candidato_id)
    
    sql = f"UPDATE candidatos SET {','.join(campos_atualizacao)} WHERE id= %s"

    try:
        cursor.execute(sql, valores)
        conn.commit()

        if cursor.rowcount > 0:
            print(f'candidato ID {candidato_id} atualizado com sucesso')
            return True
        else:
            print(f'candidato ID {candidato_id} não encontrado')
            return False
    except psycopg2.Error as e:
        conn.rollback()
        print(f'erro {e}')
    finally:
        desconectar_banco(conn, cursor)
    
def excluir_candidato(candidato_id):
    conn, cursor = conectar_banco()

    if not conn:
        return False

    try:
        cursor.execute("DELETE FROM candidatos WHERE id = %s")
        conn.commit()

        if cursor.rowcount > 0:
            print(f'candidato {candidato_id} deletado')
            return True
        else:
            print(f'candidato {candidato_id} não encontrado')
            return False
    except psycopg2.Error as e:
        conn.rollback()
        print(f'erro {e}')
        return False
    finally:
        desconectar_banco(conn, cursor)

def contar_candidatos():
    conn, cursor = conectar_banco()

    if not conn:
        return 0
    
    try:
        cursor.execute("SELECT COUNT(*) FROM candidatos")
        resultado = cursor.fetchone()

        total = resultado[0]
        print(f'Total de candidatos: {total}')
        return total
    except psycopg2.Error as e:
        print(f'erro{e}')
        return 0
    finally:
        desconectar_banco(conn,cursor)

def buscar_candidatos_por_email(email):
    conn, cursor = conectar_banco()

    if not conn:
        return []

    try:
        cursor.execute("SELECT * FROM candidatos WHERE LOWER(email) = LOWER(%s)", (email))
        candidatos = cursor.fetchall()

        lista = [dict(candidato) for candidato in candidatos]
        print(f"encontrados{len(lista)} candidatos com email '{email}'")
        return lista
    except psycopg2.error as e:
        print(f'erro {e}')
        return []
    finally:
        desconectar_banco(conn, cursor)
    
