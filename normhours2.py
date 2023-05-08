import pandas as pd
from actions import *
from tables import *
import logging

import pdb
import traceback

LOG_FILE = 'app.log'
#logging = init_logging(LOG_FILE, level=logging.DEBUG)


def process_all(data_workbook, norms_workbook):


    logging.info("Processing csotarto...")
    csotarto = process_csotarto(data_workbook.get_table('Csotarto'), norms_workbook.get_table('Csotarto'))
    data_workbook.add_table('Csotarto', csotarto)

    logging.info("Processing hegesztes...")
    hegesztes = process_hegesztes(data_workbook.get_table('Hegesztes'), norms_workbook.get_table('Hegesztes'))
    data_workbook.add_table('Hegesztes', hegesztes)

    logging.info("Processing csovezetek...")
    csovezetek = process_csovezetek(data_workbook.get_table('Csovezetek'), norms_workbook.get_table('Csovezetek'))
    data_workbook.add_table('Csovezetek', csovezetek)

    logging.info("Processing karimaszerelés...")
    karimaszereles = process_karimaszerelés(data_workbook.get_table('Karimaszereles'), norms_workbook.get_table('Karimaszereles'))
    data_workbook.add_table('Karimaszereles', karimaszereles)

    logging.info("Processing nyomasproba...")
    nyomasproba = process_nyomasproba(data_workbook.get_table('Nyomasproba'), norms_workbook.get_table('Nyomasproba'))
    data_workbook.add_table('Nyomasproba', nyomasproba)

    return data_workbook
    

def process_excel(input, output):
    logging.info(f"Reading input from {input}...")
    data_workbook = Workbook.read_excel_to_workbook(input)
    
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    NORMASHEET_ID = '1Cd1PIhYJUQJd8Dr7XfcL31nd_ukNjAL-yqYGTFOVBh4'

    norms_workbook = Workbook.read_google_sheets_to_workbook(SERVICE_ACCOUNT_FILE, NORMASHEET_ID)

    process_all(data_workbook, norms_workbook)

    logging.info(f"Writing output to {output}...")
    data_workbook.write_to_excel(output)
    

def process_spreadsheet():
    
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    TORZSSHEET_ID = '1LtCsUPBqGYpnEZXyKFFoaPaeFfe1CLU-O9wiTMGqJUE'
    NORMASHEET_ID = '1Cd1PIhYJUQJd8Dr7XfcL31nd_ukNjAL-yqYGTFOVBh4'

    data_workbook = Workbook.read_google_sheets_to_workbook(SERVICE_ACCOUNT_FILE, TORZSSHEET_ID)
    norms_workbook = Workbook.read_google_sheets_to_workbook(SERVICE_ACCOUNT_FILE, NORMASHEET_ID)

    process_all(data_workbook, norms_workbook)

    logging.info(f"Writing output to {TORZSSHEET_ID}...")
    data_workbook.write_to_google_sheets(SERVICE_ACCOUNT_FILE, TORZSSHEET_ID)




def process_hegesztes(data: Table, norms: Table) -> Table:
    norms.rename_columns({'D': 'Külső átmérő', 'v': 'Falvastagság'})
    action = Interpolate2DAction(regressor_cols=['Külső átmérő', 'Falvastagság'], norms=norms, data_interpolated_col='Munkaóra', data_type_col='Típus')
    data = action.action(data)
    return data

def process_csotarto(data: Table, norms: Table) -> Table:
    norms.rename_columns({'kg-ig': 'Súly'})
    action = Interpolate1DAction(regressor_col='Súly', norms=norms, data_interpolated_col='Munkaóra', data_type_col='Típus')
    data = action.action(data)
    data.data['Munkaóra'] = data.data['Munkaóra'] * data.data['Súly']
    return data

def process_csovezetek(data: Table, norms: Table) -> Table:
    norms.rename_columns({'D': 'Külső átmérő', 'v': 'Falvastagság'})
    action = Interpolate2DAction(regressor_cols=['Külső átmérő', 'Falvastagság'], norms=norms, data_interpolated_col='Munkaóra', data_type_col='Típus')
    data = action.action(data)
    data.data['Munkaóra'] = data.data['Munkaóra'] * data.data['Hossz']
    return data

def process_karimaszerelés(data: Table, norms: Table) -> Table:
    norms.rename_columns({'DN': 'DN'})
    
    

    norms.data['Összeépített vakperem - PN10-40'] = pd.to_numeric(norms.data['Összeépített vakperem'], errors='coerce') + pd.to_numeric(norms.data['PN10-40'], errors='coerce')
    norms.data['Összeépített vakperem - PN64-160'] = pd.to_numeric(norms.data['Összeépített vakperem'], errors='coerce') + pd.to_numeric(norms.data['PN64-160'], errors='coerce')
    norms.data['Összeépített vakperem - PN250-320'] = pd.to_numeric(norms.data['Összeépített vakperem'], errors='coerce') + pd.to_numeric(norms.data['PN250-320'], errors='coerce')

    
    data.data.loc[(data.data['Típus'] == 'Összeépített vakperem') & (data.data['Nyomásfokozat'] <= 40), 'Típus'] = 'Összeépített vakperem - PN10-40'
    data.data.loc[(data.data['Típus'] == 'Összeépített vakperem') & (data.data['Nyomásfokozat'] > 40) & (data.data['Nyomásfokozat'] <= 160), 'Típus'] = 'Összeépített vakperem - PN64-160'
    data.data.loc[(data.data['Típus'] == 'Összeépített vakperem') & (data.data['Nyomásfokozat'] > 160), 'Típus'] = 'Összeépített vakperem - PN250-320'
    
    action = Interpolate1DAction(regressor_col='DN', norms=norms, data_interpolated_col='Munkaóra', data_type_col='Típus')
    data = action.action(data)
    return data


def process_nyomasproba(data: Table, norms: Table) -> Table:
    norms.rename_columns({'D': 'Külső átmérő'})
    action = Interpolate1DAction(regressor_col='Külső átmérő', norms=norms, data_interpolated_col='Munkaóra', data_type_col='Típus')
    data = action.action(data)
    data.data['Munkaóra'] = data.data['Munkaóra'] * data.data['Hossz']
    return data


if __name__ == '__main__':
    try:
        process_excel('torzs.xlsx', 'torzs_out.xlsx')
    except:
        traceback.print_exc()
        pdb.post_mortem()

