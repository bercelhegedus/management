import pandas as pd
import pdb
from tables import Table, Workbook
import logging

def read_spreadsheets(data=True, nyomonkovetes=True):
    
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    TORZSSHEET_ID = '1LtCsUPBqGYpnEZXyKFFoaPaeFfe1CLU-O9wiTMGqJUE'
    NYOMONKOVETES = '1yzf9lybroinPysPDB79MpXn1fGG4PyshhpRv1TnYt4U'
    if data:
        data_workbook = Workbook.read_google_sheets_to_workbook(SERVICE_ACCOUNT_FILE, TORZSSHEET_ID, rename_columns_to_ascii=True)
        yield data_workbook
    if nyomonkovetes:    
        nyomonkovetes_workbook = Workbook.read_google_sheets_to_workbook(SERVICE_ACCOUNT_FILE, NYOMONKOVETES, rename_columns_to_ascii=True)
        yield nyomonkovetes_workbook


def cast_to_string(val):
    if pd.isna(val):
        return ''  # or return 'NaN' or any other representation you prefer
    elif isinstance(val, pd.Timestamp):
        return val.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return str(val)

def create_combined_table(data_workbook, nyomonkovetes):

        #drop column ID
        nyomonkovetes.data = nyomonkovetes.data.drop(columns=['ID'])

        #concatenate tables

        res = []
        for kategoria in ['Csotarto', 'Csovezetek', 'Hegesztes', 'Karimaszereles', 'Nyomasproba']:
            table = data_workbook.get_table(kategoria)
            table.data['Kategoria'] = kategoria
            res.append(table.data)

        combined = Table(pd.concat(res, ignore_index=True))

        #merge tables
        merged = combined.join(nyomonkovetes, on=['Izometria','Lap','Kategoria','Sorszam'], how='left')
        
        print(combined.data.head())
        print(nyomonkovetes.data.head())
        print(merged.data.head())

        merged.data['Munkaora'] = merged.data['Munkaora'].round(1)

        # replace NaN with 0 for Elkeszult (m)
        merged.data['Elkeszult (m)'] = merged.data['Elkeszult (m)'].fillna(0)

        return merged.data.applymap(cast_to_string)


def get_employees():
    employee_table_id = '1Jhl9lonUjIFtxq-5-SK1MEwqAtu5gYNdWoX2nClVTxU'
    employee_table = Workbook.read_google_sheets_to_workbook('service_account.json', employee_table_id).get_table('Hegesztok')
    return employee_table.data


def accapted_values(column_name: str):
    if column_name == 'Elkeszitette':
        return get_employees()['Azonosito'].unique().tolist()


def update_tracking(new_records:pd.DataFrame):

    SERVICE_ACCOUNT_FILE = 'service_account.json'
    NYOMONKOVETES = '1yzf9lybroinPysPDB79MpXn1fGG4PyshhpRv1TnYt4U'
    nyomonkovetes_workbook = Workbook()
    nyomonkovetes_workbook.add_table('Nyomonkovetes', Table(new_records))
    print(f'Uploading: \n {new_records}')
    nyomonkovetes_workbook.write_to_google_sheets(SERVICE_ACCOUNT_FILE, spreadsheet_id = NYOMONKOVETES, allow_new_columns=False, append=True)
    logging.info("Nyomonkovetes updated")



if __name__ == '__main__':
    data_workbook, nyomonkovetes_workbook = read_spreadsheets()
    nyomonkovetes = nyomonkovetes_workbook.get_table('Nyomonkovetes')
    table = create_combined_table(data_workbook, nyomonkovetes)
