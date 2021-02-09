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
from src.indexes import ind_val_leq
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
        # Read the CV files
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
        if (len(icols_icp) == 1):
            icp_subset= icp[:d_index+1]
        else:
            icp_subset= icp[:,:d_index+1]

        # Redefine t_icp for the next subset
        if(i < len(files)-2):
            t_icp = t_icp[d_index-1:]
            if (len(icols_icp) == 1):
                icp = icp[d_index-1:]
            else:
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

    # Get different ICPs
    if (len(icols_icp) == 1):
        y_icp = np.interp(x_pots,t_icp_subset,icp_subset)
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
    xshift = x_pots + Dt[i]
    show_pots_icp(xshift,y_pots,y_icp,tini,prop_label,
                  prefixes[i],plot_format=plotformat)

    # Write output
    header1 = '# '+prefixes[i]+'\n' 
    tofile = np.array([])
    if (i==1):
        header2 = '# time,E,I,intensity,j \n'
        header3 = '# s,V,mA,counts,mA cm-2 \n'
        y_pots_area = y_pots/area
        tofile = np.column_stack((xshift,vv,y_pots,y_icp,y_pots_area))
    else:
        header2 = '# time,E,intensity \n'
        header3 = '# s,V,counts \n'
        tofile = np.column_stack((xshift,y_pots,y_icp))

    outfil = 'output/'+files[i]
    with open(outfil, 'w') as outf:
        outf.write(header1)
        outf.write(header2)
        outf.write(header3)
        np.savetxt(outf,tofile,fmt='%1.8e',delimiter=',')
    outf.closed
    print('Output file: {}'.format(outfil))

if (showplots): plt.show()
