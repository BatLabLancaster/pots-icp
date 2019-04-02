"""A python module to deal with simultaneous measurements from different equipment.

.. moduleauthor:: Violeta Gonzalez-Perez <violegp@gmail.com>

This program expects the data to be in this format:
* pre_ocvfile,post_ocvfile: time(s) V
* ocvfile: time(s) V dum I(mA)
* icpfile: time(min),dum,ICP

The header of the files can be of any lenght as long as the first
character of each line is not a number.
"""
#############Input files names to be modified#############
steps_pots = '01_Zn_Steps_1MKOH_30RPM_02_CP_C01.txt'
steps_icp = '01_Zn_Steps_1MKOH_30RPM.csv'
preocv_file = '04_Zn_CV_2mVs_30RPM_1MKOH_OneNeb2_02_01_OCV_C01.txt'
cv_file = '04_Zn_CV_2mVs_30RPM_1MKOH_OneNeb2_02_03_CV_C01.txt'
postocv_file = '04_Zn_CV_2mVs_30RPM_1MKOH_OneNeb2_02_04_OCV_C01.txt'
icp_file = '05_Zn_CV_5mVs_30RPM_1MKOH_OneNeb2_01.csv'
#####################################End of modifications

import numpy as np
import sys,os.path
from pathlib import Path
import matplotlib.pyplot as plt
from src.io import jumpheader
from src.indexes import ind_val_leq
from src.icp_t_correction import icp_t_correction

# The files with the data to be analyzed
files= [preocv_file,cv_file,postocv_file,icp_file]
prefix= ['preocv','cv','postocv','icp']

# Check that those files exist in the inputdata folder
infiles = ['inputdata/'+ifile for ifile in files]

for ff in infiles:
    if not os.path.isfile(ff):
        print('STOP: file not found, \n {}'.format(ff)) ; sys.exit()

# Read the ICP data
ih = jumpheader(infiles[3]) #; print('ih={}'.format(ih)) 
t_icp, icp = np.loadtxt(infiles[3], usecols= (0,2),
                                 unpack=True, skiprows=ih, delimiter=',')
t_icp = t_icp*60. # converting to seconds

# Correct the ICP time
slope, zero = icp_t_correction(steps_icp,steps_pots,show_plots=True)
t_icp = (t_icp - zero)/slope

# Loop over the (O)CV files
nsubsets = len(files)-1 
for i in range(nsubsets):
    # Read the data 
    ih = jumpheader(infiles[i]) 
    if (i==0 or i ==2): #Pre and post-ocv
        times,voltage = np.loadtxt(infiles[i], usecols= (0,1),unpack=True, skiprows=ih)
        prop_label='V(V)'
    elif (i==1): # CV
       times,voltage,current = np.loadtxt(infiles[i], usecols= (0,1,3),unpack=True, skiprows=ih)
       prop_label='I(mA)'
       
    # Check the stepping size
    diff_t = np.unique(np.diff(times))
    if (len(diff_t) > 1):
        if (max(np.diff(diff_t)) > 5e-4):
            print('\n WARNING: there are different step sizes within {}: {} \n'.format(prefix[i],diff_t))
        
    # Find the time of the last measurement
    last_t = times[-1]
    print('  time({}): {:.3f} s to {:.3f} s'.format(prefix[i],times[0],last_t))

    if (times[0] > t_icp[-1]):
        sys.exit('STOP cv_icp.py \n   Potentiostate times are outside the ICP range')
    
    if (i<2 and last_t < t_icp[-1]):
        # Find the index for the corresponding icpt
        # one extra point will be taken
        d_index = ind_val_leq(t_icp,last_t) + 1 #; print(d_index,t_icp[d_index],last_t) 
        # Define the ICP subset 
        t_icp_subset= t_icp[:d_index+1]
        icp_subset= icp[:d_index+1]

        # Redefine t_icp for the next subset
        if(i < nsubsets-1):
            t_icp = t_icp[d_index-1:]
            icp = icp[d_index-1:]
    else:
        t_icp_subset= t_icp
        icp_subset= icp
    print('  times(ICP subset): {:.3f} s to {:.3f} s'.format(t_icp_subset[0],t_icp_subset[-1]))
    
    # Define the arrays to plot and store
    x_pots = times
    if(i == 1):
        y_pots = current
        vv = voltage
    else:
        y_pots = voltage
    # Take into account the values to the potentiostat up to the last ICP time
    if(times[-1]>t_icp_subset[-1]):
        d_index = ind_val_leq(times,t_icp_subset[-1])
        x_pots = times[:d_index+1]
        if(i == 1):
            y_pots = current[:d_index+1]
            vv = voltage[:d_index+1]
        else:
            y_pots = voltage[:d_index+1]

    # Interpolate to the potentiostat times
    y_icp = np.interp(x_pots,t_icp_subset,icp_subset)

    # Plot
    fig, ax1 = plt.subplots()
    
    ax2 = ax1.twinx()
    ax1.plot(x_pots, y_pots, 'g-')
    ax2.plot(x_pots, y_icp, 'b-')

    ax1.set_xlabel('time (s, '+prefix[i]+')')
    ax1.set_ylabel(prop_label, color='g')
    ax2.set_ylabel('ICP', color='b')

    plotfile = 'output/'+prefix[i]+'.pdf'
    fig.savefig(plotfile,bbox_inches='tight')
    print('Output plot: ',plotfile)
    
    # Write output and plot
    if (i==1):
        header = prefix[i]+'_time(s),V(V),I(mA),ICP \n'
        tofile = np.column_stack((x_pots,vv,y_pots,y_icp))
    else:
        header = prefix[i]+'_time(s),V(V),ICP \n'
        tofile = np.column_stack((x_pots,y_pots,y_icp))
        
    outfil = 'output/'+files[i]
    with open(outfil, 'w') as outf:
        outf.write(header)
        for row in tofile:
            np.savetxt(outf,tofile,fmt='%1.8e',delimiter=',')
    outf.closed
    print('Output file: {}'.format(outfil))

