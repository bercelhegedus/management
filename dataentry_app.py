from flask import Flask, jsonify, render_template, request
import pandas as pd
import  numpy as np

app = Flask(__name__)

def your_function():
    data = {
        'A': ['foo', 'bar', 'foo', 'bar', 'foo', 'bar', 'foo', 'foo', 'bar', 'foo',
            'bar', 'foo', 'foo', 'bar', 'foo', 'bar', 'foo', 'bar', 'foo', 'bar'],
        'B': ['one', 'two', 'three', 'four', 'five', 'one', 'two', 'three', 'four', 'five',
            'one', 'two', 'three', 'four', 'five', 'one', 'two', 'three', 'four', 'five'],
        'C': ['small', 'large', 'medium', 'small', 'large', 'medium', 'small', 'large', 'medium', 'small',
            'large', 'medium', 'small', 'large', 'medium', 'small', 'large', 'medium', 'small', 'large'],
        'D': [1, 2, 2, 3, 3, 4, 5, 6, 2, 3, 4, 5, 7, 8, 9, 10, 12, 15, 16, 20],
        'E': [2, 4, 5, 5, 6, 6, 8, 9, 7, 8, 10, 11, 13, 14, 18, 20, 22, 24, 26, 30]
    }

    df = pd.DataFrame(data)

    # Define the categories for the new column 'F'
    categories = ['cat1', 'cat2', 'cat3', 'cat4', 'cat5']

    # Add new categorical column 'F'
    df['F'] = np.random.choice(categories, df.shape[0])

    return df

@app.route('/get_table', methods=['GET'])
def get_table():
    value_a = request.args.get('value_a', None)
    value_b = request.args.get('value_b', None)
    value_c = request.args.get('value_c', None)
    
    df = your_function()
    
    if value_a:
        df = df[df['A'] == value_a]
    if value_b:
        df = df[df['B'] == value_b]
    if value_c:
        df = df[df['C'] == value_c]
        
    return jsonify(df.to_dict(orient='records'))

@app.route('/get_unique_values_a', methods=['GET'])
def get_unique_values():
    df = your_function()
    unique_values = df['A'].unique().tolist()
    print(unique_values)
    return jsonify(unique_values)

@app.route('/get_unique_values_b', methods=['GET'])
def get_unique_values_b():
    value_a = request.args.get('value_a', None)
    df = your_function()
    if value_a:
        df = df[df['A'] == value_a]
    unique_values = df['B'].unique().tolist()
    return jsonify(unique_values)

@app.route('/get_unique_values_c', methods=['GET'])
def get_unique_values_c():
    value_a = request.args.get('value_a', None)
    value_b = request.args.get('value_b', None)
    df = your_function()
    if value_a:
        df = df[df['A'] == value_a]
    if value_b:
        df = df[df['B'] == value_b]
    unique_values = df['C'].unique().tolist()
    return jsonify(unique_values)

@app.route('/get_column_type', methods=['GET'])
def get_column_type():
    column_name = request.args.get('column_name', None)
    if column_name == 'A':
        return jsonify({'type': 'static'})
    elif column_name == 'B':
        return jsonify({'type': 'static'})
    elif column_name == 'C':
        return jsonify({'type': 'static'})
    elif column_name == 'D':
        return jsonify({'type': 'number'})
    elif column_name == 'E':
        return jsonify({'type': 'number'})
    elif column_name == 'F':
        return jsonify({'type': 'categorical', 'values': ['cat1', 'cat2', 'cat3', 'cat4', 'cat5']})


@app.route('/save_data', methods=['POST'])
def save_data():
    data = request.json
    new_df = pd.DataFrame(data)
    # Do whatever you want with the new_df
    print(new_df)
    return jsonify({"message": "Data saved successfully!"})


@app.route('/')
def index():
    return render_template('dataentry_index.html')


if __name__ == '__main__':
    app.run(debug=True)
