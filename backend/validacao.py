import re
from typing import List, Tuple

def validar_email(email: str) -> Tuple[bool, str]:
    if not email: 
        return False, "Email é obrigatório"
    if len(email) > 100:
        return False, "Email muito longo"
    
    padrao_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if re.match(padrao_email, email):
        return True, "Email válido"
    else:
        return False, "Formato de email inválido, exempplo: usuario@gmail.com"
    
def validar_nome(nome: str) -> Tuple[bool, str]:
    if not nome:
        return False, "Nome é obrigatório"
    
    nome_limpo = nome.strip()

    if len(nome)< 2:
        return False, "Nome precisa ter mais de 2 caracteres"
    
    if len(nome)> 100:
        return False, "Nome é muito longo"
    
    padrao_nome = r'^[a-zA-ZÀ-ÿ\s\-\']+$'

    if re.match(padrao_nome, nome_limpo):
        return True, "Nome válido"
    
    else:
        return False, "Nome inválido"
    
def validar_telefone(telefone:str)-> Tuple[bool,str]:
    if not telefone:
        return True
    
    if len(telefone)>20:
        return False, "Telefone muito longo"
    
    telefone_limpo = re.sub(r'[^\d]', '', telefone)

    if len(telefone_limpo)<10 or len(telefone_limpo) > 11:
        return False, "Telefone dever ter 10 ou 11 dígitos"
    
    if len(telefone_limpo) >= 2:
        ddd = int(telefone_limpo[:2])
        if ddd <11 or ddd> 99:
            return False
    
    if telefone_limpo == "11111111111" or telefone_limpo == "0000000000":
        return False, "Número de telefone inválido"
    
    return True, "Telefone válido"

def validar_experiencia(experiencia: str) -> Tuple[bool, str]:
    if not experiencia:
        return True
    
    experiencia_limpa = experiencia.strip()

    if len(experiencia_limpa) > 5000:
        return False, "máximo de 500 caracteres"
    
    if len(experiencia_limpa) < 10:
        return False, "Mínimo de 10 caracteres"
    
    return True, "Válido"

def validar_senha(senha: str) -> Tuple[bool, str]:
    if not senha:
        return False, "senha é obrigatória"
    
def validar_id(id_valor)-> Tuple[bool, str]:
    try:
        id_numero = int(id_valor)

        if id_numero <= 0:
            return False, "ID deve ser número positivo"
    
        return True, 'id válido'
    except(ValueError, TypeError):
        return False, "id deve ser um número"
    
    
def validar_candidato_completo(nome: str, email:str, telefone: str= None, experiencia: str=None)-> Tuple[bool, List[str]]:
    erros = []

    nome_valido , msg_nome = validar_nome(nome)
    if not nome_valido:
        erros.append(f'Nome {msg_nome}')

    email_valido, msg_email = validar_email(email)
    if not email_valido:
        erros.append(f'Email: {msg_email}')
    
    telefone_valido, msg_telefone = validar_telefone(telefone)
    if not telefone_valido:
       erros.append(f'telefone{msg_telefone}')

    experiencia_valida, msg_experiencia = validar_experiencia(experiencia) 
    if not experiencia_valida:
        erros.append(f'experiencia{msg_experiencia}')

    if not erros:
        return True, ['Todos os dados são válidos']
    else:
        return False, erros
    
def limpar_dados_candidato(nome:  str, email:str, telefone: str = None, experiencia: str = None) -> dict:
    dados_limpos = {}

    if nome:
        dados_limpos['nome'] =  nome.strip().title()
    
    if email:
        dados_limpos['email'] = email.strip().lower()

    if telefone:
        telefone_limpo = re.sub(r'[^\d]', '', telefone.strip())
        dados_limpos['telefone'] = telefone_limpo

    if experiencia:
        dados_limpos['experiencia'] = experiencia.strip()

    return dados_limpos

def testar_validacao():
    print('teste de validação')
    
    print("Validações bem-sucedidas:")
    nome_ok, msg = validar_nome("Pedro Silva")
    print(f"Nome válido: {nome_ok} - {msg}")
    
    email_ok, msg = validar_email("pedro@gmail.com")
    print(f"Email válido: {email_ok} - {msg}")
    
    tel_ok, msg = validar_telefone("11999887766")
    print(f"Telefone válido: {tel_ok} - {msg}")
    
    print("Validações mal-sucedidas:")
    nome_erro, msg = validar_nome("A")
    print(f"Nome inválido: {nome_erro} - {msg}")
    
    email_erro, msg = validar_email("email_invalido")
    print(f"Email inválido: {email_erro} - {msg}")
    
    tel_erro, msg = validar_telefone("123")
    print(f"Telefone inválido: {tel_erro} - {msg}")
    
    print("Validação completa:")
    valido, erros = validar_candidato_completo("", "email_ruim", "123", "abc")
    print(f"Válido: {valido}")
    print(f"Erros: {erros}")

    
