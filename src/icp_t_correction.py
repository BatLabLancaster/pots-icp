"""
.. moduleauthor:: Violeta Gonzalez-Perez <violetagp@protonmail.com>
"""
import numpy as np
import os.path
from .io import jumpheader
from .plotting import show_corrected_steps
import matplotlib.pyplot as plt

def get_start_step_pots(ts_icp,ts_pots,i_pots,tstart_pots,dt_pots):
    '''
    Create a time array that starts in tstart_pots and
    increases in steps of dt_pots. 
    '''
    xx_all = np.arange(tstart_pots,max(max(ts_pots),max(ts_icp)),dt_pots)
    gt_pots = xx_all[:-1]
    gi_pots = np.interp(gt_pots, ts_pots, i_pots)

    return gt_pots,gi_pots

def read_pots_steps(steps_pots,stepcol_pots):
    '''
    Read the potential step times and absolute currents
    '''
    # Check that the calibration file exists in the inputdata folder
    ff = 'inputdata/'+steps_pots
    if not os.path.isfile(ff):
        print('STOP: file not found, \n {}'.format(ff)) ; exit()
    
    ih = jumpheader('inputdata/'+steps_pots)
    ts_pots, i_pots = np.loadtxt('inputdata/'+steps_pots,
                       usecols= (0,stepcol_pots),
                                 unpack=True, skiprows=ih)
    i_pots = abs(i_pots) # Absolute current

    return ts_pots, i_pots

def read_icp_steps(steps_icp,icol_icp):
    '''
    Read the ICP step times (in s) and absolute currents
    '''
    # Check that the calibration file exists in the inputdata folder
    ff = 'inputdata/'+steps_icp
    if not os.path.isfile(ff):
        print('STOP: file not found, \n {}'.format(ff)) ; exit()

    # Read the ICP step times
    ih = jumpheader('inputdata/'+steps_icp)
    ts_icp, i_icp = np.loadtxt('inputdata/'+steps_icp, delimiter=',',
                        usecols= (0,icol_icp),unpack=True, skiprows=ih)
    ts_icp = ts_icp*60. # in seconds
    i_icp = abs(i_icp)  # Absolute current

    return ts_icp, i_icp

def get_start_step_icp(ts_pots,i_pots,ts_icp,i_icp,gt_pots,gi_pots,tstart_pots,dt_pots,height_fraction,prefix,plot_format='pdf'):
    '''
    Create a time array that starts in tstart_pots and
    increases in steps of dt_pots. 
    '''
    # Set arrays for the ICP step starts
    gt_icp = np.zeros(shape=len(gt_pots)) ; gt_icp.fill(-999.)
    gi_icp = np.zeros(shape=len(gt_pots)) ; gi_icp.fill(-999.)

    # Find the maximum dt
    maxdt = np.max(np.diff(ts_icp))

    # Remove the ICP values below the minimum of ts_pots
    ind = np.where(ts_icp > min(ts_pots))
    ts_icp1 = ts_icp[ind] ; i_icp1 = i_icp[ind]

    # Assuming that the first pulse matches in time
    # find the height of this first pulse
    ind = np.where(ts_icp1 < ts_icp1[0]+dt_pots)
    ts_icp2 = ts_icp1[ind] ; i_icp2 = i_icp1[ind]
    reduced_height = max(i_icp2) - (max(i_icp2)-min(i_icp2))/height_fraction

    # Cut all the data above half this peak
    # to remove dealing with the scatter of the peaks.
    ind = np.where(i_icp1 < reduced_height)
    ts_icp3 = ts_icp1[ind] ; i_icp3 = i_icp1[ind]

    # Work with the sub-sets before the peaks
    # to find the step start
    gjj = 0
    isubs = np.array([]) ; tsubs = np.array([])
    for ii, ts in enumerate(ts_icp3[:-1]):
        diff = ts_icp3[ii+1] - ts
        if (diff <= maxdt):
            isubs = np.append(isubs,i_icp3[ii])
            tsubs = np.append(tsubs,ts_icp3[ii])
        else:
            # Obtain the derivatives to find changes in slope
            m = np.diff(isubs)/np.diff(tsubs)

            # Start of the step is considered to be the
            # last point with a negative slope
            ind = np.where(m<0.) #; print(np.shape(ind)[1])
            if (np.shape(ind)[1] > 1):
                indexes = np.squeeze(ind)
                index = indexes[-1]

                gt_icp[gjj] = tsubs[index]
                gi_icp[gjj] = isubs[index]
                if (gjj < len(gt_pots)-1):
                    gjj += 1
                else:
                    break
            elif (np.shape(ind)[1] == 1): 
                index = ind[0][0]
                #here: unclear how to do this part
                gt_icp[gjj] = tsubs[index]
                gi_icp[gjj] = isubs[index]
                if (gjj < len(gt_pots)-1):
                    gjj += 1
                else:
                    break
            
            # Reset the subset arrays
            isubs = np.array([]) ; tsubs = np.array([])

    plt.figure()
    plt.xlabel('time (s)') ; plt.ylabel('Current (arbitrary units)')
    plt.plot(ts_pots,i_pots,'k',label='Potentiostat')
    plt.plot(gt_pots,gi_pots,'ko',label='Pots Step start')
    plt.plot(ts_icp1,i_icp1,'r',label='ICP signal')
    plt.plot(ts_icp2,i_icp2,'g.',label='1st ICP peak')
    plt.plot(ts_icp3,i_icp3,'y.',label='ICP up to the 1st peak')
    ind=np.where(gt_icp>-999.)
    plt.plot(gt_icp[ind],gi_icp[ind],'ro',label='ICP Step start')
    leg = plt.legend(loc=1) ; leg.draw_frame(False)

    plotfile = 'output/start_step_'+prefix+'.'+plot_format
    plt.savefig('output/start_step_'+prefix+'.'+plot_format) 
    print('Plot with the start of the steps: {}'.format(plotfile))

    return gt_icp,gi_icp
    
