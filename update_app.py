from flask import Flask, render_template, request, send_file, jsonify, make_response, Blueprint
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
import logging
from normhours2 import process_excel, process_spreadsheet, process_all
from tables import Workbook
import tempfile
import io

update_blueprint = Blueprint('update_update_blueprint', __name__)

@update_blueprint.route('/update', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('update_index.html')



def get_output_bytes(input_file):

    input_data = input_file.read()
    input_bytes = io.BytesIO(input_data)

    data_workbook = Workbook.read_excel_to_workbook(input_bytes)

    SERVICE_ACCOUNT_FILE = 'service_account.json'
    NORMASHEET_ID = '1Cd1PIhYJUQJd8Dr7XfcL31nd_ukNjAL-yqYGTFOVBh4'
    MODIFIER_ID = '1IYJj1j9i0c_8W4PR_tVr7sf98cp9mznpCpSp-0ITbnI'

    norms_workbook = Workbook.read_google_sheets_to_workbook(SERVICE_ACCOUNT_FILE, NORMASHEET_ID)
    modifier_workbook = Workbook.read_google_sheets_to_workbook(SERVICE_ACCOUNT_FILE, MODIFIER_ID)

    process_all(data_workbook, norms_workbook, modifier_workbook)

    output = io.BytesIO()
    data_workbook.write_to_excel(output)
    output.seek(0)
    
    return output

@update_blueprint.route('/process_excel', methods=['POST'])
def process_excel_route():
    file = request.files['input_file']
    print(file.filename)
    input_file = file.stream
    output_bytes = get_output_bytes(input_file)
    output_filename = f"{file.filename}"
    
    response = make_response(send_file(output_bytes, download_name=output_filename, as_attachment=False))
    response.headers['X-Input-Filename'] = file.filename
    return response


@update_blueprint.route('/process_spreadsheet', methods=['POST'])
def process_spreadsheet_route():
    # Call your process_spreadsheet function here
    try:
        process_spreadsheet()
    except Exception as e:
        # Log the error and show a message to the user
        logging.error(f"Error updating Google Sheets: {str(e)}")
        return jsonify({'message': f'Error updating Google Sheets: {str(e)}'}), 500

    return jsonify({'message': 'Google Sheets updated.'}), 200
