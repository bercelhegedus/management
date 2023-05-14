import pandas as pd
from actions import *
from tables import *
import logging

import pdb
import traceback

LOG_FILE = 'app.log'
#logging = init_logging(LOG_FILE, level=logging.DEBUG)

logging.basicConfig(level=logging.DEBUG)


def apply_magassag_modifier(data: Table, magassag_modifier: Table, izometria: Table = None) -> Table:
    
    drop_column = False
    if not 'Magassag' in data.data.columns:
        drop_column = True
        if not izometria:
            return data 
        if not 'Magassag' in izometria.data.columns:
            return data
        
        data.data = pd.merge(data.data, izometria.data[['IzometrialapID','Magassag']], on='IzometrialapID', how='left')
    magassag_modifier.rename_columns({'Magassagtol': 'Magassag'})
    nearest_lower_multiplier_action = NearestLowerMultiplierAction(magassag_modifier,'Magassag', 'Szorzo', 'Munkaóra')
    data = nearest_lower_multiplier_action.action(data)

    if drop_column:
        data.data = data.data.drop(columns=['Magassag'])

    return data


def process_all(data_workbook, norms_workbook, mod_workbook):

    if 'Csotarto' in data_workbook.tables.keys():
        logging.info("Processing csotarto...")
        csotarto = process_csotarto(data_workbook.get_table('Csotarto'), norms_workbook.get_table('Csotarto'))
        csotarto = apply_magassag_modifier(csotarto, mod_workbook.get_table('Magassag'), izometria=data_workbook.get_table('Izometria'))
        data_workbook.add_table('Csotarto', csotarto)

    if 'Hegesztes' in data_workbook.tables.keys():
        logging.info("Processing hegesztes...")
        hegesztes = process_hegesztes(data_workbook.get_table('Hegesztes'), norms_workbook.get_table('Hegesztes'), mod_workbook.get_table('Anyag'), izometria=data_workbook.get_table('Izometria'))
        hegesztes = apply_magassag_modifier(hegesztes, mod_workbook.get_table('Magassag'), izometria=data_workbook.get_table('Izometria'))
        data_workbook.add_table('Hegesztes', hegesztes)

    if 'Csovezetek' in data_workbook.tables.keys():
        logging.info("Processing csovezetek...")
        csovezetek = process_csovezetek(data_workbook.get_table('Csovezetek'), norms_workbook.get_table('Csovezetek'))
        csovezetek = apply_magassag_modifier(csovezetek, mod_workbook.get_table('Magassag'), izometria=data_workbook.get_table('Izometria'))
        data_workbook.add_table('Csovezetek', csovezetek)

    if 'Karimaszereles' in data_workbook.tables.keys():
        logging.info("Processing karimaszerelés...")
        karimaszereles = process_karimaszerelés(data_workbook.get_table('Karimaszereles'), norms_workbook.get_table('Karimaszereles'))
        karimaszereles = apply_magassag_modifier(karimaszereles, mod_workbook.get_table('Magassag'), izometria=data_workbook.get_table('Izometria'))
        data_workbook.add_table('Karimaszereles', karimaszereles)

    if 'Nyomasproba' in data_workbook.tables.keys():
        logging.info("Processing nyomasproba...")
        nyomasproba = process_nyomasproba(data_workbook.get_table('Nyomasproba'), norms_workbook.get_table('Nyomasproba'))
        nyomasproba = apply_magassag_modifier(nyomasproba, mod_workbook.get_table('Magassag'), izometria=data_workbook.get_table('Izometria'))
        data_workbook.add_table('Nyomasproba', nyomasproba)

    return data_workbook
    

def process_excel(input, output):
    logging.info(f"Reading input from {input}...")
    data_workbook = Workbook.read_excel_to_workbook(input)
    
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    NORMASHEET_ID = '1Cd1PIhYJUQJd8Dr7XfcL31nd_ukNjAL-yqYGTFOVBh4'
    MODIFIER_ID = '1IYJj1j9i0c_8W4PR_tVr7sf98cp9mznpCpSp-0ITbnI'

    norms_workbook = Workbook.read_google_sheets_to_workbook(SERVICE_ACCOUNT_FILE, NORMASHEET_ID)
    modifier_workbook = Workbook.read_google_sheets_to_workbook(SERVICE_ACCOUNT_FILE, MODIFIER_ID)

    process_all(data_workbook, norms_workbook, modifier_workbook)

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




def process_hegesztes(data: Table, norms: Table,anyag_modifier: Table, izometria: Table=None) -> Table:

    norms.rename_columns({'D': 'Külső átmérő', 'v': 'Falvastagság'})
    action = Interpolate2DAction(regressor_cols=['Külső átmérő', 'Falvastagság'], norms=norms, data_interpolated_col='Munkaóra', data_type_col='Típus')
    data = action.action(data)
    
    drop_col = False
    if not 'Anyagminoseg' in data.data.columns:
        drop_col = True
        if not izometria:
            return data 
        if not 'Anyagminoseg' in izometria.data.columns:
            return data
        
        data = pd.merge(data, izometria[['IzometrialapID']], on='IzometrialapID', how='left')

    multiplier_action = MultiplierAction(anyag_modifier, 'Anyagminoseg', 'Szorzo', 'Munkaóra')
    data = multiplier_action.action(data)

    if drop_col:
        data.data = data.data.drop(columns=['Anyagminoseg'])

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
    
    
    if 'Nyomásfokozat' in data.data.columns:
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
        process_excel('base.xlsx', 'out.xlsx')
        #process_spreadsheet()
        pass
    except:
        traceback.print_exc()
        pdb.post_mortem()

