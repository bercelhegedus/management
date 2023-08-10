import pandas as pd
from actions import *
from tables import *
import logging
import os
import sys

import pdb
import traceback


def read_spreadsheets():
    
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    TORZSSHEET_ID = '1LtCsUPBqGYpnEZXyKFFoaPaeFfe1CLU-O9wiTMGqJUE'
    NYOMONKOVETES = '1yzf9lybroinPysPDB79MpXn1fGG4PyshhpRv1TnYt4U'

    data_workbook = Workbook.read_google_sheets_to_workbook(SERVICE_ACCOUNT_FILE, TORZSSHEET_ID)
    nyomonkovetes_workbook = Workbook.read_google_sheets_to_workbook(SERVICE_ACCOUNT_FILE, NYOMONKOVETES)

    return data_workbook, nyomonkovetes_workbook


def aggregate(data_workbook):

    aggregate_csotarto = aggregate_csotarto(data_workbook)


import pandas as pd
import numpy as np

def join_first_n(table1: pd.DataFrame, table2: pd.DataFrame, on: list, count_column: str) -> pd.DataFrame:
    # Sort the dataframes
    table1 = table1.sort_values(by=on)
    table2 = table2.sort_values(by=on)

    table2['Datum'] = pd.to_datetime(table2['Datum'])  # Ensure the date column is in datetime format

    # Create the helper column in the first dataframe
    table1['helper'] = table1.groupby(on).cumcount()

    # "Explode" the second dataframe
    table2_exploded = pd.DataFrame(np.repeat(table2.values, table2[count_column], axis=0), columns=table2.columns)
    table2_exploded[count_column] = table2_exploded[count_column].astype(int)  # Ensure count_column is int

    # Create the helper column in the exploded dataframe
    table2_exploded['helper'] = table2_exploded.groupby(on + ['Datum']).cumcount()

    idx = table2_exploded.groupby('helper')['Datum'].idxmin()  # Get the index of the max date for each group
    table2_exploded = table2_exploded.loc[idx]

    table2_exploded['Lap'] = table2_exploded['Lap'].astype(int)

    # Perform the join operation
    result = table1.merge(table2_exploded, how='left', on=on + ['helper'])

    result = result.drop(columns=['helper','Elkeszult (db)'])

    return result


def aggregate_csotarto(data_workbook, nyomonkovetes_workbook):

    csotarto = data_workbook.get_table('Csotarto')
    
    nyomonkovetes = nyomonkovetes_workbook.get_table('Nyomonkovetes')
    csotarto_nyomonkovetes = nyomonkovetes.slice({'Kategoria': ['Csőtartó']})

    count = Table(csotarto.data.groupby(['Izometria', 'Lap']).size().reset_index().rename(columns={0:'count'}))


    csotarto_nyomonkovetes = csotarto_nyomonkovetes.join(count, on=['Izometria', 'Lap'], how='left')
    
    #set Elkeszult (db) to count where Teljes elkeszultseg = TRUE

    csotarto_nyomonkovetes.data.loc[csotarto_nyomonkovetes.data['Teljes elkeszultseg'] == 'TRUE', 'Elkeszult (db)'] = csotarto_nyomonkovetes.data['count']

    #csotarto_nyomonkovetes.data = csotarto_nyomonkovetes.data.loc[csotarto_nyomonkovetes.data.index.repeat(csotarto_nyomonkovetes.data['Elkeszult (db)'])].reset_index(drop=True)
    
    csotarto_nyomonkovetes.data = join_first_n(csotarto.data, csotarto_nyomonkovetes.data[['Izometria', 'Lap', 'Datum', 'Elkeszult (db)']], on=['Izometria', 'Lap'], count_column='Elkeszult (db)')

    

    # Add Elkeszult % and Elkeszult munkaora where Datum

    csotarto_nyomonkovetes.data.loc[csotarto_nyomonkovetes.data['Datum'].notna(), 'Elkeszult %'] = 100

    csotarto_nyomonkovetes.data.loc[csotarto_nyomonkovetes.data['Datum'].notna(), 'Elkeszult munkaora'] = csotarto_nyomonkovetes.data['Munkaora']

    # Set Elkeszult % and Elkeszult munkaora to 0 where Datum is NAN

    csotarto_nyomonkovetes.data.loc[csotarto_nyomonkovetes.data['Datum'].isna(), 'Elkeszult %'] = 0

    csotarto_nyomonkovetes.data.loc[csotarto_nyomonkovetes.data['Datum'].isna(), 'Elkeszult munkaora'] = 0

    #Datum to datetime

    csotarto_nyomonkovetes.data['Datum'] = pd.to_datetime(csotarto_nyomonkovetes.data['Datum'])

    return csotarto_nyomonkovetes

