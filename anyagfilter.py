from tables import *
import pandas as pd


import traceback
import pdb

try:
    mod=Workbook.read_google_sheets_to_workbook('service_account.json','1IYJj1j9i0c_8W4PR_tVr7sf98cp9mznpCpSp-0ITbnI')
    pdb.set_trace()
    anyag = mod.get_table('Anyag')
    anyag = Table(anyag.data.groupby('Megnevezes')['Szorzo'].agg(['unique']).applymap(lambda x: x[0]).reset_index())
    anyag.rename_columns({'unique':'Szorzo'})
    
    mod.add_table('Anyag', anyag)
    mod.write_to_google_sheets('service_account.json','1IYJj1j9i0c_8W4PR_tVr7sf98cp9mznpCpSp-0ITbnI')
except:
    traceback.print_exc()
    pdb.post_mortem()

