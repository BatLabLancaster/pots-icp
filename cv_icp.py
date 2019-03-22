import numpy as np
import sys,os.path
from pathlib import Path
import matplotlib.pyplot as plt
from src.io import jumpheader
from src.indexes import ind_val_leq
from src.icp_t_correction import icp_t_correction

"""A python module to deal with simultaneous measurements from different equipment.

.. moduleauthor:: Violeta Gonzalez-Perez <violegp@gmail.com>

This program expects the data to be in this format:
* pre_ocvfile,post_ocvfile: time(s) V
* ocvfile: time(s) V dum I(mA)
* icpfile: time(min),dum,ICP

The header of the files can be of any lenght as long as the first
character of each line is not a number.
"""

#############Input files#############
steps_pots_pre = '01_Zn_Steps_1MKOH_30RPM_01_OCV_C01.txt'
steps_pots_cv = '01_Zn_Steps_1MKOH_30RPM_01_OCV_C01.txt'
steps_pots_post = '01_Zn_Steps_1MKOH_30RPM_01_OCV_C01.txt'
steps_icp = '01_Zn_Steps_1MKOH_30RPM.csv'
preocv_file = '04_Zn_CV_2mVs_30RPM_1MKOH_OneNeb2_02_01_OCV_C01.txt'
cv_file = '04_Zn_CV_2mVs_30RPM_1MKOH_OneNeb2_02_03_CV_C01.txt'
postocv_file = '04_Zn_CV_2mVs_30RPM_1MKOH_OneNeb2_02_04_OCV_C01.txt'
icp_file = '05_Zn_CV_5mVs_30RPM_1MKOH_OneNeb2_01.csv'
#####################################

# Time correction calculations
# icp_t_correction(x,y)
slope, zero = icp_t_correction(steps_icp,
                               steps_pots_pre,
                               steps_pots_cv,
                               steps_pots_post)

##################################################
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
firstvalue = t_icp[0]

# Use correction calculated above for the time
t_icp = t_icp/slope - zero

# Loop over the (O)CV files
nsubsets = len(files)-1 
for i in range(nsubsets):
    # Read the data 
    ih = jumpheader(infiles[i])
    if (i==0 or i ==2):
        # Read the volage as prop
        times,prop = np.loadtxt(infiles[i], usecols= (0,1),unpack=True, skiprows=ih)
        prop_label = 'V(V)'
    elif (i==1):
        # Read the current as prop 
        times,prop = np.loadtxt(infiles[i], usecols= (0,3),unpack=True, skiprows=ih)
        prop_label = 'I(mA)'

    # Check the stepping size
    diff_t = np.unique(np.array([j-i for i,
                                 j in zip(times[:-1], times[1:])]))
    if (len(diff_t) > 1):
        print('WARNING: there are different step sizes within {}: {}'.format(prefix,diff_t))
        
    # Find the time of the last measurement
    last_t = times[len(times)-1] ; print(last_t)
    print(t_icp[0],t_icp[-1])
    
    # Find the index for the corresponding icpt
    d_index = ind_val_leq(t_icp,last_t) #; print(d_index)
    # Define the ICP subset 
    t_icp_subset= t_icp[:d_index+1]
    icp_subset= icp[:d_index+1]
    # Redefine t_icp for the next subset
    if(i < nsubsets-1):
        t_icp = t_icp[d_index+1:]
        icp = icp[d_index+1:]

    # Interpolate values to the smaller time array
    if (len(t_icp_subset)<=len(times)):
        xx = t_icp_subset
        yy2 = icp_subset
        yy1 = np.interp(xx,times,prop)
    else:
        xx = times
        yy1 = prop
        yy2 = np.interp(xx,t_icp_subset,icp_subset)

    # Plot
    fig, ax1 = plt.subplots()

    ax2 = ax1.twinx()
    ax1.plot(xx, yy1, 'g-')
    ax2.plot(xx, yy2, 'b-')

    ax1.set_xlabel('time (s, '+prefix[i]+')')
    ax1.set_ylabel(prop_label, color='g')
    ax2.set_ylabel('ICP', color='b')

    plotfile = 'output/'+prefix[i]+'.png'
    fig.savefig(plotfile)
    print('Output plot: ',plotfile)
    
    # Write output and plot
    tofile = np.column_stack((xx,yy1,yy2))
    outfil = 'output/'+files[i]
    with open(outfil, 'w') as outf:
        outf.write(prefix[i]+'_time(s),'+prop_label+',ICP \n')
        for row in tofile:
            np.savetxt(outf,tofile,fmt='%1.8e',delimiter=',')
    outf.closed
    print('Output file: {}'.format(outfil))

