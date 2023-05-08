from flask import Flask, render_template, request, send_file, jsonify
import os
import logging
from normhours2 import process_excel, process_spreadsheet
import tempfile

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/process_excel', methods=['POST'])
def process_excel_route():
    input_file = request.files['input_file']
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        input_file_path = os.path.join(temp_dir, input_file.filename)
        input_file.save(input_file_path)

        try:
            filename, ext = os.path.splitext(input_file.filename)
            output_filename = f"{filename}_processed{ext}"
            output_file_path = os.path.join(temp_dir, output_filename)
            process_excel(input_file_path, output_file_path)
        except Exception as e:
            logging.error(f"Error processing Excel file: {str(e)}")
            return jsonify({'message': f'Error processing Excel file: {str(e)}'}), 500

        return send_file(output_file_path, as_attachment=True, download_name=output_filename)


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
