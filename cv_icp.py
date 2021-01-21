"""A python module to deal with simultaneous measurements from different equipment.

.. moduleauthor:: Violeta Gonzalez-Perez <violetagp@protonmail.com>

This program expects the data to be in this format:
* pre_ocvfile,post_ocvfile: time(s) V 
* cvfile: time(s) V cellV I(mA)
* icpfile: time(min),...[ICP column to be specified via icol_icp, same as for the steps]

The header of the files can be of any lenght as long as the first
character of each line is not a number.

For multiple CV files, this codes assume a name such:
CV_*_#.txt     (with * being hhmmss and # an integer)
Note that spaces CAN be present in the name of CV files.
"""
#############Input files names to be modified#############

steps_pots = 'Steps_094423.txt'
steps_icp = '01_Zn_Steps_200mMLi2SO4_15RPM.csv'
preocv_file = 'OCP_192955.txt'
cv_file = 'CV_193157_1.txt'
postocv_file = 'OCP_200155.txt'
icp_file = '04_Zn_CV_2mVs_1MKOH_15RPM.csv'

multipleCVfiles = True #True for multiple CV files

area =  1. # In cm2 to get j(mA cm-2)
stepcol_pots = 3 # Column with the current steps

icol_icp = 1 # Column with the ICP steps to be used in the time correction
height_fraction = 3. # Affecting the calculation of the time correction
tstart_pots = 10. # Start time for the time correction
dt_pots = 120.     # Time intrevals used for the time correction

correct_time_manually = False # Assume the following values
manual_slope = 0.5
manual_zero = 10.

icols_icp = [icol_icp,2] # Columns with ICP steps to be plot (e.g. [1,2])
showplots = True  # True = plots are shown while program runs
plotformat = 'png' # or 'pdf'  or 'jpg'
#####################################End of modifications

import numpy as np
import os.path
import matplotlib.pyplot as plt
from src.io import jumpheader, joinCVfiles
from src.indexes import ind_val_leq
from src.icp_t_correction import *

# Check if multiple CV files are expected
if (multipleCVfiles):
    cv_file = 'CVall.txt'
    joinCVfiles(cv_file)

# The files with the data to be analyzed
files= [preocv_file,cv_file,postocv_file,icp_file]
prefixes= ['preocv','cv','postocv','icp']

# Check that those files exist in the inputdata folder
infiles = ['inputdata/'+ifile for ifile in files]

for ff in infiles:
    if not os.path.isfile(ff):
        print('STOP: file not found, \n {}'.format(ff)) ; sys.exit()

# Read the ICP data
ih = jumpheader(infiles[3]) #; print('ih={}'.format(ih)) 
t_icp = np.loadtxt(infiles[3], usecols= (0,),
                   unpack=True, skiprows=ih, delimiter=',')
t_icp = t_icp*60. # converting to seconds

# Correct the ICP time
if correct_time_manually:
    slope = manual_slope
    zero = manual_zero

    prefix = steps_icp.split('.')[0]
    ts_pots, i_pots= read_pots_steps(steps_pots,stepcol_pots)
    ts_icp, i_icp = read_icp_steps(steps_icp,icol_icp)
    i_icp = (i_icp-min(i_icp))*max(i_pots)/max(i_icp)
    gt_pots,gi_pots = get_start_step_pots(ts_icp,ts_pots,i_pots,
                                          tstart_pots,dt_pots)
    gt_icp,gi_icp = get_start_step_icp(ts_pots,i_pots,ts_icp,i_icp,
                                       gt_pots,gi_pots,
                                       tstart_pots,dt_pots,
                                       height_fraction,
                                       prefix,plot_format=plotformat)
    ind=np.where(gt_icp>-999.)
    show_corrected_steps(slope,zero,gt_pots[ind],gt_icp[ind],
                         ts_pots,ts_icp,i_pots,i_icp,prefix,plot_format=plotformat)
    if (showplots): plt.show()
