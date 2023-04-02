import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import sys
import os
from scipy.interpolate import LinearNDInterpolator, interp1d
import logging
from typing import List, Dict, Tuple, Optional, Union
import pdb
import traceback
from google_sheets import get_service, process_table, upload_table
from populate_inspections import update_inspections
from logger import init_logger

LOG_FILE = 'app.log'
init_logger(LOG_FILE, level=logging.DEBUG)


def interpolate_1d(regressor: pd.Series, target: pd.Series, x: float) -> float:
    # Remove missing values from the regressor and target arrays
    mask = target != ''
    f = interp1d(regressor[mask], target[mask], fill_value='extrapolate')
    return f(x).item()

def interpolate_2d(regressor1: pd.Series, regressor2: pd.Series, target: pd.Series, x1: float, x2: float) -> float:
    # Remove missing values from the regressor1, regressor2, and target arrays
    mask = target != ''
    points = list(zip(regressor1[mask], regressor2[mask]))
    f = LinearNDInterpolator(points, target[mask])
    return f(x1, x2).item()


def process_hegesztes(data: pd.DataFrame, norms: pd.DataFrame) -> pd.DataFrame:
    #interpolate on D and v
    data = data.dropna(subset=['Típus', 'Külső átmérő', 'Falvastagság'])
    data['Külső átmérő'] = data['Külső átmérő'].astype(float)
    data['Falvastagság'] = data['Falvastagság'].astype(float)
    norms['D'] = norms['D'].astype(float)
    norms['v'] = norms['v'].astype(float)
    data['Munkaóra'] = data[['Külső átmérő', 'Falvastagság', 'Típus']].apply(lambda x: interpolate_2d(norms['D'], norms['v'], norms[x[2]], x[0], x[1]), axis=1)
    logger.info(f'Processed {len(data)} rows of hegesztes')
    return data


def process_csotarto(data: pd.DataFrame, norms: pd.DataFrame) -> pd.DataFrame:
    #interpolate on kg-ig
    data['Súly'] = data['Súly'].astype(float)
    data = data.dropna(subset=['Súly', 'Típus'])
    norms['kg-ig'] = norms['kg-ig'].astype(float)
    data['Munkaóra'] = data[['Súly', 'Típus']].apply(lambda x: x[0] * interpolate_1d(norms['kg-ig'], norms[x[1]], x[0]), axis=1)
    logger.info(f'Processed {len(data)} rows of csotarto')
    return data


def process_csovezetek(data: pd.DataFrame, norms: pd.DataFrame) -> pd.DataFrame:
    #interpolate on D and v
    data = data.dropna(subset=['Típus', 'Külső átmérő', 'Falvastagság'])
    data['Külső átmérő'] = data['Külső átmérő'].astype(float)
    data['Falvastagság'] = data['Falvastagság'].astype(float)
    data['Hossz'] = data['Hossz'].astype(float)
    norms['D'] = norms['D'].astype(float)
    norms['v'] = norms['v'].astype(float)
    data['Munkaóra'] = data[['Külső átmérő', 'Falvastagság', 'Típus', 'Hossz']].apply(lambda x: x[3] * interpolate_2d(norms['D'], norms['v'], norms[x[2]], x[0], x[1]), axis=1)
    logger.info(f'Processed {len(data)} rows of csovezetek')
    return data


