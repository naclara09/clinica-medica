from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg

app = FastAPI(title="Clínica NovaVita")

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
        host='127.0.0.1'
    )

@app.get("/")
def home():
    return {"status": "API Clínica NovaVita Rodando"}


@app.post("/items")
async def criar(p: Paciente):
    conn = await get_conn()
    await conn.execute("INSERT INTO pacientes (nome, cpf, telefone, historico) VALUES ($1, $2, $3, $4)",
                       p.nome, p.cpf, p.telefone, p.historico)
    await conn.close()
    return {"msg": "Cadastrado!"}

@app.get("/items")
async def listar():
    conn = await get_conn()
    rows = await conn.fetch("SELECT * FROM pacientes")
    await conn.close()
    return [dict(r) for r in rows]

@app.get("/items/{id}")
async def buscar(id: int):
    conn = await get_conn()
    row = await conn.fetchrow("SELECT * FROM pacientes WHERE id = $1", id)
    await conn.close()
    if not row: raise HTTPException(status_code=404)
    return dict(row)

@app.put("/items/{id}")
async def atualizar(id: int, p: Paciente):
    conn = await get_conn()
    await conn.execute("UPDATE pacientes SET nome=$1, cpf=$2, telefone=$3, historico=$4 WHERE id=$5",
                       p.nome, p.cpf, p.telefone, p.historico, id)
    await conn.close()
    return {"msg": "Atualizado!"}

@app.delete("/items/{id}")
async def deletar(id: int):
    conn = await get_conn()
    await conn.execute("DELETE FROM pacientes WHERE id = $1", id)
    await conn.close()
    return {"msg": "Removido!"}