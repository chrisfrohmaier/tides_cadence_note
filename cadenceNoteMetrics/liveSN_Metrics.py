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
fitres = args.fitres

## Load the spec-observed SNe
specSN = pd.read_csv(input_file)
specSN['snid'] = specSN['snid'].astype(int)
specSN['redshift'] = specSN['redshift'].astype(float)

f = open(output_dir+('/liveSNmetrics.txt'), 'w')

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

    np.savetxt(outdir+'/nzHistogramLiveSNe.csv', np.column_stack((0.5*(bins[1:]+bins[:-1]),nia,ncc,nslsne,ncart,nbg,ntde)), delimiter=',', header='zbin,n_ia,n_cc,n_slsne,n_cart,n_bgiax,ntde', fmt='%.3f')
    # plt.hist(data['redshift'][np.isin(data['sntype'],np.array([21,25]))], bins=np.arange(0,1.3,0.05), histtype='step', label=index2type[i])

    plt.xlim(-0.01,1.2)
    #plt.ylim(3,3e4)
    plt.xlabel('Redshift')
    plt.ylabel('Number of SNe in bin')
    plt.yscale('log')
    #plt.legend(loc='lower left',mode='expand',framealpha=0.95, fontsize='small', bbox_to_anchor=(0,1.02,1,0.2), ncol=1)
    plt.legend(loc='upper right',framealpha=0.95, fontsize='small',ncol=1)


    plt.savefig(str(outdir)+'/numberRedshiftBinsLive.pdf', dpi=300, bbox_inches='tight')

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
