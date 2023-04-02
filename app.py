from flask import Flask, request, jsonify, render_template
import json
import threading
from normhours import process_sheets
import logging
from logger import init_logger

LOG_FILE = 'app.log'
logger = init_logger(LOG_FILE, level=logging.DEBUG)

app = Flask(__name__)

@app.route('/')
def home():
    logger.info(f"Request: {request.method} {request.path}")
    return "Welcome to the Flask App! This is a webhook application for processing Google Sheets."

@app.route('/logs')
def show_logs():
    with open(LOG_FILE, 'r') as log_file:
        logs = log_file.read().splitlines()
    return render_template('logs.html', logs=logs)

@app.route('/webhook', methods=['POST'])
def webhook():
    logger.info(f"Request: {request.method} {request.path} {request.data}")

    SERVICE_ACCOUNT_FILE = 'service_account.json'
    TORZSSHEET_ID = '1LtCsUPBqGYpnEZXyKFFoaPaeFfe1CLU-O9wiTMGqJUE'
    NORMASHEET_ID = '1Cd1PIhYJUQJd8Dr7XfcL31nd_ukNjAL-yqYGTFOVBh4'

    if request.method == 'POST':
        data = request.get_json(force=True)
        logger.info(data)
        entry_ids = data.get('entry_ids', [])
        if isinstance(entry_ids, str):
            entry_ids = [entry_ids]
        sheets = data.get('sheets', ['Csotarto', 'Hegesztes', 'Csovezetek', 'Karimaszereles'])

        try:
            thread = threading.Thread(target=process_sheets,
                            kwargs={
                                'service_account_file': SERVICE_ACCOUNT_FILE,
                                'torzssheet_id': TORZSSHEET_ID,
                                'normasheet_id': NORMASHEET_ID,
                                'ids_to_update': entry_ids,
                                'sheets': sheets,
                                'update_blanks': True
                            })
            thread.start()
            logger.info("Update started")
            return jsonify({'message': 'Update started.'}), 200
        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 500

    return jsonify({'message': 'Invalid request.'}), 400

if __name__ == '__main__':
 
    app.run(debug=True)
