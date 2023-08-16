from flask import Flask, jsonify, render_template, request, Blueprint
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import pandas as pd
import  numpy as np
from dataentry_get_data import create_combined_table, get_employees
import pandas as pd

import pdb

dataentry_blueprint = Blueprint('dataentry_dataentry_blueprint', __name__)

table = create_combined_table()

column_types = pd.read_csv('dataentry_columns.csv', dtype = str)


def accapted_values(column_name: str):
    if column_name == 'Elkeszitette':
        return get_employees()['Azonosito'].unique().tolist()

@dataentry_blueprint.route('/get_table', methods=['GET'])
def get_table():
    izometria = request.args.get('izometria', None)
    lap = request.args.get('lap', None)
    kategoria = request.args.get('kategoria', None)

    df = table

    if izometria:
        df = df[df['Izometria'] == izometria]
    if lap:
        df = df[df['Lap'] == lap]
    if kategoria:
        df = df[df['Kategoria'] == kategoria]

    return jsonify(df.to_dict(orient='records'))

@dataentry_blueprint.route('/get_unique_values_izometria', methods=['GET'])
def get_unique_values_izometria():
    df = table
    unique_values = df['Izometria'].unique().tolist()
    return jsonify(unique_values)

@dataentry_blueprint.route('/get_unique_values_lap', methods=['GET'])
def get_unique_values_lap():
    izometria = request.args.get('izometria', None)
    df = table
    if izometria:
        df = df[df['Izometria'] == izometria]
    unique_values = df['Lap'].unique().tolist()
    return jsonify(unique_values)

@dataentry_blueprint.route('/get_unique_values_kategoria', methods=['GET'])
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

@dataentry_blueprint.route('/get_column_types', methods=['GET'])
def get_column_types(column_types: pd.DataFrame = column_types):
    column_names = request.args.get('column_names', None)
    category = request.args.get('kategoria', None)


    if not column_names:
        return jsonify({}), 400  # Return a bad request if no column names are provided

    # Splitting the comma-separated column names
    column_names = column_names.split(',')

    # Fetching the types for each column
    result = {}
    for column_name in column_names:
        
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

        if column_type == 'exclude':
            result[column_name] = {'type': column_type}
        elif column_type == 'categorical':
            result[column_name] = {'type': column_type, 'values': accapted_values(column_name), 'priority': priority}
        else:
            result[column_name] = {'type': column_type, 'priority': priority}
    return jsonify(result)

@dataentry_blueprint.route('/save_data', methods=['POST'])
def save_data():
    data = request.json
    new_df = pd.DataFrame(data)
    # Do whatever you want with the new_df
    print(new_df)
    return jsonify({"message": "Data saved successfully!"})


@dataentry_blueprint.route('/nyomonkovetes')
@login_required
def index():
    return render_template('dataentry_index.html')


