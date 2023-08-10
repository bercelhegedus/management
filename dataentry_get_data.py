import pandas as pd
import pdb
from progress_report import read_spreadsheets
from tables import Table, Workbook

def cast_to_string(val):
    if pd.isna(val):
        return ''  # or return 'NaN' or any other representation you prefer
    elif isinstance(val, pd.Timestamp):
        return val.strftime('%Y-%m-%d %H:%M:%S')
    else:
        return str(val)

def create_combined_table():
        
        data_workbook, nyomonkovetes_workbook = read_spreadsheets()

        print('Spreadsheets read')

        nyomonkovetes = nyomonkovetes_workbook.get_table('Nyomonkovetes')

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

        # round munka ora to 1 decimal
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


if __name__ == '__main__':
    print(get_column_type())