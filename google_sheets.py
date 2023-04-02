import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging
from typing import List, Dict, Tuple, Optional, Union
import xlsxwriter
from logger import init_logger

LOG_FILE = 'app.log'
logger = init_logger(LOG_FILE, level=logging.DEBUG)

def get_service(service_account_file) -> object:
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
    service = build('sheets', 'v4', credentials=credentials)
    return service


def process_table(service, tableid: str, sheetname: str) -> pd.DataFrame:
    data = service.spreadsheets().values().get(spreadsheetId=tableid, range=sheetname).execute().get('values', [])
    max_cols = max(len(row) for row in data)
    data = [row + [None] * (max_cols - len(row)) for row in data]
    data = pd.DataFrame(data[1:], columns=data[0])
    return data


def process_all_tables(service, tableid: str) -> Dict[str, pd.DataFrame]:
    spreadsheet = service.spreadsheets().get(spreadsheetId=tableid).execute()
    sheet_metadata = spreadsheet.get('sheets', [])
    sheet_names = [sheet['properties']['title'] for sheet in sheet_metadata]
    data_dict = {}
    for sheet_name in sheet_names:
        data = service.spreadsheets().values().get(spreadsheetId=tableid, range=sheet_name).execute().get('values', [])
        max_cols = max(len(row) for row in data)
        data = [row + [None] * (max_cols - len(row)) for row in data]
        data = pd.DataFrame(data[1:], columns=data[0])
        data_dict[sheet_name] = data
    return data_dict


def upload_table(service, tableid: str, sheetname: str, data: pd.DataFrame):
    data = data.fillna('')
    data_list = data.T.reset_index().values.T.tolist()
    service.spreadsheets().values().update(spreadsheetId=tableid, range=sheetname, valueInputOption='USER_ENTERED', body={'values': data_list}).execute()
    logger.info(f'Uploaded {sheetname} to {tableid}')


def df_dict_to_excel(df_by_sheet: Dict[str, pd.DataFrame], filename: str):
    writer = pd.ExcelWriter(filename, engine='xlsxwriter', engine_kwargs={'options': {'strings_to_numbers': True}})
    for sheet_name, df in df_by_sheet.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    writer.save()

