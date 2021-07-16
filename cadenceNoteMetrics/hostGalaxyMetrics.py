import matplotlib
matplotlib.use('Agg')
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser()
parser.add_argument('-in', '--input', help="Full path to the input csv file")
parser.add_argument('-outdir', '--output', help="Full path to the output directory")
parser.add_argument('-sn', '--fitres', help="Full path to the SNANA fitres file")

# Execute the parse_args() method
args = parser.parse_args()

input_file = args.input
output_dir = args.output


## Load the spec-observed SNe
specSN = pd.read_csv(input_file)
specSN['snid'] = specSN['snid'].astype(int)
specSN['redshift'] = specSN['redshift'].astype(float)

f = open(output_dir+('/hostGalaxymetrics.txt'), 'w')

def groupMergeSpecSampleFitSample(snfit, specSN):
    specSN['postAll'] = specSN['pre_g'] + specSN['pre_r'] + specSN['pre_i'] + specSN['pre_z'] + specSN['post_g_all'] + specSN['post_r_all'] + specSN['post_i_all'] + specSN['post_z_all']
    specSN['postAllFilters'] = specSN['post_g_all'] + specSN['post_r_all'] + specSN['post_i_all'] + specSN['post_z_all']
    specSN['preAllFilters'] = specSN['pre_g'] + specSN['pre_r'] + specSN['pre_i'] + specSN['pre_z']
    groupSpec = specSN.groupby(['snid', 'peakmjd', 'ra', 'dec', 'hostgal_ra', 'hostgal_dec', 'sntype',
           'redshift', 'uni_filter', 'obs_count', 'pre_epochs', 'post_epochs',
           'num_pre_filters', 'num_post_filters', 'trigstart', 'pre_g', 'post_g',
           'pre_r', 'post_r', 'pre_i', 'post_i', 'pre_z', 'post_z', 'post_g_all',
           'post_r_all', 'post_i_all', 'post_z_all', 'postAll', 'postAllFilters', 'preAllFilters'])\
        .agg({'ob_first_tile_id': "count", 'mjd_obs': "min",'qmost_ra': 'mean','qmost_dec': 'mean','total_texp': 'sum','q3c_dist': 'mean'})\
        .reset_index()\
        .rename(columns={"ob_first_tile_id": "num_spec", "mjd_obs": "mjd_obs_first",\
                         "qmost_ra": "qmost_ra_mean", "qmost_dec": "qmost_dec_mean",\
                        "q3c_dist":"q3c_dist_mean"})
    merged = groupSpec.merge(snfit, how='inner', left_on='snid', right_on='CID', suffixes=(False, False), copy=True)
    mergedCosmo = merged[(abs(merged['c'])<.3) & (abs(merged['x1'])<3)\
                         & (merged['FITPROB']>0.001) & (merged['x1ERR']<1) & (merged['PKMJDERR']<1)].copy()
    mergedCosmo['mu'] = mergedCosmo['mB'] - (-19.365 - 0.141*mergedCosmo['x1'] + 3.1*mergedCosmo['c'])
    
    #mu_err = = ( mergedCosmo['mBERR']**2 + (0.141**2 * mergedCosmo['x1ERR']**2) + (3.1**2 * mergedCosmo['cERR']**2) + (2*0.141*cov_mBx1)  - (2*beta*cov_mBc) - (2*alpha*beta* cov_x1c) )**0.5
    sf = -2.5/(mergedCosmo['x0'] * np.log(10))
    
    mergedCosmo['muERR'] = ((mergedCosmo['mBERR'])**2 + (0.14*mergedCosmo['x1ERR'])**2 + (3.1*mergedCosmo['cERR'])**2 + 2*0.14*mergedCosmo['COV_x1_x0']*sf  - 2*3.1*mergedCosmo['COV_c_x0']*sf -2*0.14*3.1* mergedCosmo['COV_x1_c'] )**0.5
    
    mergedCosmo['sim_mu'] = mergedCosmo['SIM_mB'] - (-19.365 - 0.141*mergedCosmo['SIM_x1'] + 3.1*mergedCosmo['SIM_c'])
    


    return mergedCosmo, specSN, groupSpec

def round_sigfigs(num, sig_figs): 
     if num != 0: 
        return np.round(num, -int(np.floor(np.log10(abs(num))) - (sig_figs - 1))) 
     else:
        return 0  # Can't take the log of 0 