def process_karimaszerelés(data: pd.DataFrame, norms: pd.DataFrame) -> pd.DataFrame:
    #interpolate on DN
    #drop rows with empty values
    data = data.dropna(subset=['Típus', 'DN'])
    data['DN'] = data['DN'].astype(float)
    data['Nyomásfokozat'] = data['Nyomásfokozat'].astype(float)
    #data['Típus'] = data['Típus'].apply(lambda x: x.upper() if 'pn' in x.lower() else x)
    # # change PN64-140 to PN64-160
    # data.loc[data['Típus'] == 'PN64-140', 'Típus'] = 'PN64-160'
    # # change PN14-40 to PN10-40
    # data.loc[data['Típus'] == 'PN14-40', 'Típus'] = 'PN10-40'
    norms = norms[norms['DN'] != '']
    norms = norms.astype(float)

    norms['Összeépített vakperem - PN10-40'] = norms['Összeépített vakperem'] + norms['PN10-40']
    norms['Összeépített vakperem - PN64-160'] = norms['Összeépített vakperem'] + norms['PN64-160']
    norms['Összeépített vakperem - PN250-320'] = norms['Összeépített vakperem'] + norms['PN250-320']

    data.loc[(data['Típus'] == 'Összeépített vakperem') & (data['Nyomásfokozat'] <= 40), 'Típus'] = 'Összeépített vakperem - PN10-40'
    data.loc[(data['Típus'] == 'Összeépített vakperem') & (data['Nyomásfokozat'] > 40) & (data['Nyomásfokozat'] <= 160), 'Típus'] = 'Összeépített vakperem - PN64-160'
    data.loc[(data['Típus'] == 'Összeépített vakperem') & (data['Nyomásfokozat'] > 160), 'Típus'] = 'Összeépített vakperem - PN250-320'

    data['Munkaóra'] = data[['DN','Típus']].apply(lambda x: interpolate_1d(norms['DN'], norms[x[1]], x[0]), axis=1)
    logger.info(f'Processed {len(data)} rows of karimaszerelés')
    return data

def process_nyomasproba(data: pd.DataFrame, norms: pd.DataFrame) -> pd.DataFrame:
    data['Külső átmérő'] = data['Külső átmérő'].astype(float)
    data['Hossz'] = data['Hossz'].astype(float)
    data = data.dropna(subset=['Külső átmérő', 'Típus'])
    norms['D'] = norms['D'].astype(float)
    data['Munkaóra'] = data[['Külső átmérő', 'Típus', 'Hossz']].apply(lambda x: x[2] * interpolate_1d(norms['D'], norms[x[1]], x[0]), axis=1)
    logger.info(f'Processed {len(data)} rows of nyomasproba')
    return data



def process_sheets(service_account_file: str, torzssheet_id: str, normasheet_id: str,update_blanks = False, ids_to_update: List[str] = [], sheets: List[str] = ['Csotarto', 'Hegesztes', 'Csovezetek', 'Karimaszereles', 'Nyomasproba']) -> None:

    service = get_service(service_account_file)

    if 'Csovezetek' in sheets and 'Nyomasproba' not in sheets:
        sheets.append('Nyomasproba')

    for sheet in sheets:

        logger.debug(f'Processing {sheet}')

        data = process_table(service, torzssheet_id, sheet)

        norms = process_table(service, normasheet_id, sheet)

        logger.debug(f'{sheet} data loaded')

        if not update_blanks:
            ids_to_update = ids_to_update + data[data['Munkaóra'].isna()]['ID'].tolist()

        if ids_to_update:
            original_data = data.copy()
            data = data[data['ID'].isin(ids_to_update)]

        if data.empty:
            continue

        if sheet == 'Csotarto':
            data = process_csotarto(data, norms)
        elif sheet == 'Hegesztes':
            data = process_hegesztes(data, norms)
        elif sheet == 'Csovezetek':
            update_inspections(csovezetek_ids_to_update=data['ID'].tolist())
            data = process_csovezetek(data, norms)
        elif sheet == 'Karimaszereles':
            data = process_karimaszerelés(data, norms)
        elif sheet == 'Nyomasproba':
            data = process_nyomasproba(data, norms)
        else:
            raise ValueError('Invalid sheet name')

        if ids_to_update:
            for _, row in data.iterrows():
                row_id = row['ID']
                row_index = original_data.index[original_data['ID'] == row_id].tolist()[0]
                original_data.loc[row_index] = row
            data = original_data

        upload_table(service, torzssheet_id, sheet, data)


def main():
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    TORZSSHEET_ID = '1LtCsUPBqGYpnEZXyKFFoaPaeFfe1CLU-O9wiTMGqJUE'
    NORMASHEET_ID = '1Cd1PIhYJUQJd8Dr7XfcL31nd_ukNjAL-yqYGTFOVBh4'

    process_sheets(SERVICE_ACCOUNT_FILE, TORZSSHEET_ID, NORMASHEET_ID)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    except:
        traceback.print_exc()
        pdb.post_mortem()
