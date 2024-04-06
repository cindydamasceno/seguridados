import pandas as pd
from bs4 import BeautifulSoup as bs
import gspread, requests, os
from datetime import datetime,timedelta,timezone
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from dotenv import load_dotenv,find_dotenv

######### CREDENCIAIS ###############
load_dotenv()
find_dotenv()
URL_PLANILHA=os.getenv("URL_PLANILHA")
ID_SHEET=os.getenv("ID_SHEET")

with open("KEY_SHEET.json", "w") as f:
    f.write(os.environ["KEY_SHEET"])
####################################

# INICIA A RASPAGEM NO SITE DA SSPDS-CE

def raspagem():
    ano = datetime.now().strftime("%Y") # PEGA DATA DO ANO CORRENTE.
    tentativas=0

    # RASPADOR NO SITE DA SSPDS
    while tentativas < 4:
        try:
            print(f"Tentativa: {tentativas+1}")
            soup = bs(requests.get(f"https://www.sspds.ce.gov.br/html/estatisticas-{ano}/").content,"html.parser").find_all("ul", {"class": 'ListaEst col3 -Laranja'})[2]
            link=soup.find("a",{"class":"box"})["href"]
            print(f"Dados acessados com sucesso na tentativa {tentativas+1}. Iniciando padronização")

            break
        except Exception as e:
            if tentativas == 3:
                print(f"Número máximo de tentativas atingido em {datetime.now()}. Tente novamente mais tarde.")
    return link

# PADRONIZAÇÃO DA BASE DE DADOS

def padroniza ():
    link=raspagem()
    df=pd.read_excel(link)
    mun=pd.read_csv(URL_PLANILHA)
    
    # ADIÇÃO DE REGIÕES DE PLANEJAMENTO (FONTE: IPECE), CÓDIGO IBGE, CÓDIGO DOS INDICADORES

    dic_regiao={
                "Cariri": 1,
                "Centro Sul": 2,
                "Grande Fortaleza": 3,
                "Litoral Leste": 4,
                "Litoral Norte": 5,
                "Litoral Oeste / Vale do Curu": 6,
                "Maciço de Baturité": 7,
                "Serra da Ibiapaba": 8,
                "Sertão Central": 9,
                "Sertão de Canindé": 10,
                "Sertão de Sobral": 11,
                "Sertão dos Crateús": 12,
                "Sertão dos Inhamuns": 13,
                "Vale do Jaguaribe": 14
            }

    dic_indicador={
        "FEMINICÍDIO": 1,
        "HOMICIDIO DOLOSO": 2,
        "LESAO CORPORAL SEGUIDA DE MORTE": 3,
        "ROUBO SEGUIDO DE MORTE (LATROCINIO)": 4,
            }

    dic_mun={}
    for index,linha in mun.iterrows():
        municipio=linha["mun"]
        cd=linha["cdibge"]
        regiao=linha["regiao"]

        if municipio not in dic_mun:
            dic_mun[municipio]={"cd": cd, "regiao": regiao}

    df["Ano"]=df["Data"].dt.strftime("%Y")
    df["CdIbge"]=df["Município"].apply(lambda municipio : dic_mun[municipio].get("cd"))
    df["Regiao"]=df["Município"].apply(lambda municipio : dic_mun[municipio].get("regiao"))
    df["CdRegiao"]=df["Regiao"].apply(lambda regiao : dic_regiao[regiao])
    df["CdIndicador"]=df["Natureza"].apply(lambda indicador : dic_indicador[indicador])
    df["Data"]=df["Data"].dt.strftime("%d-%m-%Y")
    df['Hora'] = df["Hora"].astype(str).str[:5] # pega os primeiros digitos da hora e ignora os segundos
    df=df[['Ano', 'Regiao',"CdRegiao", 'CdIbge' ,'Município', 'AIS', 'Natureza',"CdIndicador", 'Data', 'Hora', 'Dia da Semana',
       'Meio Empregado', 'Gênero', 'Idade da Vítima', 'Escolaridade da Vítima',
       'Raça da Vítima']]
    
    return df

    # ATUALIZAÇÃO DA BASE DE DADOS COM AS NOVAS INFORMAÇÕES
def formata_planilha():
    
    data=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=-3))).strftime("%d-%m-%Y-%Hh%M")
    # CREDENCIAIS
    conta = ServiceAccountCredentials.from_json_keyfile_name("KEY_SHEET.json")
    api = gspread.authorize(conta)
    db = api.open_by_key(ID_SHEET)
    aba=db.sheet1 # aba com dados
    aba.update_title(data) # renomeia pela data de looping do código
    return aba
        
def cruza_planilha():
    aba=formata_planilha()
    df=padroniza()
    # TRANSFORMA EM DATAFRAME PARA COMPARAÇÃO ENTRE LISTAS
    consulta = get_as_dataframe(aba)

    # CRIA LISTA COM VALORES NOVOS E ANTIGOS

    antigo = []
    novo = []
    
    for index, linha in consulta.iterrows(): 
        tupla_linha = tuple(linha) # CADA LINHA LIDA COMO TUPLA PARA TRAVAR A FORMATAÇÃO
        antigo.append(tupla_linha)
    
    for index, linha in df.iterrows():
        lista_linha = linha.tolist()
        novo.append(lista_linha)
    return antigo, novo

def atualiza_seguridados ():
    data=datetime.now().strftime("%d-%m-%Y-%Hh%M")
    antigo,novo=cruza_planilha()
    aba=formata_planilha()
    conferencia = [linha for linha in novo if tuple(linha) not in antigo] # ENVIA SOMENTE DADOS NOVOS 

    # Adiciona em lote à planilha
    aba.append_rows(conferencia)
    return f"Planilha atualizada em: {data}"

def dados_novos_df():
    aba=formata_planilha()
    df = get_as_dataframe(aba)
    return df