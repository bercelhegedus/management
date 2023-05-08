from flask import Flask, render_template, request, send_file, jsonify
import os
import logging
from normhours2 import process_excel, process_spreadsheet

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/process_excel', methods=['POST'])
def process_excel_route():
    input_file = request.files['input_file']
    downloads_folder = os.path.expanduser("~/Downloads")
    input_file_path = os.path.join(downloads_folder, input_file.filename)
    input_file.save(input_file_path)

    try:
        process_excel(input_file_path, 'output.xlsx')
    except Exception as e:
        # Log the error and show a message to the user
        logging.error(f"Error processing Excel file: {str(e)}")
        return jsonify({'message': f'Error processing Excel file: {str(e)}'}), 500

    output_file_path = 'output.xlsx'
    return send_file(output_file_path, as_attachment=True, attachment_filename='output.xlsx')


@app.route('/process_spreadsheet', methods=['POST'])
def process_spreadsheet_route():
    # Call your process_spreadsheet function here
    try:
        process_spreadsheet()
    except Exception as e:
        # Log the error and show a message to the user
        logging.error(f"Error updating Google Sheets: {str(e)}")
        return jsonify({'message': f'Error updating Google Sheets: {str(e)}'}), 500

    return jsonify({'message': 'Google Sheets updated.'}), 200

if __name__ == '__main__':
    app.run(debug=True)
