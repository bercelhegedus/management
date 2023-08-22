from flask import Flask, jsonify, render_template, request, Blueprint
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import pandas as pd
import  numpy as np
from tracking_get_data import create_combined_table, get_employees, update_tracking, read_spreadsheets
import pandas as pd
import random
import string
from tables import Table
import logging

import pdb

tracking_blueprint = Blueprint('tracking_blueprint', __name__)


data_workbook, nyomonkovetes_workbook = read_spreadsheets()
nyomonkovetes = nyomonkovetes_workbook.get_table('Nyomonkovetes')
table = create_combined_table(data_workbook, nyomonkovetes)


column_types = pd.read_csv('tracking_columns.csv', dtype = str)


employees = get_employees()

def filter_employees(employees: Table = employees):
    employees = employees.slice({'Alvallalkozo': current_user.alvallalkozok})
    return employees.data['Azonosito'].unique().tolist()


def extract_column_info(columns ,category, column_types: pd.DataFrame = column_types):

        # Fetching the types for each column
    result = {}
    for column_name in columns:
        
        categoryless = column_types[column_types['category'].isnull()]

        if column_name in categoryless['column'].unique():
            column_type = categoryless[categoryless['column'] == column_name]['type'].iloc[0]
            priority = categoryless[categoryless['column'] == column_name]['priority'].iloc[0]
        elif column_name in column_types[column_types['category'] == category]['column'].unique():
            column_type = column_types[column_types['category'] == category][column_types['column'] == column_name]['type'].iloc[0]
            priority = column_types[column_types['category'] == category][column_types['column'] == column_name]['priority'].iloc[0]
        else:
            column_type = 'exclude'
            priority = 0

        result[column_name] = {'type': column_type, 'priority': priority}

    return result

@tracking_blueprint.route('/get_table', methods=['GET'])
def get_table():
    izometria = request.args.get('izometria', None)
    lap = request.args.get('lap', None)
    kategoria = request.args.get('kategoria', None)
    
    df = table.copy()
    
    df = df.fillna('')

    if izometria:
        df = df[df['Izometria'] == izometria]
    if lap:
        df = df[df['Lap'] == lap]
    if kategoria:
        df = df[df['Kategoria'] == kategoria]

    #get column types
    column_names = df.columns.tolist()
    column_types = extract_column_info(column_names, kategoria)
    column_types = {k: v['type'] for k, v in column_types.items()}


    all_info = df.apply(get_cell_info,args=(column_types,),axis=1)

    return jsonify(all_info.to_dict(orient='records'))

def get_cell_info(row, column_types):
    modified_row = {}
    for cell in row.index:
        if column_types[cell] == 'exclude':
            continue
        elif column_types[cell] == 'static':
            modified_row[cell] = {'value': row[cell], 'type': 'static'}
        elif column_types[cell] == 'categorical':
            modified_row[cell] = {'value': row[cell], 'type': 'categorical'}
            if cell == 'Elkeszitette':
                modified_row[cell]['accepted_values'] = filter_employees(employees)
        elif column_types[cell] == 'date':
            modified_row[cell] = {'value': row[cell], 'type': 'date'}
        elif column_types[cell] == 'number':
            modified_row[cell] = {'value': row[cell], 'type': 'number'}
            if cell == 'Elkeszult (m)':
                modified_row[cell]['min'] = 0
                try:
                    modified_row[cell]['max'] = float(row['Hossz'])
                except:
                    pdb.set_trace()
        else:
            raise ValueError(f'Unknown column type: {column_types[cell]}')
    return pd.Series(modified_row)


@tracking_blueprint.route('/get_unique_values_izometria', methods=['GET'])
def get_unique_values_izometria():
    df = table
    unique_values = df['Izometria'].unique().tolist()
    return jsonify(unique_values)

@tracking_blueprint.route('/get_unique_values_lap', methods=['GET'])
def get_unique_values_lap():
    izometria = request.args.get('izometria', None)
    df = table
    if izometria:
        df = df[df['Izometria'] == izometria]
    unique_values = df['Lap'].unique().tolist()
    return jsonify(unique_values)

@tracking_blueprint.route('/get_unique_values_kategoria', methods=['GET'])
def get_unique_values_kategoria():
    izometria = request.args.get('izometria', None)
    lap = request.args.get('lap', None)
    df = table

    if izometria:
        df = df[df['Izometria'] == izometria]
    if lap:
        df = df[df['Lap'] == lap]
    unique_values = df['Kategoria'].unique().tolist()
    return jsonify(unique_values)

@tracking_blueprint.route('/get_column_priority', methods=['GET'])
def get_column_priority(column_types: pd.DataFrame = column_types):
    column_names = request.args.get('column_names', None)
    category = request.args.get('kategoria', None)


    if not column_names:
        return jsonify({}), 400  # Return a bad request if no column names are provided

    # Splitting the comma-separated column names
    column_names = column_names.split(',')

    # Fetching the priorities for each column
    result = extract_column_info(column_names, category)
    result = {k: int(v['priority']) for k, v in result.items()}

    return jsonify(result)

@tracking_blueprint.route('/save_data', methods=['POST'])
def save_data():
    global table
    data = request.json
    new_df = pd.DataFrame(data)
    new_df.dropna(subset=['Datum'], inplace=True)
    new_df  = new_df[new_df['Datum'] != '']

    new_df['ID'] = new_df['Izometria'].apply(lambda x: ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)))
    new_df['Rogzitette'] = current_user.username
    new_df['Rogzites datuma'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    new_table = Table(new_df)
    table_table = Table(table)
    combined = table_table.join(new_table, how='left', on=['Izometria','Lap','Kategoria','Sorszam'])
    table = combined.data

    logging.info(f'Table updated.')
    update_tracking(new_df)
    return jsonify({"message": "Sikeres mentes!"})


@tracking_blueprint.route('/nyomonkovetes')
@login_required
def index():
    return render_template('tracking_index.html')


