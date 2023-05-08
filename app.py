from flask import Flask, render_template, request, send_file, jsonify, make_response
import os
import logging
from normhours2 import process_excel, process_spreadsheet, process_all
from tables import Workbook
import tempfile
import io

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')



def get_output_bytes(input_file):

    input_data = input_file.read()
    input_bytes = io.BytesIO(input_data)

    data_workbook = Workbook.read_excel_to_workbook(input_bytes)

    SERVICE_ACCOUNT_FILE = 'service_account.json'
    NORMASHEET_ID = '1Cd1PIhYJUQJd8Dr7XfcL31nd_ukNjAL-yqYGTFOVBh4'

    norms_workbook = Workbook.read_google_sheets_to_workbook(SERVICE_ACCOUNT_FILE, NORMASHEET_ID)

    process_all(data_workbook, norms_workbook)

    output = io.BytesIO()
    data_workbook.write_to_excel(output)
    output.seek(0)
    
    return output

@app.route('/process_excel', methods=['POST'])
def process_excel_route():
    file = request.files['input_file']
    print(file.filename)
    input_file = file.stream
    output_bytes = get_output_bytes(input_file)
    output_filename = f"{file.filename}"
    
    response = make_response(send_file(output_bytes, download_name=output_filename, as_attachment=False))
    response.headers['X-Input-Filename'] = file.filename
    return response


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