else:
    slope, zero = icp_t_correction(steps_icp,steps_pots,
                                   stepcol_pots,icol_icp,
                                   tstart_pots,dt_pots,
                                   height_fraction,
                                   show_plots=showplots,
                                   plot_format=plotformat)
t_icp = (t_icp - zero)/slope

# Read the ICP data
icp = np.loadtxt(infiles[3], usecols= (icols_icp),
                 unpack=True, skiprows=ih, delimiter=',')

# Loop over the (O)CV files
nsubsets = len(files)-1 
for i in range(nsubsets):
    # Read the data 
    ih = jumpheader(infiles[i]) 
    if (i==0 or i ==2): #Pre and post-ocv
        times,voltage = np.loadtxt(infiles[i], usecols= (0,1),unpack=True, skiprows=ih)
        prop_label='V(V)'
    elif (i==1): # CV
       times,voltage,cellV,current = np.loadtxt(infiles[i], usecols= (0,1,2,3),unpack=True, skiprows=ih)
       prop_label='I(A)'
       
    # Check the stepping size
    diff_t = np.unique(np.diff(times))
    if (len(diff_t) > 1):
        if (max(np.diff(diff_t)) > 5e-4):
            print('\n WARNING: there are different step sizes within {} ({}): {} \n'.format(prefixes[i],files[i],diff_t))
        
    # Find the time of the last measurement
    last_t = times[-1]
    print('  time({}): {:.3f} s to {:.3f} s'.format(prefixes[i],times[0],last_t))

    if (times[0] > t_icp[-1]):
        sys.exit('STOP (cv_icp:{}) \n Potentiostate times={} > {} (ICP range)'.format(prefixes[i],times[0],t_icp[-1]))

    if (i<2 and last_t < t_icp[-1]):
        # Find the index for the corresponding icpt
        # one extra point will be taken
        d_index = ind_val_leq(t_icp,last_t) + 1 #; print(d_index,t_icp[d_index],last_t) 
        # Define the ICP subset 
        t_icp_subset= t_icp[:d_index+1]
        icp_subset= icp[:,:d_index+1]

        # Redefine t_icp for the next subset
        if(i < nsubsets-1):
            t_icp = t_icp[d_index-1:]
            icp = icp[:,d_index-1:]
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

    # Plot
    fig, ax1 = plt.subplots()
    
    ax2 = ax1.twinx()
    ax1.plot(x_pots, y_pots, 'k--')

    for sub in icp_subset:
        # Interpolate to the potentiostat times
        y_icp = np.interp(x_pots,t_icp_subset,sub)
        ax2.plot(x_pots, y_icp)

    ax1.set_xlabel('time (s, '+prefixes[i]+')')
    ax1.set_ylabel(prop_label, color='k')
    ax2.set_ylabel('ICP', color='orange')

    plotfile = 'output/'+prefixes[i]+'.'+plotformat
    fig.savefig(plotfile,bbox_inches='tight')
    print('Output plot: ',plotfile)
        
    # Write output and plot
    header1 = '# '+prefixes[i]+'\n' 
    tofile = np.array([])
    if (i==1):
        header2 = '# time,E,I,intensity,j \n'
        header3 = '# s,V,mA,counts,mA cm-2 \n'
        y_pots_area = y_pots/area
        tofile = np.column_stack((x_pots,vv,y_pots,y_icp,y_pots_area))
    else:
        header2 = '# time,E,intensity \n'
        header3 = '# s,V,counts \n'
        tofile = np.column_stack((x_pots,y_pots,y_icp))

    outfil = 'output/'+files[i]
    with open(outfil, 'w') as outf:
        outf.write(header1)
        outf.write(header2)
        outf.write(header3)
        np.savetxt(outf,tofile,fmt='%1.8e',delimiter=',')
    outf.closed
    print('Output file: {}'.format(outfil))

if (showplots): plt.show()
