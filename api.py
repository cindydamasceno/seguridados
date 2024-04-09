from flask import Flask,jsonify,send_file,request,render_template
from datetime import datetime,timedelta,timezone
from raspador_dados import atualiza_seguridados,dados_novos_df
from dotenv import load_dotenv
import pandas as pd
import json,os

app = Flask(__name__,template_folder="templates")

###### CREDENCIAIS ######
ATUALIZA_URL=os.getenv("ATUALIZA_URL")

## ACESSO AO BANCO DE DADOS NOVOS
df=dados_novos_df()

# VARIAVEL GLOVAL PARA PEGAR RASPADOR
data_raspagem=None

@app.route("/",methods=["GET"])
def home():
    global data_raspagem
    indicadores=sorted([indicador for indicador in df["Natureza"].unique()])
    regioes=sorted([regiao for regiao in df["Regiao"].unique()])
    municipios=sorted([municipio for municipio in df["Município"].unique()])
    data_max=pd.to_datetime(df["Data"].iloc[-1],format="%d-%m-%Y")
    anos=sorted([ano for ano in df["Ano"].unique()])
    return render_template("index.html",data_raspagem=data_raspagem,anos=anos,indicadores=indicadores,regioes=regioes,municipios=municipios,data_max=data_max)

@app.route(f"/{ATUALIZA_URL}",methods=["GET"])
def agenda_seguridados():
    global data_raspagem
    data_raspagem=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=-3))).strftime("%d-%m-%Y-%Hh%M")
    atualiza_seguridados()
    return f"Informações atualizadas em {data_raspagem}"

# FORMULÁRIOS A PARTIR DAQUI

# FORMULÁRIO REGIAO
@app.route("/API/REGIAO", methods=["POST"])
def API_REGIAO():
    # RECEBE PARAMETROS DO FORMULÁRIO DO ESTADO
    ano = request.form.get('ano_regiao')
    regiao = request.form.get('regiao_regiao')
    indicador = request.form.get('indicador_regiao')
    data_inicio = request.form.get('data_inicio_regiao')
    data_fim = request.form.get('data_fim_regiao')
    formato=request.form.get('formato_regiao')

    filtro=df.copy() # PARA NÃO SOBRESCREVER

    if not regiao or not indicador:
        return "Obrigatório preenchimento de região e indicador criminal"
    
    filtro=filtro[filtro["Regiao"] == regiao] # ADICIONA OS CAPITULARES
    filtro=filtro[filtro["Natureza"] == indicador]

    if ano:
        filtro=filtro[filtro["Ano"] == int(ano)]

    if data_inicio:
        filtro=filtro[pd.to_datetime(filtro["Data"],format="%d-%m-%Y") >= pd.to_datetime(data_inicio)]

    if data_fim:
        filtro=filtro[pd.to_datetime(filtro["Data"],format="%d-%m-%Y") <= pd.to_datetime(data_fim)]

    if formato=="CSV":
        filtro.to_csv(f"{regiao}_CSV_{ano}_{indicador}.csv",index=False)
        return send_file(f"{regiao}_CSV_{ano}_{indicador}.csv",as_attachment=True)

    if formato=="JSON":
        filtro.to_json(f"{regiao}_JSON_{ano}_{indicador}.json", orient="records",indent=4,force_ascii=False)
        return send_file(f"{regiao}_JSON_{ano}_{indicador}.json", as_attachment=True)
    
    if formato=="Planilha(.xlsx)":
        filtro.to_excel(f"{regiao}_PLANILHA_{ano}_{indicador}.xlsx",index=False)
        return send_file(f"{regiao}_PLANILHA_{ano}_{indicador}.xlsx", as_attachment=True)
    
    if len(filtro)<1:
        return render_template("erro.html")

    return

