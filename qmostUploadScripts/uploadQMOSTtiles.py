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


qmost_cols = ['vid','monyear','file','tile_id','status','jd','ob_ntile','ob_first_tile_id','ra','dec','pos','texp','isky','n_subsurveys','ntotal_tar_lr','ntotal_tar_hr','navail_tar_lr','navail_tar_hr','nfib_tar_lr','nfib_tar_hr','nfib_empty_lr','nfib_empty_hr','fh_avail_lr','fh_sci_lr','fh_empty_lr','fh_overexp_lr','fh_uncompl_lr','fh_extra_lr','fh_avail_hr','fh_sci_hr','fh_empty_hr','fh_overexp_hr','fh_uncompl_hr','fh_extra_hr','weather_factor']

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

#print(df_qmost[qmost_cols])

output_phot = io.StringIO()
df_qmost[qmost_cols].to_csv(output_phot, sep='\t', header=False, index=False)
output_phot.seek(0)
contents = output_phot.getvalue()
cur.copy_from(output_phot, 'qmost_tiles', null="") # null values become ''
conn.commit()
conn.close()