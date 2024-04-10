import pandas as pd
from datetime import datetime, timedelta,timezone
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os,json
from dotenv import load_dotenv, find_dotenv


######### CREDENCIAIS ###############
load_dotenv()
find_dotenv()

ID_SHEET=os.getenv("ID_SHEET")

with open("KEY_SHEET.json", "w") as f:
    f.write(os.environ["KEY_SHEET"])

######################################################################
def salva_data():
    # CREDENCIAIS API SHEETS
    data=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=-3))).strftime("%d-%m-%Y-%Hh%M")
    conta = ServiceAccountCredentials.from_json_keyfile_name("KEY_SHEET.json") # CREDENCIAL
    api = gspread.authorize(conta)
    db = api.open_by_key(ID_SHEET)
    aba_data=db.get_worksheet(1) # SEGUNDA ABA PARA SALVAR SOMENTE A DATA
    aba_data.update_title(f"Data de atualização:{data}") # RENOMEIA PELA DATA DO LOOPING DO CODIGO
    print(f"Nome da aba: {aba_data}")

    # CRIAÇAO DE DATA
    data_raspador=datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=-3))).strftime('%d/%m/%Y às %Hh%M')
    aba_data.update_cell(1,1,data_raspador)

    return aba_data

def obter_data_planilha():
    # CREDENCIAIS API SHEETS
    conta = ServiceAccountCredentials.from_json_keyfile_name("KEY_SHEET.json") # CREDENCIAL
    api = gspread.authorize(conta)
    db = api.open_by_key(ID_SHEET)
    aba_data = db.get_worksheet(1) # SEGUNDA ABA PARA A DATA
    data_raspagem = aba_data.cell(1, 1).value
    return data_raspagem