def aggregate_hegesztes(data_workbook, nyomonkovetes_workbook):

    hegesztes = data_workbook.get_table('Hegesztes')

    nyomonkovetes = nyomonkovetes_workbook.get_table('Nyomonkovetes')
    hegesztes_nyomonkovetes = nyomonkovetes.slice({'Kategoria': ['Hegesztés']})

    hegesztes_nyomonkovetes.data = hegesztes_nyomonkovetes.data.astype({'Sorszam': int})

    #merge on Izometria, Lap, and Sorszam, add columns Datum and Elkeszitette

    hegesztes_nyomonkovetes = hegesztes.join(hegesztes_nyomonkovetes, on=['Izometria', 'Lap', 'Sorszam'], how='left', columns=['Datum', 'Elkeszitette'])

    # Add Elkeszult % and Elkeszult munkaora where Datum

    hegesztes_nyomonkovetes.data.loc[hegesztes_nyomonkovetes.data['Datum'].notna(), 'Elkeszult %'] = 100

    hegesztes_nyomonkovetes.data.loc[hegesztes_nyomonkovetes.data['Datum'].notna(), 'Elkeszult munkaora'] = hegesztes_nyomonkovetes.data['Munkaora']
 
    # Add Elkeszult % and Elkeszult munkaora where Datum

    hegesztes_nyomonkovetes.data.loc[hegesztes_nyomonkovetes.data['Datum'].notna(), 'Elkeszult %'] = 100

    hegesztes_nyomonkovetes.data.loc[hegesztes_nyomonkovetes.data['Datum'].notna(), 'Elkeszult munkaora'] = hegesztes_nyomonkovetes.data['Munkaora']

    # Set Elkeszult % and Elkeszult munkaora to 0 where Datum is NAN

    hegesztes_nyomonkovetes.data.loc[hegesztes_nyomonkovetes.data['Datum'].isna(), 'Elkeszult %'] = 0

    hegesztes_nyomonkovetes.data.loc[hegesztes_nyomonkovetes.data['Datum'].isna(), 'Elkeszult munkaora'] = 0

    #Datum to datetime

    hegesztes_nyomonkovetes.data['Datum'] = pd.to_datetime(hegesztes_nyomonkovetes.data['Datum'])

    return hegesztes_nyomonkovetes

#same as hegesztes just for Karimaszereles

def aggregate_karimaszereles(data_workbook, nyomonkovetes_workbook):

    karimaszereles = data_workbook.get_table('Karimaszereles')

    nyomonkovetes = nyomonkovetes_workbook.get_table('Nyomonkovetes')
    karimaszereles_nyomonkovetes = nyomonkovetes.slice({'Kategoria': ['Karimaszerelés']})
    
    #merge on Izometria, Lap, and Sorszam, add columns Datum and Elkeszitette

    karimaszereles_nyomonkovetes = karimaszereles.join(karimaszereles_nyomonkovetes, on=['Izometria', 'Lap', 'Sorszam'], how='left', columns=['Datum', 'Elkeszitette'])

    # Add Elkeszult % and Elkeszult munkaora where Datum

    karimaszereles_nyomonkovetes.data.loc[karimaszereles_nyomonkovetes.data['Datum'].notna(), 'Elkeszult %'] = 100

    karimaszereles_nyomonkovetes.data.loc[karimaszereles_nyomonkovetes.data['Datum'].notna(), 'Elkeszult munkaora'] = karimaszereles_nyomonkovetes.data['Munkaora']

    # Set Elkeszult % and Elkeszult munkaora to 0 where Datum is NAN

    karimaszereles_nyomonkovetes.data.loc[karimaszereles_nyomonkovetes.data['Datum'].isna(), 'Elkeszult %'] = 0

    karimaszereles_nyomonkovetes.data.loc[karimaszereles_nyomonkovetes.data['Datum'].isna(), 'Elkeszult munkaora'] = 0

    #Datum to datetime
    
    karimaszereles_nyomonkovetes.data['Datum'] = pd.to_datetime(karimaszereles_nyomonkovetes.data['Datum'])

    return karimaszereles_nyomonkovetes

