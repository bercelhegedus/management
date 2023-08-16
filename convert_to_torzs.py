import os
import pandas as pd
import numpy as np
import random
import string
import pdb
import zipfile


#cycle though .xlsx files in zip_ref

def concatonate_excels(dir_path):



    sheets_dict = {}

    izometrialaps = pd.DataFrame()
    #files from dir_path and subdirs
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if not file.endswith('.xlsx'):
                continue

            #read in file
            xl_file = pd.read_excel(os.path.join(root,file), sheet_name=None)

            #rename sheets

            #Csőtartó to Csotarto
            if 'Csőtartó' in xl_file:
                xl_file['Csotarto'] = xl_file.pop('Csőtartó')
            
            #hegesztes to Hegesztes
            if 'hegesztes' in xl_file:
                xl_file['Hegesztes'] = xl_file.pop('hegesztes')

            #csovezetek to Csovezetek
            if 'csovezetek' in xl_file:
                xl_file['Csovezetek'] = xl_file.pop('csovezetek')
            
            #Varrat to Hegesztes
            if 'Varrat' in xl_file:
                xl_file['Hegesztes'] = xl_file.pop('Varrat')

            #Karima to Karimaszereles
            if 'Karima' in xl_file:
                xl_file['Karimaszereles'] = xl_file.pop('Karima')
            
            #Cső to Csovezetek
            if 'Cső' in xl_file:
                xl_file['Csovezetek'] = xl_file.pop('Cső')
            
            osszegzes = xl_file['Osszegzes'].transpose().reset_index()
            osszegzes.columns = osszegzes.iloc[0]
            osszegzes = osszegzes.iloc[1:]
            osszegzes['IzometrialapID'] = osszegzes['Izometria'].apply(lambda x: ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)))

            if not izometrialaps.empty:
                izometrialaps = pd.concat([izometrialaps, osszegzes])
            else:
                izometrialaps = osszegzes 

            # concatenate the sheets into a single dataframe for each sheet
            for sheet_name, sheet_df in xl_file.items():
                if sheet_name == 'Osszegzes':
                    continue
                    
                #replace ' ' with NaN
                sheet_df.replace(' ', np.nan, inplace=True)
                sheet_df.replace('', np.nan, inplace=True)

                #drop rows where any value is NaN
                sheet_df.dropna(how='any', inplace=True)

                #get filename without extension
                sheet_df['Lap'] = osszegzes['Lap'].values[0]

                sheet_df['Izometria'] = osszegzes['Izometria'].values[0]

                sheet_df['IzometrialapID'] = osszegzes['IzometrialapID'].values[0]

                sheet_df['ID'] = sheet_df['Izometria'].apply(lambda x: ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)))

                sheet_df['Típus'] = sheet_df['Típus'].apply(lambda x: x.capitalize() if isinstance(x, str) else x)

                #capitalize all columns
                #sheet_df.columns = sheet_df.columns.str.capitalize()
                
                if sheet_name == 'Csovezetek':
                    if 'hosszúság' in sheet_df.columns:
                        sheet_df.rename(columns={'hosszúság': 'Hossz'}, inplace=True)


                if sheet_name == 'Hegesztes':
                    sheet_df['Típus'] = sheet_df['Típus'].apply(lambda x: 'Csőbeültetés' if x == 'Beültetés' else x)
                    sheet_df['Típus'] = sheet_df['Típus'].apply(lambda x: 'Csőbeültetés' if x == 'Csobeültetes' else x)
                    sheet_df['Típus'] = sheet_df['Típus'].apply(lambda x: 'Weldolet, nipli' if x == 'Weldolet nipli' else x)

                if sheet_name == 'Karimaszereles':
                    sheet_df['Típus'] = sheet_df['Típus'].apply(lambda x: x.upper() if "PN" in x.upper() else x)

                if sheet_name in sheets_dict:
                    sheets_dict[sheet_name] = pd.concat([sheets_dict[sheet_name], sheet_df])
                else:
                    sheets_dict[sheet_name] = sheet_df




    #order each sheet by Izometria, Lap, Sorszam
    for sheet_name, sheet_df in sheets_dict.items():
        sheet_df.sort_values(by=['Izometria', 'Lap', 'Sorszám'], inplace=True)
    
    #order izometrialaps by Izometria, Lap

    izometrialaps.sort_values(by=['Izometria', 'Lap'], inplace=True)

    return sheets_dict, izometrialaps
            

def aggregate_izometria(izometrialaps):
    
    #get the number of rows for each Izometria, store it in Lapok Szama

    izometrialaps['Lapok száma'] = izometrialaps.groupby(['Izometria'])['Lap'].transform('count')

    # join all unique Alvallalkozo values for each Izometria

    izometrialaps.groupby(['Izometria'])['Alvállalkozó'].transform(lambda x: ', '.join(map(str, x.unique())))

    # get izometria table

    izometria = izometrialaps[['Izometria', 'Lapok száma', 'Alvállalkozó']].drop_duplicates()

    return izometria


def create_nyomasproba(csovezetek):

    # create a rwo for each ro in csovezetek where Szilárdsági nyomáspróba == 1

    szilardsagi_nyomasproba = csovezetek[csovezetek['Szilárdsági nyomáspróba'] == 1][['ID','IzometrialapID','Izometria','Lap','Külső átmérő','Hossz','Falvastagság']]
    szilardsagi_nyomasproba['Típus'] = 'Szilárdsági nyomáspróba'

    # Tömörségi nyomáspróba == 1

    tomorsagi_nyomasproba = csovezetek[csovezetek['Tömörségi nyomáspróba'] == 1][['ID','IzometrialapID','Izometria','Lap','Külső átmérő','Hossz','Falvastagság']]
    tomorsagi_nyomasproba['Típus'] = 'Tömörségi nyomáspróba'

    nyomasproba = pd.concat([szilardsagi_nyomasproba, tomorsagi_nyomasproba])

    nyomasproba.rename(columns={'ID': 'CsovezetekID'}, inplace=True)

    nyomasproba['Sorszám'] = szilardsagi_nyomasproba.groupby(['Izometria', 'Lap']).cumcount().reset_index(drop=True) + 1

    nyomasproba['ID'] = nyomasproba['Izometria'].apply(lambda x: ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)))

    return nyomasproba



def main():

    dir_path = r'C:\Users\berce\programming\Tiszaujvaros'
    sheet_dict, izometrialaps = concatonate_excels(dir_path)

    izometria = aggregate_izometria(izometrialaps)

    nyomasproba = create_nyomasproba(sheet_dict['Csovezetek'])

    sheet_dict['Izometrialap'] = izometrialaps
    sheet_dict['Izometria'] = izometria
    sheet_dict['Nyomasproba'] = nyomasproba

    #write to excel
    with pd.ExcelWriter('output.xlsx') as writer:
        for sheet_name, sheet_df in sheet_dict.items():
            sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
    

if __name__ == '__main__':
    try:
        main()
    except:
        import traceback
        traceback.print_exc()
        pdb.post_mortem()


