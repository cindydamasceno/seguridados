from flask import Flask,jsonify,send_file,request
from datetime import datetime,timedelta,timezone
from raspador_dados import atualiza_seguridados,dados_novos_df
from dotenv import load_dotenv
import pandas as pd
import json,os

app = Flask(__name__)

###### CREDENCIAIS ######
ATUALIZA_URL=os.getenv("ATUALIZA_URL")
#########################

@app.route(f"/{ATUALIZA_URL}",methods=["GET"])
def agenda_seguridados():
    data=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=-3))).strftime("%d-%m-%Y-%Hh%M")
    atualiza_seguridados()
    return f"Informações atualizadas em {data}"

########## QUERY PARA FORMULÁRIO HTML #############
@app.route("/API/PESQUISA",methods=["POST"])
def PESQUISA():
    # RECEBE PARAMETROS DO FORMULARIO HTML (GITPAGES)
    CONSULTA = request.json # REQUISIÇÃO API FLASK
    ano = CONSULTA.get('ANO')
    municipio = CONSULTA.get('MUNICIPIO')
    indicador = CONSULTA('INDICADOR')
    data_inicio = CONSULTA('DATA_INICIO')
    data_fim = CONSULTA('DATA_FIM')
    formato=CONSULTA('FORMATO')

    if not municipio or not indicador:
        return jsonify({'erro': 'Campos obrigatórios não preenchidos.'})
    
    # CRITÉRIOS DE PESQUISA
    filtro=dados_novos_df().copy # CRIA UMA CÓPIA PARA EVITAR CONFLITO

    if ano:
        filtro=filtro[filtro["Ano"]==ano]

    if data_inicio:
        filtro=filtro[[pd.to_datetime(filtro["Data"],format='%d-%m-%Y')] >= pd.to_datetime(data_inicio,format='%d-%m-%Y')]

    if data_fim:
        filtro=filtro[[pd.to_datetime(filtro["Data"],format='%d-%m-%Y')] <= pd.to_datetime(data_fim,format='%d-%m-%Y')]

    if formato=="CSV":
        filtro.to_csv(f"resultado_csv_{municipio}_{indicador}",index=False)
        return send_file(f"resultado_csv_{municipio}_{indicador}",as_attachment=True)

    if formato=="JSON":
        filtro.to_json(f"resultado_json_{municipio}_{indicador}", orient="records",indent=4,force_ascii=False)
        return send_file(f"resultado_json_{municipio}_{indicador}", as_attachment=True)

    if formato=="Planilha - XLSX":
        filtro.to_excel(f"resultado_excel_{municipio}_{indicador}",index=False)
        return send_file(f"resultado_excel_{municipio}_{indicador}", as_attachment=True)
    
    return "Sucesso! Verifique a caixa de download do seu dispositivo"

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