def aggregate_csovezetek(data_workbook, nyomonkovetes_workbook):

    csovezetek = data_workbook.get_table('Csovezetek')

    csovezetek.data = csovezetek.data.groupby(['Izometria', 'Lap']).agg({'IzometrialapID': 'first', 'Hossz': 'sum', 'Munkaora': 'sum'}).reset_index()

    nyomonkovetes = nyomonkovetes_workbook.get_table('Nyomonkovetes')
    csovezetek_nyomonkovetes = nyomonkovetes.slice({'Kategoria': ['Csővezeték']})

    csovezetek_nyomonkovetes = csovezetek_nyomonkovetes.join(csovezetek, on=['Izometria', 'Lap'], how='left', columns=['Hossz'])

    # update elkeszult (m) to with hossz where Teljes elkeszultseg = TRUE

    csovezetek_nyomonkovetes.data.loc[csovezetek_nyomonkovetes.data['Teljes elkeszultseg'] == 'TRUE', 'Elkeszult (m)'] = csovezetek_nyomonkovetes.data['Hossz']

    # drop where Elkeszult (m) NAN

    csovezetek_nyomonkovetes.data = csovezetek_nyomonkovetes.data[csovezetek_nyomonkovetes.data['Elkeszult (m)'].notna()]

    

    #Add dummy first row for each Izometria, Lap pair with Elkeszult (m) = 0 Datum = 2020-01-01

    csovezetek_nyomonkovetes.data = csovezetek_nyomonkovetes.data.groupby(['Izometria', 'Lap']).apply(
    lambda x: pd.concat(
        [
            x, 
            pd.DataFrame(
                [{
                    'Datum': '01/01/2020', 
                    'Elkeszult (m)': 0, 
                    'Izometria': x.name[0], 
                    'Lap': x.name[1]
                }])], ignore_index=True)).reset_index(drop=True)
    
    csovezetek_nyomonkovetes.data.sort_values(['Datum', 'Elkeszult (m)'], ascending=[True, True], inplace=True)
    
    csovezetek_nyomonkovetes.data['Elkeszult'] = csovezetek_nyomonkovetes.data.groupby(['Izometria', 'Lap'], group_keys=False)['Elkeszult (m)'].apply(lambda x: x.diff())

    #Drop dummies
    csovezetek_nyomonkovetes.data = csovezetek_nyomonkovetes.data[csovezetek_nyomonkovetes.data['Datum'] != '01/01/2020']

    csovezetek_nyomonkovetes = csovezetek.join(csovezetek_nyomonkovetes, on=['Izometria', 'Lap'], how='left', columns=['Datum', 'Elkeszult'])

    csovezetek_nyomonkovetes.data['Elkeszult %'] = (csovezetek_nyomonkovetes.data['Elkeszult'] / csovezetek_nyomonkovetes.data['Hossz']) * 100

    csovezetek_nyomonkovetes.data['Elkeszult munkaora'] = (csovezetek_nyomonkovetes.data['Elkeszult %'] * csovezetek_nyomonkovetes.data['Munkaora']) / 100

    # Set Elkeszult % and Elkeszult munkaora to 0 where Datum is NAN

    csovezetek_nyomonkovetes.data.loc[csovezetek_nyomonkovetes.data['Datum'].isna(), 'Elkeszult %'] = 0

    csovezetek_nyomonkovetes.data.loc[csovezetek_nyomonkovetes.data['Datum'].isna(), 'Elkeszult munkaora'] = 0

    csovezetek_nyomonkovetes.data['Datum'] = pd.to_datetime(csovezetek_nyomonkovetes.data['Datum'])

    return csovezetek_nyomonkovetes

def aggregate_nyomasproba(data_workbook, nyomonkovetes_workbook):

    nyomasproba = data_workbook.get_table('Nyomasproba')

    nyomonkovetes = nyomonkovetes_workbook.get_table('Nyomonkovetes')
    nyomasproba_nyomonkovetes = nyomonkovetes.slice({'Kategoria': ['Nyomáspróba']})

    nyomasproba_nyomonkovetes = nyomasproba.join(nyomasproba_nyomonkovetes, on=['Izometria', 'Lap'], how='left', columns=['Datum'])

    # Add Elkeszult % and Elkeszult munkaora where Datum

    nyomasproba_nyomonkovetes.data.loc[nyomasproba_nyomonkovetes.data['Datum'].notna(), 'Elkeszult %'] = 100

    nyomasproba_nyomonkovetes.data.loc[nyomasproba_nyomonkovetes.data['Datum'].notna(), 'Elkeszult munkaora'] = nyomasproba_nyomonkovetes.data['Munkaora']

    # Set Elkeszult % and Elkeszult munkaora to 0 where Datum is NAN

    nyomasproba_nyomonkovetes.data.loc[nyomasproba_nyomonkovetes.data['Datum'].isna(), 'Elkeszult %'] = 0

    nyomasproba_nyomonkovetes.data.loc[nyomasproba_nyomonkovetes.data['Datum'].isna(), 'Elkeszult munkaora'] = 0

    #Datum to datetime

    nyomasproba_nyomonkovetes.data['Datum'] = pd.to_datetime(nyomasproba_nyomonkovetes.data['Datum'])

    return nyomasproba_nyomonkovetes





    

