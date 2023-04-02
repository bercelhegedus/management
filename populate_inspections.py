import pandas as pd
import random
import os
import sys
import string
from google_sheets import get_service, process_table, upload_table
import traceback
import pdb    
import logging
from logger import init_logger

LOG_FILE = 'app.log'
init_logger(LOG_FILE, level=logging.DEBUG)

def update_inspections(csovezetek_ids_to_update=[], force_update=False):
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    TORZSSHEET_ID = '1LtCsUPBqGYpnEZXyKFFoaPaeFfe1CLU-O9wiTMGqJUE'

    service = get_service(SERVICE_ACCOUNT_FILE)

    csovezetek = process_table(service, TORZSSHEET_ID, 'Csovezetek')

    if csovezetek_ids_to_update:
        csovezetek = csovezetek[csovezetek['ID'].isin(csovezetek_ids_to_update)]

    nyomasproba = process_table(service, TORZSSHEET_ID, 'Nyomasproba')

    if force_update:
        nyomasproba = nyomasproba.drop(index=nyomasproba.index)

    cso_cols=['ID', 'Sorszám', 'CsovezetekID', 'IzometrialapID', 'Izometria', 'Lap', 'Külső átmérő', 'Típus', 'Hossz']
    new_rows = pd.DataFrame(columns=cso_cols)
    for _, row in csovezetek.iterrows():
        logger.debug(f"Processing nyomasproba row: {row['ID']}")
        nyomasproba_max = nyomasproba.loc[nyomasproba['IzometrialapID']==row['IzometrialapID'],'Sorszám'].max()
        if pd.isna(nyomasproba_max):
            nyomasproba_max = 0
        new_rows_max = new_rows.loc[new_rows['IzometrialapID']==row['IzometrialapID'],'Sorszám'].max()
        if pd.isna(new_rows_max):
            new_rows_max = 0
        sorszam = max(nyomasproba_max, new_rows_max) + 1
        for probe_type in ['Szilárdsági nyomáspróba', 'Tömörségi nyomáspróba']:
            if row[probe_type] == '1':
                row_temp = row.copy()
                row_temp = row_temp.rename({'ID': 'CsovezetekID'})
                row_temp['Típus'] = probe_type
                row_temp['Sorszám'] = sorszam
                sorszam += 1

                if not ((nyomasproba['CsovezetekID'] == row_temp['CsovezetekID']) & (nyomasproba['Típus'] == row_temp['Típus'])).any():
                    row_temp['ID'] = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                    new_rows = pd.concat([new_rows,row_temp[cso_cols].to_frame().T])



    nyomasproba = pd.concat([nyomasproba, new_rows], ignore_index=True)

    valid_ids = csovezetek['ID'].unique()
    nyomasproba = nyomasproba[nyomasproba['CsovezetekID'].isin(valid_ids)]

    # Find rows to delete
    rows_to_delete = []
    for _, row in nyomasproba.iterrows():
        cso_row = csovezetek[csovezetek['ID'] == row['CsovezetekID']].iloc[0]
        if cso_row['Szilárdsági nyomáspróba'] != '1' and cso_row['Tömörségi nyomáspróba'] != '1':
            rows_to_delete.append(row.name)

    # Delete rows
    nyomasproba = nyomasproba.drop(rows_to_delete)

    upload_table(service, TORZSSHEET_ID, 'Nyomasproba', nyomasproba)




if __name__ == '__main__':
    try:
        update_inspections(force_update=True)
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except:
        traceback.print_exc()
        pdb.post_mortem()