# FORMULÁRIO CEARÁ
@app.route("/API/CEARA", methods=["POST"])
def API_CEARA():
    # RECEBE PARAMETROS DO FORMULÁRIO DO ESTADO
    ano = request.form.get('ano_ceara')
    indicador = request.form.get('indicador_ceara')
    data_inicio = request.form.get('data_inicio_ceara')
    data_fim = request.form.get('data_fim_ceara')
    formato=request.form.get('formato_ceara')

    filtro=df.copy() # PARA NÃO SOBRESCREVER

    if ano:
        filtro=filtro[filtro["Ano"] == int(ano)]
    
    if indicador:
        filtro=filtro[filtro["Natureza"] == indicador]
    else:
        return "Preenchimento do indicador obrigatório."
    
    if data_inicio:
        filtro=filtro[pd.to_datetime(filtro["Data"],format="%d-%m-%Y") >= pd.to_datetime(data_inicio)]

    if data_fim:
        filtro=filtro[pd.to_datetime(filtro["Data"],format="%d-%m-%Y") <= pd.to_datetime(data_fim)]

    if formato=="CSV":
        filtro.to_csv(f"ceara_csv_{ano}_{indicador}.csv",index=False)
        return send_file(f"ceara_csv_{ano}_{indicador}.csv",as_attachment=True)

    if formato=="JSON":
        filtro.to_json(f"ceara_json_{ano}_{indicador}.json", orient="records",indent=4,force_ascii=False)
        return send_file(f"ceara_json_{ano}_{indicador}.json", as_attachment=True)
    
    if formato=="Planilha(.xlsx)":
        filtro.to_excel(f"ceara_planilha_{ano}_{indicador}.xlsx",index=False)
        return send_file(f"ceara_planilha_{ano}_{indicador}.xlsx", as_attachment=True)
    
    if len(filtro)<1:
        return render_template("erro.html")

    return 

# FORMULÁRIO MUNICIPIO
@app.route("/API/PESQUISA",methods=["POST"])
def PESQUISA():
    # RECEBE PARAMETROS DO FORMULARIO HTML
    ano = request.form.get('ano')
    municipio = request.form.get('municipio')
    indicador = request.form.get('indicador')
    data_inicio = request.form.get('data_inicio')
    data_fim = request.form.get('data_fim')
    formato=request.form.get('formato')

    if not municipio or not indicador or not formato:
        return jsonify({'erro': 'Campos obrigatórios não preenchidos.'})
    
    # CRITÉRIOS DE PESQUISA
    filtro=dados_novos_df().copy() # CRIA UMA CÓPIA PARA EVITAR CONFLITO

    # CONDICIONAIS PARA ACESSAR O CÓDIGO
    
    filtro=filtro[filtro["Município"]==municipio.capitalize()]
    filtro=filtro[filtro["Natureza"]==indicador]

    if ano:
        filtro=filtro[filtro["Ano"]==int(ano)]

    if data_inicio:
        filtro=filtro[pd.to_datetime(filtro["Data"],format="%d-%m-%Y") >= pd.to_datetime(data_inicio)]

    if data_fim:
        filtro=filtro[pd.to_datetime(filtro["Data"],format="%d-%m-%Y") <= pd.to_datetime(data_fim)]

    if len(filtro)<1:
        return render_template("erro.html")

    # BAIXA RESULTADO DE ACORDO COM O FORMATO ESCOLHIDO
        
    if formato=="CSV":
        filtro.to_csv(f"{municipio}_csv_{indicador}.csv",index=False)
        return send_file(f"{municipio}_csv_{indicador}.csv",as_attachment=True)

    if formato=="JSON":
        filtro.to_json(f"{municipio}_json_{indicador}.json", orient="records",indent=4,force_ascii=False)
        return send_file(f"{municipio}_json_{indicador}.json", as_attachment=True)
    
    if formato=="Planilha(.xlsx)":
        filtro.to_excel(f"{municipio}_planilha_{indicador}.xlsx",index=False)
        return send_file(f"{municipio}_planilha_{indicador}.xlsx", as_attachment=True)
    
    return 

################################################## ENDPOINTS PARA REQUISIÇÕES#####################################################################

@app.route("/CEARA",methods=["GET"])
def CEARA():
    # OCORRÊNCIAS POR ESTADO
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
    resultado=df[df["CdRegiao"] == regiao]    
    return resultado.to_json(orient='records',indent=4,force_ascii=False)

if __name__=="__main__":
    app.run(debug=True)