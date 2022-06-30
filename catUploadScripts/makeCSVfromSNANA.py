import argparse
import pandas as pd
from astropy.table import Table
import os
import numpy as np
import sys

cols = ['SUBSURVEY','SNID','IAUC','FAKE','RA','DEC','PIXSIZE','NXPIX','NYPIX','CCDNUM',\
        'SNTYPE','NOBS','PTROBS_MIN','PTROBS_MAX','MWEBV','MWEBV_ERR','REDSHIFT_HELIO',\
        'REDSHIFT_HELIO_ERR','REDSHIFT_FINAL','REDSHIFT_FINAL_ERR','VPEC','VPEC_ERR',\
        'HOSTGAL_NMATCH','HOSTGAL_NMATCH2','HOSTGAL_OBJID','HOSTGAL_PHOTOZ',\
        'HOSTGAL_PHOTOZ_ERR','HOSTGAL_SPECZ','HOSTGAL_SPECZ_ERR','HOSTGAL_RA','HOSTGAL_DEC',\
        'HOSTGAL_SNSEP','HOSTGAL_DDLR','HOSTGAL_CONFUSION','HOSTGAL_LOGMASS',\
        'HOSTGAL_LOGMASS_ERR','HOSTGAL_sSFR','HOSTGAL_sSFR_ERR','HOSTGAL_MAG_u',\
        'HOSTGAL_MAG_g','HOSTGAL_MAG_r','HOSTGAL_MAG_i','HOSTGAL_MAG_z','HOSTGAL_MAG_Y',\
        'HOSTGAL_MAGERR_u','HOSTGAL_MAGERR_g','HOSTGAL_MAGERR_r','HOSTGAL_MAGERR_i',\
        'HOSTGAL_MAGERR_z','HOSTGAL_MAGERR_Y','HOSTGAL_SB_FLUXCAL_u','HOSTGAL_SB_FLUXCAL_g',\
        'HOSTGAL_SB_FLUXCAL_r','HOSTGAL_SB_FLUXCAL_i','HOSTGAL_SB_FLUXCAL_z',\
        'HOSTGAL_SB_FLUXCAL_Y','PEAKMJD','SEARCH_TYPE','SIM_MODEL_NAME','SIM_MODEL_INDEX',\
        'SIM_TYPE_INDEX','SIM_TYPE_NAME','SIM_TEMPLATE_INDEX','SIM_LIBID','SIM_NGEN_LIBID',\
        'SIM_NOBS_UNDEFINED','SIM_SEARCHEFF_MASK','SIM_REDSHIFT_HELIO','SIM_REDSHIFT_CMB',\
        'SIM_REDSHIFT_HOST','SIM_REDSHIFT_FLAG','SIM_VPEC','SIM_DLMU','SIM_LENSDMU','SIM_RA',\
        'SIM_DEC','SIM_MWEBV','SIM_PEAKMJD','SIM_MAGSMEAR_COH','SIM_AV','SIM_RV','SIM_PEAKMAG_u',\
        'SIM_PEAKMAG_g','SIM_PEAKMAG_r','SIM_PEAKMAG_i','SIM_PEAKMAG_z','SIM_PEAKMAG_Y',\
        'SIM_EXPOSURE_u','SIM_EXPOSURE_g','SIM_EXPOSURE_r','SIM_EXPOSURE_i','SIM_EXPOSURE_z',\
        'SIM_EXPOSURE_Y','SIM_GALFRAC_u','SIM_GALFRAC_g','SIM_GALFRAC_r','SIM_GALFRAC_i',\
        'SIM_GALFRAC_z','SIM_GALFRAC_Y','SIM_SUBSAMPLE_INDEX']

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--path', help="Full path to the HEADfile")

# Execute the parse_args() method
args = parser.parse_args()

input_head = args.path
#input_head = '/Users/cfrohmaier/Documents/TiDES/lsstFellow/Jan2021/TiDES_LSST/MV_LSSTDDF_CART/LSSTDDF_NONIaMODEL0-0012_HEAD.FITS.gz'
base, headin = os.path.split(input_head)
input_phot = base+'/'+headin.split('HEAD')[0]+'PHOT'+headin.split('HEAD')[1]
#print(input_phot)

try:
    fin1 = Table.read(input_head, format='fits')
except:
    print('Failed to load file: ', input_head)
    sys.exit()
fin1.convert_bytestring_to_unicode()
#phots = fits.open(phot_in[k])
try:
    phot1 = Table.read(input_phot, format='fits')
except:
    print('Failed to load file: ', input_phot)
    sys.exit()

phot1.convert_bytestring_to_unicode()
df_head = fin1.to_pandas() #pd.DataFrame(fin[1].data)
df_phots = phot1.to_pandas()#pd.DataFrame(phots[1].data)

### Update 1st April because Rick changed SNANA
if 'CCDNUM' not in df_head.columns:
    df_head['CCDNUM'] = 0

##Update 30 June 2022
##Rick made come more changes
if 'SUBSURVEY' not in df_head.columns:
    df_head['SUBSURVEY'] = ''
if 'HOSTGAL_sSFR' not in df_head.columns:
    df_head['HOSTGAL_sSFR'] = -99
if 'HOSTGAL_sSFR_ERR' not in df_head.columns:
    df_head['HOSTGAL_sSFR_ERR'] = -99

