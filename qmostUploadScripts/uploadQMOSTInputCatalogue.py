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


qInput_Cols = ['catv', 'survey', 'subsurvey',\
    'qsp_id', 'resolution', 'ra', 'dec', 'mag',\
       'texp_d', 'texp_g', 'texp_b', 'fcompl',\
           'jd_earliest', 'jd_latest' ]

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--creds', help="Full path to your Database login credentials")
parser.add_argument('-p', '--file', help="Full path to the QMOST file")
parser.add_argument('-r', '--catv', help="Catalogue version, and int of the date")
parser.add_argument('-sid', '--survey', help="Survey ID, hint we're 10")
parser.add_argument('-subid', '--subsurvey', help="Sub-Survey ID, 1,2, or 3")



# Execute the parse_args() method
args = parser.parse_args()

input_file = args.file
catv = args.catv
sid = args.survey
subid = args.subsurvey
credentials_file = args.creds

#print(input_file, catv, sid, subid)

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
    fin3 = Table.read(input_file, format='fits')
except:
    print('Failed to load file: ', input_file)
    #sys.exit()
fin3.convert_bytestring_to_unicode()

df_QMOST_input = fin3.to_pandas()

df_QMOST_input['catv'] = catv
df_QMOST_input['survey'] = sid
df_QMOST_input['subsurvey'] = subid

df_QMOST_input.columns = df_QMOST_input.columns.str.lower()

output_phot = io.StringIO()
df_QMOST_input[qInput_Cols].to_csv(output_phot, sep='\t', header=False, index=False)
output_phot.seek(0)
contents = output_phot.getvalue()
cur.copy_from(output_phot, 'qmost_input_cat', null="") # null values become ''
conn.commit()
conn.close()
