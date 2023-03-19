import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging

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


def upload_table(service, tableid: str, sheetname: str, data: pd.DataFrame):
    data = data.fillna('')
    data_list = data.T.reset_index().values.T.tolist()
    service.spreadsheets().values().update(spreadsheetId=tableid, range=sheetname, valueInputOption='USER_ENTERED', body={'values': data_list}).execute()
    logging.info(f'Uploaded {sheetname} to {tableid}')
