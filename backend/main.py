import os  # <-- IMPORTANTE: Adicionado para ler o cofre
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import mysql.connector
import pandas as pd

app = FastAPI()

# Acesso liberado para a sua Vercel (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def conectar_banco():
    # Conectando ao MySQL na nuvem (Aiven) usando a Variável de Ambiente (Cofre)
    return mysql.connector.connect(
        host="mysql-1f716a77-joaquimwisnieski55-bba5.g.aivencloud.com",
        port=23046,
        user="avnadmin",
        password=os.getenv("DB_PASSWORD"), # <-- A MÁGICA DA SEGURANÇA AQUI!
        database="defaultdb"
    )

class Metricas(BaseModel):
    data_registro: str
    qtd_leads: int
    qtd_vendas: int
    taxa_conversao: float

@app.get("/buscar-metricas")
def buscar_metricas():
    conexao = conectar_banco()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("SELECT SUM(qtd_leads) as leads, SUM(qtd_vendas) as vendas FROM metricas")
    res = cursor.fetchone()
    conexao.close()
    if not res or res['leads'] is None:
        return {"leads": 0, "vendas": 0, "conversao": 0}
    conv = round((res['vendas'] / res['leads']) * 100, 1)
    return {"leads": res['leads'], "vendas": res['vendas'], "conversao": conv}

@app.post("/salvar-metricas")
def salvar_metricas(dados: Metricas):
    conexao = conectar_banco()
    cursor = conexao.cursor()
    sql = "INSERT INTO metricas (data_registro, qtd_leads, qtd_vendas, taxa_conversao) VALUES (%s, %s, %s, %s)"
    val = (dados.data_registro, dados.qtd_leads, dados.qtd_vendas, dados.taxa_conversao)
    cursor.execute(sql, val)
    conexao.commit() # ESSENCIAL: Salva no disco
    conexao.close()
    return {"status": "Sucesso"}

@app.get("/predicao-15-dias")
def calcular_predicao():
    conexao = conectar_banco()
    df = pd.read_sql("SELECT qtd_leads, qtd_vendas FROM metricas ORDER BY id DESC LIMIT 15", conexao)
    conexao.close()
    if len(df) < 3:
        return {"status": "Aguardando", "proximo_ciclo": {"leads_estimados": 0, "vendas_estimadas": 0}}
    leads_est = int(df['qtd_leads'].mean() * 15)
    vendas_est = int(df['qtd_vendas'].mean() * 15)
    return {"status": "Sucesso", "proximo_ciclo": {"leads_estimados": leads_est, "vendas_estimadas": vendas_est}}

@app.get("/exportar-dados")
def exportar_dados():
    conexao = conectar_banco()
    df = pd.read_sql("SELECT data_registro, qtd_leads, qtd_vendas, taxa_conversao FROM metricas", conexao)
    conexao.close()
    caminho = "relatorio_numeros.xlsx"
    df.to_excel(caminho, index=False)
    return FileResponse(path=caminho, filename="Relatorio_MKT.xlsx")

# ROTA DE EMERGÊNCIA: Deleta o último registro inserido
@app.delete("/deletar-ultimo")
def deletar_ultimo():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    # Deleta apenas a linha com o ID mais alto (o último que você enviou)
    cursor.execute("DELETE FROM metricas ORDER BY id DESC LIMIT 1")
    conexao.commit()
    conexao.close()
    return {"status": "Registro removido com sucesso"}

#teste