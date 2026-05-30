from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from fastapi.security import APIKeyHeader
import asyncpg
from typing import List

app = FastAPI(title="Clínica NovaVita")

API_KEY = "123456"
api_key_header = APIKeyHeader(name="x-api-key")

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida"
        )
    return True

class Paciente(BaseModel):
    nome: str
    cpf: str
    telefone: str
    historico: str

async def get_conn():
    return await asyncpg.connect(
        user='postgres', 
        password='12345', 
        database='postgres', 
        host='localhost',
    )

@app.get("/") 
def home():
    return {"status": "API Clínica NovaVita Rodando"}

@app.post("/items", status_code=status.HTTP_201_CREATED, dependencies=[Depends(verify_api_key)])
async def criar(p: Paciente):
    conn = await get_conn()
    try:
        await conn.execute(
            "INSERT INTO pacientes (nome, cpf, telefone, historico) VALUES ($1, $2, $3, $4)",
            p.nome, p.cpf, p.telefone, p.historico
        )
        return {"msg": "Cadastrado!"}
    finally:
        await conn.close()

@app.get("/items", response_model=List[dict], dependencies=[Depends(verify_api_key)])
async def listar():
    conn = await get_conn()
    try:
        rows = await conn.fetch("SELECT * FROM pacientes")
        return [dict(r) for r in rows]
    finally:
        await conn.close()

@app.get("/items/{id}", dependencies=[Depends(verify_api_key)])
async def buscar(id: int):
    conn = await get_conn()
    try:
        row = await conn.fetchrow("SELECT * FROM pacientes WHERE id = $1", id)
        if not row: 
            raise HTTPException(status_code=404, detail="Paciente não encontrado")
        return dict(row)
    finally:
        await conn.close()

@app.put("/items/{id}", dependencies=[Depends(verify_api_key)])
async def atualizar(id: int, p: Paciente):
    conn = await get_conn()
    try:
        result = await conn.execute(
            "UPDATE pacientes SET nome=$1, cpf=$2, telefone=$3, historico=$4 WHERE id=$5",
            p.nome, p.cpf, p.telefone, p.historico, id
        )
        if result == "UPDATE 0":
            raise HTTPException(status_code=404, detail="ID não encontrado para atualização")
        return {"msg": "Atualizado!"}
    finally:
        await conn.close()

@app.delete("/items/{id}", dependencies=[Depends(verify_api_key)])
async def deletar(id: int):
    conn = await get_conn()
    try:
        result = await conn.execute("DELETE FROM pacientes WHERE id = $1", id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="ID não encontrado para exclusão")
        return {"msg": "Removido!"}
    finally:
        await conn.close()                                                                                                               