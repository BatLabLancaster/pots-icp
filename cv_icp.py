import numpy as np
import sys,os.path
from pathlib import Path
import matplotlib.pyplot as plt
from src.io import jumpheader
from src.indexes import ind_val_leq

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
preocv_file = 'preocv.txt'
cv_file = 'CV.txt'
postocv_file = 'postOCV.txt'
icp_file = 'ICP.csv'
#####################################

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
t_icp = t_icp - firstvalue # Set the start time = 0.

# Loop over the (O)CV files
nsubsets = len(files)-1 
for i in range(1):#nsubsets):
    # Read the data 
    ih = jumpheader(infiles[i])
    if (i==0 or i ==2):
        # Read the volage as prop
        times,prop = np.loadtxt(infiles[i], usecols= (0,1),unpack=True, skiprows=ih)
        prop_label = 'V (V)'
    elif (i==1):
        # Read the current as prop 
        times,prop = np.loadtxt(infiles[i], usecols= (0,3),unpack=True, skiprows=ih)
        prop_label = 'I (mA)'
        
    # Find the time of the last measurement
    last_t = times[len(times)-1] #; print(last_t)
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
    #tofile = zip(xx,yy1,yy2)
    data = np.array([xx,yy1,yy2])
    tofile = data.transpose()
    outfil = 'output/'+files[i]
    with open(outfil, 'w') as outf:
        outf.write(prefix[i]+'_time(s),V(V),ICP \n')
        for row in tofile:
            np.savetxt(outf,tofile,fmt='%1.8e',delimiter=',')
    outf.closed
    print('Output file: {}'.format(outfil))
    sys.exit()
