import pandas as pd
from google_sheets import get_service, process_table, upload_table
import traceback
import pdb    
import logging
from logger import init_logger

LOG_FILE = 'app.log'
logger = init_logger(LOG_FILE, level=logging.DEBUG)

def update_izometria(service_account_file: str, torzs_sheet_id: str):
    service = get_service(service_account_file)
    torzs_sheet = service.spreadsheets().get(spreadsheetId=torzs_sheet_id).execute()
    
    


def main():
    SERVICE_ACCOUNT_FILE = 'service_account.json'
    TORZSSHEET_ID = '1LtCsUPBqGYpnEZXyKFFoaPaeFfe1CLU-O9wiTMGqJUE'
    NORMASHEET_ID = '1Cd1PIhYJUQJd8Dr7XfcL31nd_ukNjAL-yqYGTFOVBh4'

    update_izometria(SERVICE_ACCOUNT_FILE, TORZSSHEET_ID, NORMASHEET_ID)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error(traceback.format_exc())
        pdb.post_mortem()