def join_nyomonkovetes(data_workbook, nyomonkovetes_workbook):

    elorehaladas = Workbook()

    csotarto_nyomonkovetes = aggregate_csotarto(data_workbook, nyomonkovetes_workbook)
    elorehaladas.add_table('Csotarto', csotarto_nyomonkovetes)

    hegesztes_nyomonkovetes = aggregate_hegesztes(data_workbook, nyomonkovetes_workbook)
    elorehaladas.add_table('Hegesztes', hegesztes_nyomonkovetes)

    karimaszereles_nyomonkovetes = aggregate_karimaszereles(data_workbook, nyomonkovetes_workbook)
    elorehaladas.add_table('Karimaszereles', karimaszereles_nyomonkovetes)

    csovezetek_nyomonkovetes = aggregate_csovezetek(data_workbook, nyomonkovetes_workbook)
    elorehaladas.add_table('Csovezetek', csovezetek_nyomonkovetes)

    nyomasproba_nyomonkovetes = aggregate_nyomasproba(data_workbook, nyomonkovetes_workbook)
    elorehaladas.add_table('Nyomasproba', nyomasproba_nyomonkovetes)

    return elorehaladas


def lap_level_aggregate(data_workbook, result):
    
    izometrialaps = data_workbook.get_table('Izometrialap')

    izometrialaps.data['Osszes munkaora'] = 0
    izometrialaps.data['Osszes elkeszult munkaora'] = 0

    for table_name, table in result.tables.items():

        grouped = Table(table.data.groupby(['IzometrialapID']).agg({'Datum': 'last', 'Munkaora': 'sum', 'Elkeszult munkaora': 'sum'}).reset_index())

        #rename columns to include table name

        grouped.rename_columns({'Munkaora': f'{table_name} munkaora', 'Elkeszult munkaora': f'{table_name} elkeszult munkaora', 'Datum': f'{table_name} datum'}, inplace=True)

        #join to izometrialaps
        izometrialaps = izometrialaps.join(grouped, on=['IzometrialapID'], how='left')

        #add to Osszes munkaora and Osszes elkeszult munkaora
        izometrialaps.data['Osszes munkaora'] = izometrialaps.data['Osszes munkaora'] + izometrialaps.data[f'{table_name} munkaora']
        izometrialaps.data['Osszes elkeszult munkaora'] = izometrialaps.data['Osszes elkeszult munkaora'] + izometrialaps.data[f'{table_name} elkeszult munkaora']



    result.add_table('Izometrialapok' ,izometrialaps)

    return result

def izometria_level_aggregate(data_workbook, result):

    izometria = data_workbook.get_table('Izometria')

    izometrialaps = result.get_table('Izometrialapok')

    grouped_laps = izometrialaps.data.groupby(['Izometria']).agg({'Osszes munkaora': 'sum', 'Osszes elkeszult munkaora': 'sum'}).reset_index()

    izometria = izometria.join(Table(grouped_laps), on=['Izometria'], how='left')

    
    result.add_table('Izometriak' ,izometria)

    return result

def export_excel():

    data_workbook, nyomonkovetes_workbook = read_spreadsheets()


    elorehaladas = join_nyomonkovetes(data_workbook, nyomonkovetes_workbook)

    result = Workbook()

    for table_name, table in elorehaladas.tables.items():
        table.data = table.data.sort_values(by=['Datum', 'Elkeszult %'])
        result.add_table(table_name, Table(table.data.groupby('IzometrialapID').last()))

    result = lap_level_aggregate(data_workbook, result)

    result = izometria_level_aggregate(data_workbook, result)

    result.write_to_excel('elorehaladas.xlsx')

    
def main():
    export_excel()

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