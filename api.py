from flask import Flask,jsonify,send_file
from datetime import datetime,timedelta,timezone
from raspador_dados import atualiza_seguridados,dados_novos_df
from dotenv import load_dotenv
import pandas as pd
import json

app = Flask(__name__)

@app.route("/FmIZF3r12r0T0YykrFOTHvKFxMbNTJjI8p7QwN3Ga7M",methods=["GET"])
def agenda_seguridados():
    data=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=-3))).strftime("%d-%m-%Y-%Hh%M")
    atualiza_seguridados()
    return f"Informações atualizadas em {data}"


@app.route("/CEARA",methods=["GET"])
def CEARA():
    # OCORRÊNCIAS POR ESTADO
    df=dados_novos_df()
    filtro=df.groupby(["Ano", "Natureza"]).size().reset_index(name="Quantidade") 
    resultado={}

    for index, linha in filtro.iterrows():
        ano=linha["Ano"]
        natureza=linha["Natureza"]
        quantidade=linha["Quantidade"]

        if ano not in resultado:
            resultado[ano]={}

        if natureza not in resultado:
            resultado[ano].update({natureza: quantidade})
    return json.dumps(resultado)

@app.route("/ANO/<int:ano>",methods=["GET"])
def ANO(ano):
    # ANO
    df=dados_novos_df()
    resultado=df[df["Ano"] == ano]
    return resultado.to_json(orient='records')

# MUNICIPIO (PESQUISÁVEL POR CÓDIGO DO IBGE)
@app.route("/MUNICIPIO/<int:cidade>",methods=["GET"])
def MUNICIPIO(cidade):
    df=dados_novos_df()
    df["CdIbge"]=df["CdIbge"]
    resultado=df[df["Município"] == cidade]    
    return resultado.to_json(orient='records')

# INDICADOR
@app.route("/INDICADOR/<indicador>",methods=["GET"])
def INDICADOR(indicador):
    df=dados_novos_df()
    df["Natureza"]=df["Natureza"].str.upper()
    resultado=df[df["Natureza"] == indicador]    
    return resultado.to_json(orient='records')

# REGIÃO ADMINISTRATIVA
@app.route("/REGIAO/<regiao>",methods=["GET"])
def REGIAO(regiao):
    df=dados_novos_df()
    df["Regiao"]=df["Regiao"].str.upper()
    resultado=df[df["Natureza"] == regiao]    
    return resultado.to_json(orient='records')