import pandas as pd
from google_sheets import get_service, process_table, upload_table, process_all_tables, df_dict_to_excel
from typing import List, Dict, Tuple, Optional, Union
import pdb
import os
import sys
import traceback


def main():
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    TORZSSHEET_ID = '1LtCsUPBqGYpnEZXyKFFoaPaeFfe1CLU-O9wiTMGqJUE'
    service = get_service(SERVICE_ACCOUNT_FILE)
    sheet_dict = process_all_tables(service, TORZSSHEET_ID)
    sheet_dict = enrich_all(sheet_dict)
    df_dict_to_excel(sheet_dict, 'torzs.xlsx')


def calculate_hours(base_df: pd.DataFrame, new_column_name: pd.DataFrame, target_df: pd.DataFrame, groupby_column: str, target_column: str) -> pd.Series:
    hours = target_df.groupby(groupby_column)[target_column].apply(lambda x: pd.to_numeric(x, errors='coerce').sum()).reset_index().rename(columns={target_column: new_column_name})
    base_df = base_df.merge(hours, on=groupby_column, how='left')
    base_df.fillna(0, inplace=True)
    return base_df


def enrich_izometrialap(sheet_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    izometrialap = sheet_dict['Izometrialap']
    izometrialap = calculate_hours(izometrialap, 'Csotarto orak' ,sheet_dict['Csotarto'], 'IzometrialapID', 'Munkaóra')
    izometrialap = calculate_hours(izometrialap, 'Hegesztes orak' ,sheet_dict['Hegesztes'], 'IzometrialapID', 'Munkaóra')
    izometrialap = calculate_hours(izometrialap, 'Csovezetek orak' ,sheet_dict['Csovezetek'], 'IzometrialapID', 'Munkaóra')
    izometrialap = calculate_hours(izometrialap, 'Karimaszereles orak' ,sheet_dict['Karimaszereles'], 'IzometrialapID', 'Munkaóra')
    izometrialap = calculate_hours(izometrialap, 'Nyomasproba orak' ,sheet_dict['Nyomasproba'], 'IzometrialapID', 'Munkaóra')
    izometrialap['Munkaorak'] = izometrialap['Csotarto orak'] + izometrialap['Hegesztes orak'] + izometrialap['Csovezetek orak'] + izometrialap['Karimaszereles orak'] + izometrialap['Nyomasproba orak']
    izometrialap['Hegesztes %'] = izometrialap['Hegesztes orak'] / izometrialap['Munkaorak']
    izometrialap['Csotarto %'] = izometrialap['Csotarto orak'] / izometrialap['Munkaorak']
    izometrialap['Csovezetek %'] = izometrialap['Csovezetek orak'] / izometrialap['Munkaorak']
    izometrialap['Karimaszereles %'] = izometrialap['Karimaszereles orak'] / izometrialap['Munkaorak']
    izometrialap['Nyomasproba %'] = izometrialap['Nyomasproba orak'] / izometrialap['Munkaorak']
    sheet_dict['Izometrialap'] = izometrialap
    return sheet_dict


def enrich_izometria(sheet_dict:  Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    izometria = sheet_dict['Izometria']

    izometria = calculate_hours(izometria, 'Csotarto orak' ,sheet_dict['Csotarto'], 'Izometria', 'Munkaóra')
    izometria = calculate_hours(izometria, 'Hegesztes orak' ,sheet_dict['Hegesztes'], 'Izometria', 'Munkaóra')
    izometria = calculate_hours(izometria, 'Csovezetek orak' ,sheet_dict['Csovezetek'], 'Izometria', 'Munkaóra')
    izometria = calculate_hours(izometria, 'Karimaszereles orak' ,sheet_dict['Karimaszereles'], 'Izometria', 'Munkaóra')
    izometria = calculate_hours(izometria, 'Nyomasproba orak' ,sheet_dict['Nyomasproba'], 'Izometria', 'Munkaóra')
    izometria['Munkaorak'] = izometria['Csotarto orak'] + izometria['Hegesztes orak'] + izometria['Csovezetek orak'] + izometria['Karimaszereles orak'] + izometria['Nyomasproba orak']
    izometria['Hegesztes %'] = izometria['Hegesztes orak'] / izometria['Munkaorak']
    izometria['Csotarto %'] = izometria['Csotarto orak'] / izometria['Munkaorak']
    izometria['Csovezetek %'] = izometria['Csovezetek orak'] / izometria['Munkaorak']
    izometria['Karimaszereles %'] = izometria['Karimaszereles orak'] / izometria['Munkaorak']
    izometria['Nyomasproba %'] = izometria['Nyomasproba orak'] / izometria['Munkaorak']
    sheet_dict['Izometria'] = izometria
    return sheet_dict


def enrich_vallalkozok(sheet_dict:  Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    vallalkozok = sheet_dict['Alvállalkozók']
    vallalkozok = calculate_hours(vallalkozok, 'Csotarto orak' ,sheet_dict['Izometrialap'], 'Alvállalkozó', 'Csotarto orak')
    vallalkozok = calculate_hours(vallalkozok, 'Hegesztes orak' ,sheet_dict['Izometrialap'], 'Alvállalkozó', 'Hegesztes orak')
    vallalkozok = calculate_hours(vallalkozok, 'Csovezetek orak' ,sheet_dict['Izometrialap'], 'Alvállalkozó', 'Csovezetek orak')
    vallalkozok = calculate_hours(vallalkozok, 'Karimaszereles orak' ,sheet_dict['Izometrialap'], 'Alvállalkozó', 'Karimaszereles orak')
    vallalkozok = calculate_hours(vallalkozok, 'Nyomasproba orak' ,sheet_dict['Izometrialap'], 'Alvállalkozó', 'Nyomasproba orak')
    vallalkozok['Munkaorak'] = vallalkozok['Csotarto orak'] + vallalkozok['Hegesztes orak'] + vallalkozok['Csovezetek orak'] + vallalkozok['Karimaszereles orak'] + vallalkozok['Nyomasproba orak']
    vallalkozok['Hegesztes %'] = vallalkozok['Hegesztes orak'] / vallalkozok['Munkaorak']
    vallalkozok['Csotarto %'] = vallalkozok['Csotarto orak'] / vallalkozok['Munkaorak']
    vallalkozok['Csovezetek %'] = vallalkozok['Csovezetek orak'] / vallalkozok['Munkaorak']
    vallalkozok['Karimaszereles %'] = vallalkozok['Karimaszereles orak'] / vallalkozok['Munkaorak']
    vallalkozok['Nyomasproba %'] = vallalkozok['Nyomasproba orak'] / vallalkozok['Munkaorak']
    sheet_dict['Alvállalkozók'] = vallalkozok
    return sheet_dict


def enrich_all(sheet_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    sheet_dict = enrich_izometrialap(sheet_dict)
    sheet_dict = enrich_izometria(sheet_dict)
    sheet_dict = enrich_vallalkozok(sheet_dict)
    return sheet_dict


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
