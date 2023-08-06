from flask import Flask, jsonify, render_template, request
import pandas as pd

app = Flask(__name__)

def your_function():
    df = pd.DataFrame({
   'A': ['foo', 'bar', 'foo', 'bar', 'foo', 'bar', 'foo', 'foo'],
   'B': ['one', 'one', 'two', 'three', 'two', 'two', 'one', 'three'],
   'C': ['small', 'large', 'large', 'small', 'small', 'large', 'small', 'small'],
   'D': [1, 2, 2, 3, 3, 4, 5, 6],
   'E': [2, 4, 5, 5, 6, 6, 8, 9]
    })
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
