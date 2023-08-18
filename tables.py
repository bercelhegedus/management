import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging
from typing import List, Dict, Tuple, Optional, Union
import xlsxwriter
from logger import init_logger
from unidecode import unidecode
from pandas.api.types import is_numeric_dtype, is_datetime64_any_dtype
from copy import deepcopy

import pdb

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from actions import Action

class Table:
    def __init__(self, data: pd.DataFrame, rename_columns_to_ascii: bool = False):
        self.data = data
        if rename_columns_to_ascii:
            self.rename_columns_to_ascii()
        

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

    def rename_columns(self, columns: dict, inplace: bool = False) -> None:
        if inplace:
            self.data.rename(columns=columns, inplace=inplace)
        else:
            data = self.data.rename(columns=columns, inplace=inplace)
            return Table(data)

    def rename_columns_to_ascii(self):
        self.data.columns = [unidecode(col) for col in self.data.columns]
    
    def execute_action(self, action: 'Action') -> 'Table':
        return action.action(self)
    
    def join(self, other: 'Table', how: str = 'inner', on: list = None, inplace: bool = False, columns: List = []) -> 'Table':
        if how not in ['inner', 'outer', 'left']:
            raise ValueError("Invalid join type. Expected one of: 'inner', 'outer', 'left'")

        if columns:
            other = deepcopy(other)
            other.data = other.data[on + columns]

        # Cast columns in other to match the datatypes of self
        if on is not None:
            for col in on:
                # Check for numeric and datetime types, as they need special handling
                if is_numeric_dtype(self.data[col]):
                    other.data[col] = pd.to_numeric(other.data[col], errors='coerce')
                elif is_datetime64_any_dtype(self.data[col]):
                    other.data[col] = pd.to_datetime(other.data[col], errors='coerce')
                else:
                    other.data[col] = other.data[col].astype(self.data[col].dtype)

            # Use suffixes to differentiate columns from the two DataFrames
            result = self.data.merge(other.data, on=on, how=how, suffixes=('', '_y'))
        else:
            result = self.data.merge(other.data, left_index=True, right_index=True, how=how, suffixes=('', '_y'))

        # Drop columns from 'self' that have a counterpart in 'other'
        to_drop = [col for col in result if col.endswith('_y')]
        for col in to_drop:
            original_col_name = col.rstrip('_y')
            result.drop(columns=[original_col_name], inplace=True)
            result.rename(columns={col: original_col_name}, inplace=True)

        if inplace:
            self.data = result
            return self
        else:
            return Table(result)


class Workbook:
    def __init__(self):
        self.tables = {}

    def __repr__(self):
        return "\n".join(f"{table_name}: {table}" for table_name, table in self.tables.items())

    def add_table(self, table_name: str, table: Table):
        if not isinstance(table, Table):
            raise ValueError(f"'table' must be of type 'Table', got '{type(table).__name__}' instead.")
        if table_name in self.tables:
            print(f"Warning: Overwriting existing table '{table_name}'")
        self.tables[table_name] = table

    def remove_table(self, table_name: str):
        if table_name in self.tables:
            del self.tables[table_name]
        else:
            print(f"Error: Table '{table_name}' not found")

    def get_table(self, table_name: str) -> Table:
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found")
        return self.tables.get(table_name, None)

    @staticmethod
    def read_google_sheets_to_workbook(service_account_file: str, tableid: str, rename_columns_to_ascii: bool = False) -> 'Workbook':
        service = _get_service(service_account_file)
        data_dict = _process_all_tables(service, tableid)
        
        workbook = Workbook()
        for sheet_name, df in data_dict.items():
            table = Table(df, rename_columns_to_ascii=rename_columns_to_ascii)
            workbook.add_table(sheet_name, table)

        return workbook
    

    @staticmethod
    def read_excel_to_workbook(file_path: str, rename_columns_to_ascii: bool = False) -> 'Workbook':
        workbook = Workbook()
        excel_data = pd.read_excel(file_path, sheet_name=None)
        
        for sheet_name, df in excel_data.items():
            table = Table(df, rename_columns_to_ascii=rename_columns_to_ascii)
            workbook.add_table(sheet_name, table)
           
        return workbook
    

    def write_to_excel(self, file_path: str) -> None:
        with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
            for table_name, table in self.tables.items():
                table.data.to_excel(writer, sheet_name=table_name, index=False)


    def write_to_google_sheets(self, service_account_file: str, file_name: str = None, spreadsheet_id: str = None, allow_new_columns: bool = True, append: bool = False) -> str:

        if not file_name:
            if not spreadsheet_id:
                raise ValueError('Either filename or ID needed')

        # Build credentials with both Sheets and Drive API scopes
        scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)
        
        # Create Sheets and Drive services using the same credentials
        sheets_service = build('sheets', 'v4', credentials=credentials)
        drive_service = build('drive', 'v3', credentials=credentials)

        # If no spreadsheet_id is provided, create a new Google Sheets document
        if not spreadsheet_id:
            file_metadata = {
                'name': file_name,
                'mimeType': 'application/vnd.google-apps.spreadsheet',
            }
            file = drive_service.files().create(body=file_metadata).execute()
            spreadsheet_id = file.get('id')

        # Write tables to the Google Sheets document
        for table_name, table in self.tables.items():
            _write_table_to_google_sheets(sheets_service, spreadsheet_id, table_name, table.data, allow_new_columns=allow_new_columns, append=append)

        return spreadsheet_id



def _write_table_to_google_sheets(service, spreadsheet_id: str, sheet_name: str, data: pd.DataFrame, 
                                  allow_new_columns: bool = True, append: bool = False) -> None:
    # Check if sheet with the given name already exists
    sheets_data = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    existing_sheets = [sheet['properties']['title'] for sheet in sheets_data['sheets']]
    
    # If the sheet doesn't exist, create it
    if sheet_name not in existing_sheets:
        sheet_properties = {
            'properties': {
                'title': sheet_name,
            },
        }
        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={'requests': [{'addSheet': sheet_properties}]}).execute()
        append = False  # If it's a new sheet, there's nothing to append to
    else:
        # Retrieve existing columns from the sheet
        existing_data = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}!1:1").execute()
        existing_columns = existing_data.get('values', [])[0] if 'values' in existing_data else []
        
        # If not allowing new columns, filter the dataframe to only include existing columns
        if not allow_new_columns:
            for col in existing_columns:
                if col not in data.columns:
                    data[col] = ""
            data = data[existing_columns]

        # When appending, ensure all existing columns are present in the data
        if append:
            for col in existing_columns:
                if col not in data.columns:
                    data[col] = ""

    # Replace NaN values with an empty string
    data = data.fillna("")

    # Write data to the sheet
    if append:
        # Exclude headers if appending
        data_list = data.values.tolist()
    else:
        # Include headers if not appending (i.e., overwriting or creating new sheet)
        data_list = [list(data.columns)] + data.values.tolist()

    
    # If appending, determine the starting row
    if append:
        last_row_data = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=f"{sheet_name}").execute()
        last_row = len(last_row_data.get('values', []))
        range_name = f"{sheet_name}!A{last_row + 1}"  # +1 to append after the last row
    else:
        range_name = f"{sheet_name}!A1"
    
    body = {
        'values': data_list,
    }
    service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name, valueInputOption='RAW', body=body).execute()


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