##Rick also changed the PHOT files to
if 'FIELD' not in df_phots.columns:
    df_phots['FIELD'] = ''
if 'PHOTFLAG' not in df_phots.columns:
    df_phots['PHOTFLAG'] = 0
if 'PHOTPROB' not in df_phots.columns:
    df_phots['PHOTPROB'] = -9
if 'PSF_SIG1' not in df_phots.columns:
    df_phots['PSF_SIG1'] = -99
if 'SKY_SIG' not in df_phots.columns:
    df_phots['SKY_SIG'] = -99
if 'ZEROPT' not in df_phots.columns:
    df_phots['ZEROPT'] = -99

#!!! Ra, DEC scatter put that in now
def radecScatter():
    '''We need this function because SNANA only creates 50,000
    unique LIBIDs. This means that a modest number of our transients will 
    have repeated Ra, DEC values. We only need to scatter the RA, DECs by
    0.338 degrees to combat this. It is not as simple as a circular scatter,
    but we can approximate it as one.
    '''
    a = np.random.random() * 2 *np.pi #Random angle to scatter in circle
    r = np.random.random() * 0.338 # Random radius to scatter coordinates

    ##Convert back to cartesian
    xRa = r * np.cos(a) #Check angle is in radians (0->2pi) yes
    yDec = r * np.sin(a)
    ## The returned coordinates will be the amount I shift the SN and Galaxy Ra, DEC
    return [xRa, yDec]




##Firstly, we dump the fin files
df_head['SUBSURVEY'] = df_head['SUBSURVEY'].str.strip()
df_head['SNID']=df_head['SNID'].astype(int)
df_head.replace('NULL            ', "",inplace=True)
df_head.replace(' ', "",inplace=True)

if 'LSSTWFD' in headin.split('_')[0]:
    #print('WFD Field')
    scatt = np.array([radecScatter() for x in range(len(df_head))])
    df_head['RA'] = df_head['RA'] + scatt[:,0]
    df_head['DEC'] = df_head['DEC'] + scatt[:,1]
    df_head['HOSTGAL_RA'] = df_head['HOSTGAL_RA'] + scatt[:,0]
    df_head['HOSTGAL_DEC'] = df_head['HOSTGAL_DEC'] + scatt[:,1]

df_head[cols].to_csv(base+'/'+headin.split('HEAD')[0]+'HEAD.csv', sep=',', header=True, index=False)

df_phots['SNID'] = 0
df_phots.replace(' ', "",inplace=True)
df_phots['FIELD'] = df_phots['FIELD'].str.strip()
df_phots.replace('NULL', "",inplace=True)

# print(df_phots)

photSNIDs = np.zeros(len(df_phots))

# for i in range(0,len(df_head)):
#     idx = np.zeros(len(df_phots))
#     print(df_head['PTROBS_MIN'].iloc[i])
#     idx[int(df_head['PTROBS_MIN'].iloc[i])-1:int(df_head['PTROBS_MAX'].iloc[1])-1] = 1
#     df_phots['SNID'][idx] = int(df_head['SNID'].iloc[i])
for index, lc in df_head.iterrows():
    #print([lc['PTROBS_MIN'],lc['PTROBS_MAX']])
    
    photSNIDs[int(lc['PTROBS_MIN'])-1:int(lc['PTROBS_MAX'])] = int(lc['SNID'])
#     df_phots['SNID'][idx] = int(lc['SNID'])
#     # lc_slice=df_phots[lc['PTROBS_MIN']:lc['PTROBS_MAX']].copy()
#     # #!!! Filter strip! Do that like df_head['SUBSURVEY'] = df_head['SUBSURVEY'].str.strip()
#     # #!!! Ra, DEC scatter put that in now
#     # snid_col = pd.DataFrame([snid for x in range(len(lc_slice))], columns=['SNID'])
#     # phot_dump = pd.DataFrame(np.column_stack((snid_col,lc_slice)), columns=list(snid_col.columns)+list(lc_slice.columns))
#     # #print(phot_dump)
#     # output_phot = io.StringIO()
#     # phot_dump.to_csv(output_phot, sep='\t', header=False, index=False)
#     # output_phot.seek(0)
#     # contents = output_phot.getvalue()
#     # cur.copy_from(output_phot, 's10_4most_ddf_sn_phot', null="") # null values become ''
#     # conn.commit()

# df_phots['FLT'] = df_phots['FLT'].str.strip()
df_phots['SNID'] = photSNIDs.astype(int)
df_phots = df_phots[df_phots['SNID']>0]
df_phots = df_phots[df_phots['FLUXCAL']>0]

#Update 1st April because Rick renames columns without telling anyone. Fucks sake.
if 'FLT' not in df_phots.columns:
    df_phots.rename(columns={'BAND':'FLT'}, inplace=True)
    
photCols = ['SNID', 'MJD', 'FLT', 'FIELD', 'PHOTFLAG', 'PHOTPROB', 'FLUXCAL', 'FLUXCALERR', 'PSF_SIG1', 'SKY_SIG', 'ZEROPT', 'SIM_MAGOBS']
df_phots['FLT'] = df_phots['FLT'].str.strip()

df_phots[photCols].to_csv(base+'/'+headin.split('HEAD')[0]+'PHOT.csv', sep=',', header=True, index=False)