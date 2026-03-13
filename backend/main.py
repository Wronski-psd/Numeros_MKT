import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import mysql.connector
import pandas as pd

app = FastAPI()

# Configuração de CORS: Essencial para comunicação Vercel -> Render
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def conectar_banco():
    # Conexão com Aiven usando a variável de ambiente DB_PASSWORD do Render
    try:
        return mysql.connector.connect(
            host="mysql-1f716a77-joaquimwisnieski55-bba5.g.aivencloud.com",
            port=23046,
            user="avnadmin",
            password=os.getenv("DB_PASSWORD"),
            database="marketing_db"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro de conexão ao banco: {str(e)}")

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
        
        leads = int(res['leads']) if res and res['leads'] is not None else 0
        vendas = int(res['vendas']) if res and res['vendas'] is not None else 0
        
        if leads == 0:
            return {"leads": 0, "vendas": 0, "conversao": 0}
            
        conv = round((vendas / leads) * 100, 1)
        return {"leads": leads, "vendas": vendas, "conversao": float(conv)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar métricas: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Erro ao salvar dados: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Erro no cálculo de predição: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Erro ao exportar Excel: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Erro ao deletar: {str(e)}")