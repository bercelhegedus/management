import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging
from typing import List, Dict, Tuple, Optional, Union
import xlsxwriter
from logger import init_logger

import pdb

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from actions import Action

class Table:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def __repr__(self):
        return self.data.__repr__()

    def slice(self, filter: dict, cols: list = []) -> 'Table':
        filtered_data = self.data.copy()
        for column, values in filter.items():
            filtered_data = filtered_data[filtered_data[column].isin(values)]

        if cols:
            filtered_data = filtered_data.filter(cols)

        return Table(filtered_data)

    def update(self, other: 'Table') -> None:
        self.data = self.data.merge(other.data, left_index=True, right_index=True, how='left', suffixes=('', '_y'))
        self.data.update(other.data)
        self.data.drop([col for col in self.data.columns if col.endswith('_y')], axis=1, inplace=True)


    def rename_columns(self, columns: dict) -> None:
        self.data.rename(columns=columns, inplace=True)
    
    def execute_action(self, action: 'Action') -> 'Table':
        return action.action(self)
    

class Workbook:
    def __init__(self):
        self.tables = {}

    def __repr__(self):
        return "\n".join(f"{table_name}: {table}" for table_name, table in self.tables.items())

    def add_table(self, table_name: str, table: Table):
        if table_name in self.tables:
            print(f"Warning: Overwriting existing table '{table_name}'")
        self.tables[table_name] = table

    def remove_table(self, table_name: str):
        if table_name in self.tables:
            del self.tables[table_name]
        else:
            print(f"Error: Table '{table_name}' not found")

    def get_table(self, table_name: str) -> Table:
        return self.tables.get(table_name, None)

    @staticmethod
    def read_google_sheets_to_workbook(service_account_file: str, tableid: str) -> 'Workbook':
        service = _get_service(service_account_file)
        data_dict = _process_all_tables(service, tableid)
        
        workbook = Workbook()
        for sheet_name, df in data_dict.items():
            table = Table(df)
            workbook.add_table(sheet_name, table)

        return workbook
    

    @staticmethod
    def read_excel_to_workbook(file_path: str) -> 'Workbook':
        workbook = Workbook()
        excel_data = pd.read_excel(file_path, sheet_name=None)
        
        for sheet_name, df in excel_data.items():
            table = Table(df)
            workbook.add_table(sheet_name, table)
           
        return workbook
    

    def write_to_excel(self, file_path: str) -> None:
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            for table_name, table in self.tables.items():
                table.data.to_excel(writer, sheet_name=table_name, index=False)


    def write_to_google_sheets(self, service_account_file: str, file_name: str) -> str:
        # Build credentials with both Sheets and Drive API scopes

        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
        
        # Create Sheets and Drive services using the same credentials
        sheets_service = build('sheets', 'v4', credentials=credentials)
        drive_service = build('drive', 'v3', credentials=credentials)

        # Create a new Google Sheets document
        file_metadata = {
            'name': file_name,
            'mimeType': 'application/vnd.google-apps.spreadsheet',
        }
        file = drive_service.files().create(body=file_metadata).execute()
        spreadsheet_id = file.get('id')

        # Write tables to the Google Sheets document
        for table_name, table in self.tables.items():
            _write_table_to_google_sheets(sheets_service, spreadsheet_id, table_name, table.data)

        return spreadsheet_id



def _write_table_to_google_sheets(service, spreadsheet_id: str, sheet_name: str, data: pd.DataFrame) -> None:
    # Create a new sheet in the Google Sheets document
    sheet_properties = {
        'properties': {
            'title': sheet_name,
        },
    }
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': [{'addSheet': sheet_properties}]}).execute()

    # Replace NaN values with an empty string
    data = data.fillna("")

    # Write data to the new sheet
    data_list = [list(data.columns)] + data.values.tolist()
    body = {
        'values': data_list,
    }
    service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=sheet_name, valueInputOption='RAW', body=body).execute()
    

def _get_service(service_account_file) -> object:
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
    service = build('sheets', 'v4', credentials=credentials)
    return service


def _process_table(service, tableid: str, sheetname: str) -> pd.DataFrame:
    data = service.spreadsheets().values().get(spreadsheetId=tableid, range=sheetname).execute().get('values', [])
    max_cols = max(len(row) for row in data)
    data = [row + [None] * (max_cols - len(row)) for row in data]
    data = pd.DataFrame(data[1:], columns=data[0])
    for col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='ignore')

    return data


def _process_all_tables(service, tableid: str) -> Dict[str, pd.DataFrame]:
    spreadsheet = service.spreadsheets().get(spreadsheetId=tableid).execute()
    sheet_metadata = spreadsheet.get('sheets', [])
    sheet_names = [sheet['properties']['title'] for sheet in sheet_metadata]
    data_dict = {}
    for sheet_name in sheet_names:
        data = _process_table(service, tableid, sheet_name)
        data_dict[sheet_name] = data
    return data_dict