def plotnz(data, outdir):
    nia, bins, patch = plt.hist(data['redshift'][data['sntype']==1], bins=np.arange(0,1.3,0.05), histtype='step', label='SNe Ia: '+str(round_sigfigs(len(data['redshift'][data['sntype']==1]),2)), lw=1.5)
    #plt.hist(data['redshift'][np.isin(data['sntype'],np.array([21,25]))], bins=np.arange(0,1.3,0.05), histtype='step', label='Type II SNe: '+str(round_sigfigs(len(data['redshift'][np.isin(data['sntype'],np.array([21,25]))]),2)), lw=1.5)
    ncc, bins, patch = plt.hist(data['redshift'][np.isin(data['sntype'],np.array([20,23,32,33,35]))], bins=np.arange(0,1.3,0.05), histtype='step', label='CCSNe: '+str(round_sigfigs(len(data['redshift'][np.isin(data['sntype'],np.array([20,21,25,23,32,33,35]))]),2)), lw=1.5)
    nslsne, bins, patch =plt.hist(data['redshift'][np.isin(data['sntype'],np.array([70]))], bins=np.arange(0,1.3,0.05), histtype='step', label='SLSNe: '+str(round_sigfigs(len(data['redshift'][np.isin(data['sntype'],np.array([70]))]),2)), lw=1.5)
    ncart, bins, patch =plt.hist(data['redshift'][np.isin(data['sntype'],np.array([50]))], bins=np.arange(0,1.3,0.05), histtype='step', label='CaRT: '+str(round_sigfigs(len(data['redshift'][np.isin(data['sntype'],np.array([50]))]),2)), lw=1.5)
    nbg, bins, patch =plt.hist(data['redshift'][np.isin(data['sntype'],np.array([11,12]))], bins=np.arange(0,1.3,0.05), histtype='step', label='SN 91bg/Iax: '+str(round_sigfigs(len(data['redshift'][np.isin(data['sntype'],np.array([11,12]))]),2)), lw=1.5)
    #plt.hist(data['redshift'][np.isin(data['sntype'],np.array([60]))], bins=np.arange(0,1.3,0.05), histtype='step', label='KNe', lw=1.5)
    ntde, bins, patch =plt.hist(data['redshift'][np.isin(data['sntype'],np.array([80]))], bins=np.arange(0,1.3,0.05), histtype='step', label='TDEs: '+str(round_sigfigs(len(data['redshift'][np.isin(data['sntype'],np.array([80]))]),2)), lw=1.5)

    np.savetxt(outdir+'/nzHistogramHostgalaxySNe.csv', np.column_stack((0.5*(bins[1:]+bins[:-1]),nia,ncc,nslsne,ncart,nbg,ntde)), delimiter=',', header='zbin,n_ia,n_cc,n_slsne,n_cart,n_bgiax,ntde', fmt='%.3f')
    # plt.hist(data['redshift'][np.isin(data['sntype'],np.array([21,25]))], bins=np.arange(0,1.3,0.05), histtype='step', label=index2type[i])

    plt.xlim(-0.01,1.2)
    #plt.ylim(3,3e4)
    plt.xlabel('Redshift')
    plt.ylabel('Number of SNe in bin')
    plt.yscale('log')
    #plt.legend(loc='lower left',mode='expand',framealpha=0.95, fontsize='small', bbox_to_anchor=(0,1.02,1,0.2), ncol=1)
    plt.legend(loc='upper right',framealpha=0.95, fontsize='small',ncol=1)


    plt.savefig(str(outdir)+'/numberRedshiftBinsHostGalaxy.pdf', dpi=300, bbox_inches='tight')

    print('Total number of unique SNe: ', len(np.unique(data['snid'])))
    f.write('Total number of SNe: '+str(len(np.unique(data['snid'])))+'\n')
    f.write('Total number of SN Ia: '+str(len(np.unique(data['snid'][data['sntype']==1])))+'\n')
    f.write('Total number of CCSNe: '+str(len(np.unique(data['snid'][np.isin(data['sntype'],np.array([20,23,32,33,35]))])))+'\n')
    f.write('Total number of SLSNe: '+str(len(np.unique(data['snid'][np.isin(data['sntype'],np.array([70]))])))+'\n')
    f.write('Total number of CaRT: '+str(len(np.unique(data['snid'][np.isin(data['sntype'],np.array([50]))])))+'\n')
    f.write('Total number of 91bg/Iax: '+str(len(np.unique(data['snid'][np.isin(data['sntype'],np.array([11,12]))])))+'\n')
    f.write('Total number of TDE: '+str(len(np.unique(data['snid'][np.isin(data['sntype'],np.array([80]))])))+'\n')

print(specSN.dtypes)
plotnz(specSN, output_dir)

f.close()

if argparse.fitres:
   fitres = args.fitres
   snfit = pd.read_csv(fitres, delimiter='\s+', comment='#')
   snfit['CID'] = snfit['CID'].astype(int)

   mergedCosmo, snSpec, groupSpecMerged = groupMergeSpecSampleFitSample(snfit, specSN)

   mjderr = np.mean(mergedCosmo['PKMJDERR']); mjdstd = np.std(mergedCosmo['PKMJDERR'])
   preAllfilters = np.mean(mergedCosmo[mergedCosmo['sntype']==1]['preAllFilters']); preAllfilters_std = np.std(mergedCosmo[mergedCosmo['sntype']==1]['preAllFilters'])
   postAllfilters= np.mean(mergedCosmo[mergedCosmo['sntype']==1]['postAllFilters']); postAllfilters_std= np.std(mergedCosmo[mergedCosmo['sntype']==1]['postAllFilters'])
   muerr = np.mean(mergedCosmo[mergedCosmo['sntype']==1]['muERR']); muerr_std = np.std(mergedCosmo[mergedCosmo['sntype']==1]['muERR'])
   cErr = np.mean(mergedCosmo[mergedCosmo['sntype']==1]['cERR']); cErr_std = np.std(mergedCosmo[mergedCosmo['sntype']==1]['cERR'])
   x1Err = np.mean(mergedCosmo[mergedCosmo['sntype']==1]['x1ERR']); x1Err_std = np.std(mergedCosmo[mergedCosmo['sntype']==1]['x1ERR'])

   iaStats = open(output_dir+('/hostGalaxy_Ia_stats.txt'), 'w')

   iaStats.write('mjd,'+str(mjderr)+','+str(mjdstd)+'\n')
   iaStats.write('PreAllFilters,'+str(preAllfilters)+','+str(preAllfilters_std)+'\n')
   iaStats.write('PostAllFilter,'+str(postAllfilters)+','+str(postAllfilters_std)+'\n')
   iaStats.write('muErr,'+str(muerr)+','+str(muerr_std)+'\n')
   iaStats.write('cErr,'+str(cErr)+','+str(cErr_std)+'\n')
   iaStats.write('x1Err,'+str(x1Err)+','+str(x1Err_std)+'\n')

   iaStats.close()