def icp_t_correction(steps_icp,steps_pots,stepcol_pots,icol_icp,tstart_pots,dt_pots,height_fraction,show_plots=True,plot_format='pdf'):
    '''
    Correct the time drift from the ICP measurements, by fitting to
    a straight line the start of a experiment using pulses (steps):
    t_icp = slope*t_pots + zero

    Arg:
    steps_icp: characters, the name of the ICP steps file
    steps_pots: characters, the name of the Potentiostat steps file
    stepcol_pots: integer, column with current steps
    icol_icp: integer, column with ICP steps
    tstart_pots: float, start time for Pots. Steps
    dt_pots: float, interval for Pots. Steps
    height_fraction: float, used in the time correction calculation
    show_plots: boolean, to show or not the time correction plots
    plot_format: characters, format for plots

    Return:
    slope: float, the slope of the best fit
    zero: float, the shift of the best fit
    '''

    # Prefix for plots
    prefix = steps_icp.split('.')[0]

    # Read the pots calibration
    ts_pots, i_pots= read_pots_steps(steps_pots,stepcol_pots)

    # Read the ICP calibration
    ts_icp, i_icp = read_icp_steps(steps_icp,icol_icp)

    # Normalize the ICP arbitrarily
    i_icp = (i_icp-min(i_icp))*max(i_pots)/max(i_icp)
    
    # Generate the start of the pots steps
    gt_pots,gi_pots = get_start_step_pots(ts_icp,ts_pots,i_pots,
                                          tstart_pots,dt_pots)

    # Generate the start of the ICP steps
    gt_icp,gi_icp = get_start_step_icp(ts_pots,i_pots,ts_icp,i_icp,
                                       gt_pots,gi_pots,
                                       tstart_pots,dt_pots,
                                       height_fraction,
                                       prefix,plot_format=plot_format)

    # Remove unassigned starting points
    ind=np.where(gt_icp>-999.)
    
    # Fit a straight line to time(pots) vs time(ICP)
    # time(icp) = slope*time(pots) + zero
    fit, res, dum1, dum2, dum3 = np.polyfit(gt_pots[ind],gt_icp[ind],1,full=True)
    slope = fit[0] ; zero = fit[1] 

    # Plot the corrected steps
    show_corrected_steps(slope,zero,gt_pots[ind],gt_icp[ind],ts_pots,ts_icp,i_pots,i_icp,prefix,plot_format='pdf')

    if show_plots: plt.show()
    
    return slope,zero


def icp_t_manual(steps_icp,steps_pots,stepcol_pots,icol_icp,tstart_pots,dt_pots,height_fraction,slope=0.7,zero=0.,show_plots=True,plot_format='pdf'):
    '''
    Manually correct the time drift from the ICP measurements, by using a
    defined straight line to fit the start of a experiment using pulses (steps):
    t_icp = slope*t_pots + zero

    Arg:
    steps_icp: characters, the name of the ICP steps file
    steps_pots: characters, the name of the Potentiostat steps file
    stepcol_pots: integer, column with current steps
    icol_icp: integer, column with ICP steps
    tstart_pots: float, start time for Pots. Steps
    dt_pots: float, interval for Pots. Steps
    height_fraction: float, used in the time correction calculation
    slope: float, slope to be used
    zero: float, zero point to be used
    show_plots: boolean, to show or not the time correction plots
    plot_format: characters, format for plots

    Return:
    Shows the correction if shows_plots=True

    '''
    
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
                                       prefix,plot_format=plot_format)
    ind=np.where(gt_icp>-999.)
    show_corrected_steps(slope,zero,gt_pots[ind],gt_icp[ind],
                         ts_pots,ts_icp,i_pots,i_icp,prefix,plot_format=plot_format)
    if (show_plots): plt.show()

    return slope,zero
