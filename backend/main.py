from fastapi import FastAPI, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import uvicorn
from datetime import datetime

from crud import (
    cadastrar_candidato,
    listar_candidatos,
    buscar_candidato_por_id,
    atualizar_candidato,
    excluir_candidato,
    contar_candidatos,
    buscar_candidatos_por_email
)
from validacao import (
    validar_candidato_completo,
    validar_id,
    limpar_dados_candidato
)
from tabelas import main

app = FastAPI(
    title="API Sistema de Candidatos",
    description="""
    Sistema de gerenciamento de candidatos de emprego

    Fucnionalidades:
    -  Cadastro de candidatos com validação completa
    - listagem e busca de candidatos
    - atualização de dados
    -  exclusão de registros 
    - estatísticas básicas 

    desenvolvido com fastapi + postgresSQL + python
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      
        "http://127.0.0.1:3000",      
        "http://localhost:3001",      
        "http://127.0.0.1:5173",      
        "http://localhost:5173",      
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:8080",      
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

class CandidatoCreate(BaseModel):
    nome: str = Field(
        ...,
        min_lenght=2,
        max_lenght=100,
        description="Nome completo do candidato",
        example="Pedro Henrique Wayne"
    )
    email: str = Field(
        ...,
        max_lenght=100,
        description="Email válido para contato",
        example="pedrostark@gmail.com"
    )
    telefone: Optional[str] = Field(
        None,
        max_lenght=20,
        description="Telefone para contato (opcional)",
        example="11958544022"
    )
    experiencia: Optional[str] = Field(
        None, 
        max_lenght=5000,
        description="Experiência profissional (opcional)",
        example="Dwesenvolvedor Python há 3 anos, especialista em Django e Flask..."
    )
    class Config:
        schema_extra = {
            "example": {
                "nome": "Pedro Stark Wayne",
                "email": "pedrostarkwayne@gmail.com",
                "telefone": "11958544022",
                "experiencia": "Desenvolvedor html que desenvolve a 2 meses com o curso da udemy, estou me candidatando a uma vaga senior pois sou fã do harvey specter e sei que sou o melhor, quero 70 mil de salário"
            }
        }

class CandidatoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_lenght = 2, max_lenght=100)
    email: Optional[str] = Field(None, max_lenght=100)
    telefone: Optional[str] = Field(None, max_lenght= 20)
    experiencia: Optional[str] = Field(None, max_lenght=5000)

    class Config:
        schema_extra = {
            "example": {
                "nome": "Pedro wayne atualizado",
                "email": "pedrowayne@gmail.com"
            }
        }

class CandidatoResponse(BaseModel):
    id: int = Field(description="id único do candidato")
    nome: str = Field(description="Nome completo")
    email: str = Field(description="Email de contato")
    telefone: Optional[str] = Field(description="Telefone(pode ser nulo)")
    experiencia: Optional[str] = Field(description="Experiência profissional")
    data_cadastro: str = Field(description="Data de hora do cadastro")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "nome": "Pedro Wayne",
                "email": "pedro@gmail.com",
                "telefone": "11958544022",
                "experiencia": "Desenvolvedor Python há 3 anos",
                "data_cadastro": "2024-03-15T10:30:00"
            }
        }

class MessageResponse(BaseModel):
    mensagem: str = Field(description="Mensagem de confirmação")

    class Config:
        schema_extra = {
            "example": {
                "mensagem": "Candidato atualizado com sucesso"
            }
        }

class ErrorResponse(BaseModel):
    erro: str = Field(description="Descrição do erro")
    detalhes: Optional[list[str]] = Field(None, description="Lista de erros específicos")

    class Config:
        schema_extra = {
            "example": {
                "erro": "Dados inválidos",
                "detalhes": [
                    "Nome: deve ter pelo menos 2 caracteres",
                    "Email: formato inválido"
                ]
            }
        }

class EstatisticasResponse(BaseModel):
    total_candidatos: int
    com_telefone: int
    com_experiencia: int 
    percentual_com_telefone: int
    percentual_com_experiencia: int

    class Config:
        schema_extra = {
            "example": {
                "total_candidatos": 150,
                "com_telefone": 120,
                "com_experiencia": 100,
                "percentual_com_telefone": 80.0,
                "percentual_com_experiencia": 66.67
            }
        }

@app.on_event("startup")
async def startup_event():
    print('Iniciando api')
    print('horário: {datetime.now()}')

    sucesso = main()

    if sucesso:
        print('api pronta')
        print('documentação: http://localhost:8000/docs')

@app.on_event("shutdown")
async def shutdown_event():
    print('parando api')
    print('horário: {datetime.now()}')

@app.get("/", response_model=MessageResponse, tags=["Sistema"])
async def raiz():
    return{
        "mensagem":"api funcionando"
    }

@app.get("/health", tags=["Sistema"])
async def health_check():
    try:
        total_candidatos = contar_candidatos()

        return {
            "status": "healthy",
            "service": "API Sistema de candidatos",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "total_candidatos": total_candidatos
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f'Problema de conectividade : {str(e)}'
        )

@app.post("/candidatos",
          response_model=CandidatoResponse,
          status_code=status.HTTP_201_CREATED,
          tags=["Candidatos"])
async def criar_candidato(candidato: CandidatoCreate):
    valido, erros = validar_candidato_completo(
        candidato.nome,
        candidato.email,
        candidato.telefone,
        candidato.experiencia
    )

    if not valido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "erro": "Dados inválidos",
                "detalhes": erros
            }
        )
    
    dados_limpos = limpar_dados_candidato(
        candidato.nome,
        candidato.email,
        candidato.telefone,
        candidato.experiencia
    )

    novo_candidato = cadastrar_candidato(
        dados_limpos['nome'],
        dados_limpos['email'],
        dados_limpos.get('telefone'),
        dados_limpos.get('experiencia')
    )

    if "erro" in novo_candidato:
        if "unique constraint" in str(novo_candidato["erro"]).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "erro": "Email já cadastrado",
                    "detalhes": ["Este email já está sendo usado por outro candidato"]
                }
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "erro": "Erro interno do servidor",
                    "detalhes": [str(novo_candidato["erro"])]
                }
            )
        
    return novo_candidato

@app.get("/candidatos", 
         response_model=List[CandidatoResponse],
         tags=["Candidatos"])
async def obter_candidatos(
    limite: Optional[int] = Query(None, ge=1, le=100, description="Limite de resultados (1-100)"),
    busca: Optional[str] = Query(None, min_length=2, description="Busca por nome ou email")
):
    try:
        candidatos = listar_candidatos()
        
        if candidatos is None:
            candidatos = []
        
        if not isinstance(candidatos, list):
            candidatos = []
        
        if busca:
            busca_lower = busca.lower()
            candidatos_filtrados = []
            for c in candidatos:
                nome_match = busca_lower in c.get('nome', '').lower()
                email_match = busca_lower in c.get('email', '').lower()
                if nome_match or email_match:
                    candidatos_filtrados.append(c)
            candidatos = candidatos_filtrados
        
        if limite and len(candidatos) > limite:
            candidatos = candidatos[:limite]
        return candidatos
        
    except Exception as error:
        print(f'erro {error}')
        return []

@app.get("/candidatos/{candidato_id}", 
         response_model=CandidatoResponse,
         tags=["Candidatos"])
async def obter_candidato(candidato_id: int):
    id_valido, msg_id = validar_id(candidato_id)
    if not id_valido:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"erro": msg_id}
        )
    candidato = buscar_candidato_por_id(candidato_id)

    if not candidato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
               "erro": f"Candidato com ID {candidato_id} não encontrado",
               "detalhes": ["Verifique se o ID está correto ou se o candidato não foi excluído"]
           }
       )
    return candidato

@app.put("/candidatos/{candidato_id}", 
        response_model=MessageResponse,
        tags=["Candidatos"])
async def atualizar_candidato_endpoint(candidato_id: int, candidato: CandidatoUpdate):
    id_valido, msg_id = validar_id(candidato_id)
    if not id_valido:
        raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST,
           detail={"erro": msg_id}
       )
    
    candidato_existente = buscar_candidato_por_id(candidato_id)
    if not candidato_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
               "erro": f"Candidato com ID {candidato_id} não encontrado",
               "detalhes": ["Não é possível atualizar candidato que não existe"]
           }
        )
    erros_validacao = []

    from validacao import validar_nome, validar_email, validar_telefone, validar_experiencia
    
    if candidato.nome is not None:
        valido, msg = validar_nome(candidato.nome)
        if not valido:
            erros_validacao.append(f"Nome: {msg}")

        if candidato.email is not None:
            valido, msg = validar_email(candidato.email)
            if not valido:
                erros_validacao.append(f'Email: {msg}')
            else:
                candidatos_com_email = buscar_candidatos_por_email(candidato.email)
                outros_candidatos = [c for c in candidatos_com_email if c['id'] != candidato_id]
                if outros_candidatos:
                    erros_validacao.append("Email: já está sendo usado")
        
        if candidato.telefone is not None:
            valido, msg = validar_telefone(candidato.telefone)
            if not valido:
                erros_validacao.append(f'Telefone: {msg}')

        if candidato.experiencia is not None:
            valido, msg = validar_experiencia(candidato.experiencia)
            if not valido:
                erros_validacao.append(f'Experiência: {msg}')
            
        if erros_validacao:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "erro": "Dados inválidos",
                    "detalhes": erros_validacao
                }
            )
        
        dados_para_atualizar = {}

        if candidato.nome is not None:
            dados_para_atualizar['nome'] = candidato.nome.strip().title()
        if candidato.email is not None:
            dados_para_atualizar['email'] = candidato.email.strip().lower()
        if candidato.telefone is not None:
            import re
            dados_para_atualizar['telefone'] = re.sub(r'[^\d]', '', candidato.telefone.strip())
        if candidato.experiencia is not None:
            dados_para_atualizar['experiencia'] = candidato.experiencia.strip()
        
        try:
            sucesso = atualizar_candidato(
                candidato_id,
                dados_para_atualizar.get('nome'),
                dados_para_atualizar.get('email'),
                dados_para_atualizar.get('telefone'),
                dados_para_atualizar.get('experiencia')
            )
            if not sucesso:
               raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "erro": "Falha na atualização",
                        "detalhes": ["Erro interno ao salvar alterações"]
                    }
                )
            return {"mensagem": f"Candidato ID {candidato_id} atualizado com sucesso"}
        
        except Exception as e:
            if "unique constraint" in str(e).lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "erro": "Email já existe",
                        "detalhes": ["Este email já está sendo usado por outro candidato"]
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "erro": "Erro interno do servidor",
                        "detalhes": [str(e)]
                    }
                )

@app.delete("/candidatos/{candidato_id}", 
          response_model=MessageResponse,
          tags=["Candidatos"])
async def excluir_candidato_endpoint(candidato_id: int):
    id_valido, msg_id = validar_id(candidato_id)
    if not id_valido:
        raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST,
           detail={"erro": msg_id}
       )
    candidato_existente = buscar_candidato_por_id(candidato_id)
    if not candidato_existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
               "erro": f"Candidato com ID {candidato_id} não encontrado",
               "detalhes": ["Não é possível excluir candidato que não existe"]
           }
       )
    try:
        sucesso =  excluir_candidato(candidato_id)

        if not sucesso:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                   "erro": "Falha na exclusão",
                   "detalhes": ["Erro interno ao excluir candidato"]
               }
           )
       
        return {
           "mensagem": f"Candidato '{candidato_existente['nome']}' (ID {candidato_id}) excluído permanentemente"
        }
       
    except Exception as e:
       raise HTTPException(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           detail={
               "erro": "Erro interno do servidor",
               "detalhes": [str(e)]
           }
       )
    
@app.get("/candidatos/stats/geral", 
        response_model=EstatisticasResponse,
        tags=["Estatísticas"])
async def estatisticas_gerais():
    try:
        candidatos = listar_candidatos()
        total = len(candidatos)

        com_telefone = len([
            c for c in candidatos
            if c.get('telefone') and c['telefone'].strip()
        ])

        com_experiencia = len([
            c for c in candidatos
            if c.get('experiencia') and c['experiencia'].strip()
        ])

        percentual_telefone = round((com_telefone / total *100) if total >0 else 0,2)
        percentual_experiencia = round((com_experiencia / total * 100) if total > 0 else 0,2)

        return {
            "total_candidatos": total,
            "com_telefone": com_telefone,
            "com_experiencia": com_experiencia,
            "percentual_com_telefone": percentual_telefone,
            "percentual_com_experiencia": percentual_experiencia
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
               "erro": "Erro ao calcular estatísticas",
               "detalhes": [str(e)]
           }
       )

@app.get("/candidatos/buscar", 
        response_model=List[CandidatoResponse],
        tags=["Busca"])
async def buscar_candidatos_avancado(
   nome: Optional[str] = Query(None, min_length=2, description="Buscar por nome"),
   email: Optional[str] = Query(None, min_length=3, description="Buscar por email"),
   tem_telefone: Optional[bool] = Query(None, description="Filtrar por ter telefone"),
   tem_experiencia: Optional[bool] = Query(None, description="Filtrar por ter experiência")
):
    try:
        candidatos = listar_candidatos()

        if nome: 
            nome_lower = nome.lower()
            candidatos = [
                c for c in candidatos
                if nome_lower in c ['nome'].lower()
            ]
        if email:
            email_lower = email.lower()
            candidatos = [
                c for c in candidatos
                if email_lower in c['email'].lower()
            ]
        if tem_telefone is not None:
            if tem_telefone:
                candidatos  = [
                    c for c in candidatos
                    if c.get('telefone') and c['telefone'].strip()
                ]
            else:
                candidatos = [
                    c for c in candidatos
                    if not c.get('telefone') or not c['telefone'].strip()
                ]
        if tem_experiencia is not None:
            if tem_experiencia:
                candidatos = [
                    c for c in candidatos
                    if c.get('experiencia') and c['experiencia'].strip()
                ]
            else:
                candidatos = [
                    c for c in candidatos
                    if not c.get('experiencia') or not c ['experiencia'].strip()
                ]
        return candidatos

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
               "erro": "Erro na busca avançada",
               "detalhes": [str(e)]
           }
       )
    
if __name__ == "__main__":
    print('iniciando api')
    print('documentação: http://localhost:8000/docs')
    print('Health check: http://localhost:8000/health')
    print('ctrl+c para parar')

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
