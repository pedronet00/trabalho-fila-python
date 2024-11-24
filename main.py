from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

app = FastAPI()

# Simula uma fila de atendimento com instâncias do modelo Cliente
fila = [
    {"id": 1, "nome": "Cliente 1", "atendido": False, "tipo_atendimento": "N", "data_chegada": datetime.utcnow()},
    {"id": 2, "nome": "Cliente 2", "atendido": True, "tipo_atendimento": "P", "data_chegada": datetime.utcnow()},
    {"id": 3, "nome": "Cliente 3", "atendido": False, "tipo_atendimento": "N", "data_chegada": datetime.utcnow()},
]

class Cliente(BaseModel):
    id: int
    nome: str = Field(..., max_length=20)
    tipo_atendimento: str = Field(..., pattern="^(N|P)$")  # N para normal, P para prioritário
    data_chegada: datetime = Field(default_factory=datetime.utcnow)
    atendido: bool = False

    class Config:
        orm_mode = True  # Permite que o Pydantic converta dicionários em instâncias de modelo

# Função para ordenar a fila, separando os clientes prioritários dos normais
def ordenar_fila():
    global fila
    fila = sorted(fila, key=lambda c: (c['tipo_atendimento'] == "N", c['id']))

# Endpoint GET /fila
@app.get("/fila")
def obter_fila():
    global fila
    print("Conteúdo atual da fila:", fila)
    
    # Filtra os clientes que ainda não foram atendidos
    fila_nao_atendida = [c for c in fila if not c.get("atendido")]
    return fila_nao_atendida

# Endpoint GET /fila/{id}
@app.get("/fila/{id}", response_model=Cliente)
def obter_cliente(id: int):
    # Busca o cliente pelo ID na fila
    cliente = next((c for c in fila if c["id"] == id), None)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado na fila")
    
    # Retorna o cliente encontrado com todos os dados no formato esperado pelo Pydantic
    return Cliente(**cliente)

# Endpoint POST /fila
@app.post("/fila")
def adicionar_cliente(cliente: Cliente):
    cliente.id = len(fila) + 1  # Define o ID com base na posição atual na fila
    fila.append(cliente.dict())  # Adiciona o cliente na fila como dicionário
    return {"message": "Cliente adicionado com sucesso", "cliente": cliente}

# Endpoint PUT /fila
@app.put("/fila")
def atualizar_fila():
    global fila
    if not fila:
        return {"message": "A fila está vazia"}

    for cliente in fila:
        if not cliente['atendido']:
            # Simula o atendimento
            cliente['atendido'] = True  # Marca como atendido
            break  # Só atende o primeiro cliente não atendido

    ordenar_fila()
    return {"message": "Fila atualizada com sucesso"}

# Endpoint DELETE /fila/{id}
@app.delete("/fila/{id}")
def remover_cliente(id: int):
    global fila
    cliente = next((c for c in fila if c["id"] == id), None)
    if cliente is None:
        raise HTTPException(status_code=404, detail="Cliente não encontrado na fila")

    fila.remove(cliente)

    # Reorganizar as posições da fila
    for i, cliente_restante in enumerate(fila):
        cliente_restante['id'] = i + 1

    return {"message": "Cliente removido com sucesso"}
