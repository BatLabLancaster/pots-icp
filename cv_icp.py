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

tini = dt_pots   # Start time to consider the CV data in plots

icols_icp = [icol_icp,2] # Columns with ICP steps to be plot (e.g. [1,2])
showplots = True  # True = plots are shown while program runs
plotformat = 'png' # or 'pdf'  or 'jpg'
#####################################End of modifications

import numpy as np
import os.path
import matplotlib.pyplot as plt
from src.indexes import get_icp_subsets
from src.plotting import show_pots_icp
from src.io import *
from src.icp_t_correction import *

# Check if multiple CV files are expected
if (multipleCVfiles):
    cv_file = joinCVfiles()
     
# The files with the data to be analyzed
files= [preocv_file,cv_file,postocv_file,icp_file]
Dt = get_Dt(files)
prefixes= ['preocv','cv','postocv','icp']
infiles = ['inputdata/'+ifile for ifile in files]

# Get ICP/intensity header
icp_colnoms = get_col_nom(infiles[3],icols_icp,delimiter=',')
icp_head = ", ".join(icp_colnoms)

# Check that those files exist in the inputdata folder
check_files(infiles)

# Read the ICP time in seconds
t_icp = 60*read_columns(infiles[3],[0],delimiter=',')

# Correct the ICP time
if correct_time_manually:
    slope, zero = icp_t_manual(steps_icp,steps_pots,
                               stepcol_pots,icol_icp,
                               tstart_pots,dt_pots,
                               height_fraction,
                               slope=manual_slope,
                               zero=manual_zero,
                               show_plots=showplots,
                               plot_format=plotformat)
else:
    slope, zero = icp_t_correction(steps_icp,steps_pots,
                                   stepcol_pots,icol_icp,
                                   tstart_pots,dt_pots,
                                   height_fraction,
                                   show_plots=showplots,
                                   plot_format=plotformat)
t_icp = (t_icp - zero)/slope

# Read the ICP data
icp = read_columns(infiles[3],icols_icp,delimiter=',')

# Loop over the (O)CV files
for i in range(len(files)-1):

    if (i==0 or i ==2): 
        # Read the Pre and Post-ocv files
        times = read_columns(infiles[i],0)
        voltage = read_columns(infiles[i],1)
        prop_label='V(V)'
        
    elif (i==1):
        # Read the CV files, ignoring data for t<tini
        times = read_columns(infiles[i],0)
        voltage = read_columns(infiles[i],1)
        cellV = read_columns(infiles[i],2)
        current = read_columns(infiles[i],3)
        prop_label='I(A)'
       
    # Check the stepping size
    diff_t = np.unique(np.diff(times))
    if (len(diff_t) > 1):
        if (max(np.diff(diff_t)) > 5e-4):
            print('\n WARNING: there are different step sizes within {} ({}): {} \n'.format(prefixes[i],files[i],diff_t))
        
    # Find the time of the last measurement
    print('  time({})+Dt: {:.3f} s to {:.3f} s'.format(prefixes[i],times[0]+Dt[i],times[-1]+Dt[i]))

    t_icp_subset, icp_subset = get_icp_subsets(prefixes[i],
                                               times[0],times[-1],Dt[i],
                                               t_icp,icp,len(icols_icp))

    print('  times(ICP subset): {:.3f} s to {:.3f} s'.format(t_icp_subset[0],t_icp_subset[-1]))

    # Define the arrays to plot and store
    x_pots = times+Dt[i]

    if(i == 1):
        y_pots = current
        vv = voltage
    else:
        y_pots = voltage

        
    # Get different ICPs
    if (len(icols_icp) == 1):
        y_icp = np.interp(x_pots,t_icp_subset,icp_subset)
        print(prefixes[i],y_icp,t_icp_subset,icp_subset,'+++')
    else:
        isub = -1
        for sub in icp_subset:
            y = np.interp(x_pots,t_icp_subset,sub)
            isub += 1
            if (isub == 0):
                y_icp = y
            else:
                y_icp = np.column_stack((y_icp,y))

    # Plot POTS and ICP
    show_pots_icp(x_pots,y_pots,y_icp,tini,prop_label,
                  prefixes[i],plot_format=plotformat,
                  icplabels=icp_colnoms)

    # Write output
    header1 = '# '+prefixes[i]+'\n' 
    tofile = np.array([])
    if (i==1):
        header2 = '# time, E, I, '+icp_head+', j \n'
        header3 = '# s, V, mA, counts, mA cm-2 \n'
        y_pots_area = y_pots/area
        tofile = np.column_stack((x_pots,vv,y_pots,y_icp,y_pots_area))
    else:
        header2 = '# time, E, '+icp_head+' \n'
        header3 = '# s, V, counts \n'
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
