from flask import Flask,jsonify,send_file,request
from datetime import datetime,timedelta,timezone
from raspador_dados import atualiza_seguridados,dados_novos_df
from dotenv import load_dotenv
import pandas as pd
import json,os

app = Flask(__name__)

###### CREDENCIAIS ######
load_dotenv()
ATUALIZA_URL=os.getenv("ATUALIZA_URL")
#########################

@app.route(f"/{ATUALIZA_URL}",methods=["GET"])
def agenda_seguridados():
    data=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=-3))).strftime("%d-%m-%Y-%Hh%M")
    atualiza_seguridados()
    return f"Informações atualizadas em {data}"

########## QUERY PARA FORMULÁRIO HTML #############
@app.route("/API/PESQUISA",methods=["POST"])
def PESQUISA(CONSULTA):
    # RECEBE PARAMETROS DO FORMULARIO HTML (GITPAGES)
    CONSULTA = request.json # REQUISIÇÃO API FLASK
    ano = CONSULTA.get('ANO', None)
    municipio = CONSULTA.get('MUNICIPIO', None)
    indicador = CONSULTA('INDICADOR', None)
    data_inicio = CONSULTA('DATA_INICIO', None)
    data_fim = CONSULTA('DATA_FIM', None)

    if not municipio or indicador:
        return jsonify({'erro': 'Campos obrigatórios não preenchidos.'})
    
    # CRITÉRIOS DE PESQUISA
    filtro=dados_novos_df().copy # CRIA UMA CÓPIA PARA EVITAR CONFLITO
    parametros = {
        'Ano': lambda x: filtro['Ano'] == int(ano),
        'Municipio': lambda x: filtro['Municipio'] == municipio,
        'Indicador': lambda x: filtro['Indicador'] == indicador,
        'DataInicio': lambda x: pd.to_datetime(filtro['Data']) >= pd.to_datetime(data_inicio),
        'DataFim': lambda x: pd.to_datetime(filtro['Data']) <= pd.to_datetime(data_fim)
    }

    for parametro, valor in parametros.items():
        if valor and parametro in parametros:
            filtro = filtro[parametros[parametro](valor)]

    return filtro.to_json(orient='records')

##################################################

########## ENDPOINTS PARA OUTRAS REQUISIÇÃO #############
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
    resultado=df[df["CdIbge"] == cidade]    
    return resultado.to_json(orient='records')

# INDICADOR
@app.route("/INDICADOR/<int:indicador>",methods=["GET"])
def INDICADOR(indicador):
    df=dados_novos_df()
    resultado=df[df["CdIndicador"] == indicador]    
    return resultado.to_json(orient='records',indent=4,force_ascii=False)

@app.route("/REGIAO",methods=["GET"])
def REGIAO_CONSOLIDADO():
    # OCORRÊNCIAS SOMADAS POR REGIAO ADMINISTRATIVA
    df=dados_novos_df()
    filtro=df.groupby(["Ano", "Natureza", "Regiao"]).size().reset_index(name="Quantidade") 
    resultado={}

    for index, linha in filtro.iterrows():
        regiao=linha["Regiao"]
        ano=linha["Ano"]
        natureza=linha["Natureza"]
        quantidade=linha["Quantidade"]

        if regiao not in resultado:
            resultado[regiao]={}

        if ano not in resultado[regiao]:
            resultado[regiao][ano]={}

        if natureza not in resultado[regiao][ano]:
            resultado[regiao][ano].update({natureza: quantidade})
    return json.dumps(resultado)

# REGIÃO ADMINISTRATIVA ESPECÍFICA 
@app.route("/REGIAO/<int:regiao>",methods=["GET"])
def REGIAO(regiao):
    df=dados_novos_df()
    resultado=df[df["CdRegiao"] == regiao]    
    return resultado.to_json(orient='records',indent=4,force_ascii=False)

if __name__=="__main__":
    app.run(debug=True)