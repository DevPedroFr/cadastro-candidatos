from db import conectar_banco, desconectar_banco
import psycopg2
from datetime import datetime

def converter_datetime_para_string(dados):
    if isinstance(dados, dict):
        for chave, valor in dados.items():
            if isinstance(valor, datetime):
                dados[chave] = valor.isoformat()
    return dados

def cadastrar_candidato(nome, email, telefone=None, experiencia=None):    
    conn, cursor = conectar_banco()
    
    if not conn or not cursor:
        return {"erro": "Não conseguiu conectar no banco de dados"}
    
    sql = """
    INSERT INTO candidatos (nome, email, telefone, experiencia)
    VALUES (%s, %s, %s, %s)
    RETURNING id, nome, email, telefone, experiencia, data_cadastro
    """
    
    try:
        cursor.execute(sql, (nome, email, telefone, experiencia))
        resultado = cursor.fetchone()
        
        if not resultado:        
            return {"erro": "INSERT falhou - nenhum dado retornado"}
        
        conn.commit()
        
        dict_resultado = dict(resultado)
        
        dict_resultado = converter_datetime_para_string(dict_resultado)
        
        return dict_resultado
        
    except psycopg2.IntegrityError as erro:
        conn.rollback()
        if "unique" in str(erro).lower():
            return {"erro": "Email já existe no sistema"}
        else:
            return {"erro": f"Violação de integridade: {erro}"}
    
    except psycopg2.Error as erro:
        conn.rollback()
        return {"erro": f"Erro no banco de dados: {str(erro)}"}
    
    except Exception as erro:
        if conn:
            conn.rollback()
        return {"erro": f"Erro interno: {str(erro)}"}
    
    finally:
        desconectar_banco(conn, cursor)

def listar_candidatos():
    conn, cursor = conectar_banco()
    
    if not conn or not cursor:
        return []
    
    try:
        cursor.execute("SELECT * FROM candidatos ORDER BY data_cadastro DESC")
        candidatos = cursor.fetchall()
        
        if not candidatos:
            return []
        
        lista = []
        for candidato in candidatos:
            dict_candidato = dict(candidato)
            dict_candidato = converter_datetime_para_string(dict_candidato)
            lista.append(dict_candidato)
        
        return lista
        
    except psycopg2.Error as erro:
        return []
    
    except Exception as erro:
        return []
    
    finally:
        desconectar_banco(conn, cursor)

def buscar_candidato_por_id(candidato_id):
    conn, cursor = conectar_banco()
    
    if not conn or not cursor:
        return None
    
    try:
        cursor.execute("SELECT * FROM candidatos WHERE id = %s", (candidato_id,))
        candidato = cursor.fetchone()
        
        if candidato:
            dict_candidato = dict(candidato)
            dict_candidato = converter_datetime_para_string(dict_candidato)
            return dict_candidato
        else:
            return None
            
    except psycopg2.Error as erro:
        return None
    
    except Exception as erro:
        return None
    
    finally:
        desconectar_banco(conn, cursor)

def atualizar_candidato(candidato_id, nome=None, email=None, telefone=None, experiencia=None):
    conn, cursor = conectar_banco()
    
    if not conn or not cursor:
        return False
    
    campos_atualizacao = []
    valores = []
    
    if nome is not None:
        campos_atualizacao.append("nome = %s")
        valores.append(nome)
    if email is not None:
        campos_atualizacao.append("email = %s")
        valores.append(email)
    if telefone is not None:
        campos_atualizacao.append("telefone = %s")
        valores.append(telefone)
    if experiencia is not None:
        campos_atualizacao.append("experiencia = %s")
        valores.append(experiencia)
    
    if not campos_atualizacao:
        desconectar_banco(conn, cursor)
        return False
    
    valores.append(candidato_id)
    sql = f"UPDATE candidatos SET {', '.join(campos_atualizacao)} WHERE id = %s"
    
    try:
        cursor.execute(sql, valores)
        conn.commit()
        
        if cursor.rowcount > 0:
            return True
        else:
            return False
            
    except psycopg2.Error as erro:
        conn.rollback()
        return False
    
    except Exception as erro:
        if conn:
            conn.rollback()
        return False
    
    finally:
        desconectar_banco(conn, cursor)

def excluir_candidato(candidato_id):    
    conn, cursor = conectar_banco()
    
    if not conn or not cursor:
        return False
    
    try:
        cursor.execute("DELETE FROM candidatos WHERE id = %s", (candidato_id,))
        conn.commit()
        
        if cursor.rowcount > 0:
            return True
        else:
            return False
            
    except psycopg2.Error as erro:
        conn.rollback()
        return False
    
    except Exception as erro:
        if conn:
            conn.rollback()
        return False
    
    finally:
        desconectar_banco(conn, cursor)

def contar_candidatos():
    conn, cursor = conectar_banco()
    
    if not conn or not cursor:
        return 0
    
    try:
        cursor.execute("SELECT COUNT(*) FROM candidatos")
        resultado = cursor.fetchone()
        
        total = resultado[0] if resultado else 0
        return total
        
    except psycopg2.Error as erro:
        return 0
    
    except Exception as erro:
        return 0
    
    finally:
        desconectar_banco(conn, cursor)

def buscar_candidatos_por_email(email):
    conn, cursor = conectar_banco()
    
    if not conn or not cursor:
        return []
    
    try:
        cursor.execute("SELECT * FROM candidatos WHERE LOWER(email) = LOWER(%s)", (email,))
        candidatos = cursor.fetchall()
        
        if not candidatos:
            return []
    
        lista = []
        for candidato in candidatos:
            dict_candidato = dict(candidato)
            dict_candidato = converter_datetime_para_string(dict_candidato)
            lista.append(dict_candidato)
        
        print(f"🔍 Encontrados {len(lista)} candidatos com email '{email}'")
        return lista
        
    except psycopg2.Error as erro:
        return []
    
    except Exception as erro:
        return []
    
    finally:
        desconectar_banco(conn, cursor)

def teste_crud():
    print('testes de CRUD')

    print('teste de cadastro bem sucedido')
    resultado = cadastrar_candidato('Mario Rossi', 'mario@test.com', '11957475837', 'Dev Python')
    print(f'Resultado: {resultado}')

    print('Teste de email duplicado')
    resultado_dup = cadastrar_candidato('Armario jose', 'mario@test.com', '11485744933')
    print(f'Resultado: {resultado_dup}')

    print('Teste de listagem:')
    candidatos = listar_candidatos()
    print(f'Total encontrados: {len(candidatos)}')

    print('Teste de contagem')
    total = contar_candidatos()
    print(f'total no banco : {total}')