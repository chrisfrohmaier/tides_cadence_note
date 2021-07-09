import argparse
import pandas as pd
from astropy.table import Table
import os
import numpy as np
import sys
from sqlalchemy import create_engine
import psycopg2 
import io
import yaml

qmost_cols = ['vid','monyear','file','qsp_id','survey_id','subsurvey_id','ra','dec','f_compl','ntile','nob','ntile_obs','nob_obs','fobs_max','fobs','fobs_etc','nfib','ptar','jd_first','jd_last']

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--creds', help="Full path to your Database login credentials")
parser.add_argument('-p', '--file', help="Full path to the QMOST file")
parser.add_argument('-my', '--monyear', help="Month Year of thesimulation")
parser.add_argument('-vr', '--vsim', help="Version of the simulation")

# Execute the parse_args() method
args = parser.parse_args()

input_file = args.file
vsim = args.vsim
monyear = args.monyear
credentials_file = args.creds

##Connect to database
conf = yaml.load(open(credentials_file))
username = conf['tidesdb']['username']
pwd = conf['tidesdb']['password']
host = conf['tidesdb']['host']
port = conf['tidesdb']['port']
db_name = conf['tidesdb']['db_name']
engine = create_engine('postgresql+psycopg2://'+str(username)+':'+str(pwd)+'@'+str(host)+':'+str(port)+'/'+str(db_name))
conn = engine.raw_connection()
cur = conn.cursor()

#input_file = '/Users/cfrohmaier/Documents/TiDES/lsstFellow/Jan2021/TiDES_LSST/MV_LSSTDDF_CART/LSSTDDF_NONIaMODEL0-0012_file.FITS.gz'
base, filein = os.path.split(input_file)

try:
    fin1 = Table.read(input_file, format='fits')
except:
    print('Failed to load file: ', input_file)
    sys.exit()
fin1.convert_bytestring_to_unicode()

df_qmost = fin1.to_pandas()

df_qmost['vid'] = int(vsim)
df_qmost['monyear'] = str(monyear)
df_qmost['file'] = str(filein)

df_qmost = df_qmost[df_qmost['survey_id']==10] #Only want TiDES (survey 10) Reduces size by 100x!!

print("Starting Upload")
#print(df_qmost[qmost_cols])
df_qmost.fillna("")
output_phot = io.StringIO()
df_qmost[qmost_cols].to_csv(output_phot, sep='\t', header=False, index=False)
output_phot.seek(0)
contents = output_phot.getvalue()
cur.copy_from(output_phot, 'qmost_targets', null="") # null values become ''
conn.commit()
conn.close()
print("Upload Complete")