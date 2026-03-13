import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import mysql.connector
import pandas as pd

app = FastAPI()

# AJUSTE DE CORS: allow_credentials deve ser False quando usamos origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def conectar_banco():
    # AJUSTADO: Agora apontando para 'marketing_db' para bater com seu script SQL
    return mysql.connector.connect(
        host="mysql-1f716a77-joaquimwisnieski55-bba5.g.aivencloud.com",
        port=23046,
        user="avnadmin",
        password=os.getenv("DB_PASSWORD"),
        database="marketing_db"
    )

class Metricas(BaseModel):
    data_registro: str
    qtd_leads: int
    qtd_vendas: int
    taxa_conversao: float

@app.get("/buscar-metricas")
def buscar_metricas():
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT SUM(qtd_leads) as leads, SUM(qtd_vendas) as vendas FROM metricas")
        res = cursor.fetchone()
        conexao.close()
        if not res or res['leads'] is None:
            return {"leads": 0, "vendas": 0, "conversao": 0}
        conv = round((res['vendas'] / res['leads']) * 100, 1)
        return {"leads": res['leads'], "vendas": res['vendas'], "conversao": conv}
    except Exception as e:
        return {"error": str(e)}

@app.post("/salvar-metricas")
def salvar_metricas(dados: Metricas):
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()
        sql = "INSERT INTO metricas (data_registro, qtd_leads, qtd_vendas, taxa_conversao) VALUES (%s, %s, %s, %s)"
        val = (dados.data_registro, dados.qtd_leads, dados.qtd_vendas, dados.taxa_conversao)
        cursor.execute(sql, val)
        conexao.commit()
        conexao.close()
        return {"status": "Sucesso"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/predicao-15-dias")
def calcular_predicao():
    try:
        conexao = conectar_banco()
        df = pd.read_sql("SELECT qtd_leads, qtd_vendas FROM metricas ORDER BY id DESC LIMIT 15", conexao)
        conexao.close()
        if len(df) < 3:
            return {"status": "Aguardando", "proximo_ciclo": {"leads_estimados": 0, "vendas_estimadas": 0}}
        leads_est = int(df['qtd_leads'].mean() * 15)
        vendas_est = int(df['qtd_vendas'].mean() * 15)
        return {"status": "Sucesso", "proximo_ciclo": {"leads_estimados": leads_est, "vendas_estimadas": vendas_est}}
    except Exception as e:
        return {"error": str(e)}

@app.get("/exportar-dados")
def exportar_dados():
    try:
        conexao = conectar_banco()
        df = pd.read_sql("SELECT data_registro, qtd_leads, qtd_vendas, taxa_conversao FROM metricas", conexao)
        conexao.close()
        caminho = "relatorio_numeros.xlsx"
        df.to_excel(caminho, index=False)
        return FileResponse(path=caminho, filename="Relatorio_MKT.xlsx")
    except Exception as e:
        return {"error": str(e)}

@app.delete("/deletar-ultimo")
def deletar_ultimo():
    try:
        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM metricas ORDER BY id DESC LIMIT 1")
        conexao.commit()
        conexao.close()
        return {"status": "Registro removido com sucesso"}
    except Exception as e:
        return {"error": str(e)}