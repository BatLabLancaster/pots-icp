"""A python module to correct the time drft from the ICP measurements.

.. moduleauthor:: Violeta Gonzalez-Perez <violegp@gmail.com>

"""

import numpy as np
import sys, os.path
from .io import jumpheader
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

coeff = 1.
dt = 120.

def icp_t_correction(steps_icp,steps_cv):
    # Check that the calibration files exist in the inputdata folder
    for steps_f in [steps_cv,steps_icp]:
        ff = 'inputdata/'+steps_f
        if not os.path.isfile(ff):
            print('STOP: file not found, \n {}'.format(ff)) ; sys.exit()

    # Read the potential step times
    ih = jumpheader('inputdata/'+steps_cv)
    ts_pots, i_pots = np.loadtxt('inputdata/'+steps_cv,
                       usecols= (0,3),unpack=True, skiprows=ih)

    # Read the ICP step times
    ih = jumpheader('inputdata/'+steps_icp)
    ts_icp, i_icp = np.loadtxt('inputdata/'+steps_icp, delimiter=',',
                        usecols= (0,2),unpack=True, skiprows=ih)
    ts_icp = ts_icp*60. # in seconds
    #i_icp = i_icp*coeff
    i_icp = (i_icp-min(i_icp))*max(i_pots)/max(i_icp)

    # Create a time array that starts in 180'' and
    # increases in steps of 120"
    xx_all = np.arange(180.,max(max(ts_pots),max(ts_icp)),dt)
    gt_pots = xx_all[:-1]
    gi_pots = np.interp(gt_pots, ts_pots, i_pots)

    # Set arrays for the ICP step starts
    gt_icp = np.zeros(shape=len(gt_pots))
    gi_icp = np.zeros(shape=len(gt_pots))

    # Find the maximum dt
    maxdt = np.max(np.diff(ts_icp))

    # Remove the ICP values below the minimum of ts_pots
    ind = np.where(ts_icp > min(ts_pots))
    ts_icp1 = ts_icp[ind] ; i_icp1 = i_icp[ind]

    # Assuming that the first pulse matches in time
    # find the height of this first pulse
    ind = np.where(ts_icp1 < ts_icp1[0]+dt)
    ts_icp2 = ts_icp1[ind] ; i_icp2 = i_icp1[ind]
    reduced_height = max(i_icp2) - (max(i_icp2)-min(i_icp2))/5.

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
        if (diff < maxdt):
            isubs = np.append(isubs,i_icp3[ii])
            tsubs = np.append(tsubs,ts_icp3[ii])
        else:
            # Obtain the derivatives to find changes in slope
            m = np.diff(isubs)/np.diff(tsubs)

            # Start of the step is considered to be the
            # last point with a negative slope
            ind = np.where(m<0.) #; print(np.shape(ind)[1]) 
            if (np.shape(ind)[1] > 0):
                indexes = np.squeeze(ind)
                index = indexes[-1]
                gt_icp[gjj] = tsubs[index]
                gi_icp[gjj] = isubs[index]
                if (gjj < len(gt_pots)-1):
                    gjj += 1
                else:
                    break
            
            # Reset the subset arrays
            isubs = np.array([]) ; tsubs = np.array([])

    plt.xlabel('time (s)') ; plt.ylabel('Current (arbitrary units)')
    plt.plot(ts_pots,i_pots,'k',label='Potentiostat')
    plt.plot(gt_pots,gi_pots,'ko',label='Pots Step start')
    plt.plot(ts_icp1,i_icp1,'r',label='ICP signal')
    plt.plot(ts_icp2,i_icp2,'g.',label='1st ICP peak')
    plt.plot(ts_icp3,i_icp3,'y.',label='ICP up to the 1st peak')
    plt.plot(gt_icp,gi_icp,'ro',label='ICP Step start')
    leg = plt.legend(loc=1) ; leg.draw_frame(False)
    plotfile = 'output/start_step.png'
    plt.savefig(plotfile)
    print('Plot with the start of the steps: {}'.format(plotfile))
    plt.show()

    # Fit a straight line to time(pots) vs time(ICP)
    # time(icp) = slope*time(pots) + zero
    fit, res, dum1, dum2, dum3 = np.polyfit(gt_pots,gt_icp,1,full=True)
    slope = fit[0] ; zero = fit[1] 

    # Plot set up
    fig = plt.figure(figsize=(8.,9.))
    gs = gridspec.GridSpec(4,1)
    gs.update(wspace=0., hspace=0.)
    xtit = 't_pots (s)'
    xmin = gt_pots[0] ; xmax = gt_pots[-1]
    axis_val = 200.
    
    # t/t vs t
    ind = np.where((gt_pots>0.) & (gt_icp>0.))
    ratioy = (slope*gt_pots[ind] + zero)/gt_icp[ind]
    ratiox = (gt_icp[ind]-zero)/slope/gt_pots[ind]

    ymin = min(min(ratiox),min(ratioy)) - np.mean(np.diff(ratiox))
    ymax = max(max(ratiox),max(ratioy)) + np.mean(np.diff(ratiox))

    axb = plt.subplot(gs[3,:])
    axb.set_autoscale_on(False) ; axb.minorticks_on()
    axb.set_xlim(xmin,xmax) ; axb.set_ylim(ymin,ymax)
    axb.set_xlabel(xtit) 
    ytit = 'Fit/value' ; axb.set_ylabel(ytit)

    axb.plot(gt_pots[ind],ratioy,'b-')
    axb.plot(gt_pots[ind],ratiox,'r--')
    
    # t vs t
    ymin = gt_icp[0] - (gt_icp[1]-gt_icp[0])
    ymax = gt_icp[-1] + (gt_icp[1]-gt_icp[0])

    ax = plt.subplot(gs[2,:],sharex=axb) 
    ytit = 't_icp (s)' ; ax.set_ylabel(ytit)
    ax.set_autoscale_on(False) ; ax.minorticks_on()
    ax.set_ylim(ymin,ymax) ; start, end = ax.get_xlim()
    ax.xaxis.set_ticks(np.arange(start, end, axis_val))
    ax.set_xticklabels([])
    
    ax.plot(gt_pots,gt_icp,'k.')
    ax.plot(gt_pots,gt_pots*slope + zero,'b-',label='y=x*slope+zero')
    ax.plot((gt_icp-zero)/slope,gt_icp,'r--',label='x=(y-zero)/slope')
    ax.text(gt_pots[0], gt_icp[-1]-0.05*(gt_icp[-1]-gt_icp[0]),
             'slope='+str(slope)+', zero='+str(zero))
                                                 
    leg = ax.legend(loc=4) ; leg.draw_frame(False)
                                                 
    # i vs t                                                 
    ymin = min(min(i_pots),min(i_icp)) -\
        max(np.mean(np.diff(i_pots)),np.mean(np.diff(i_icp)))
    ymax = max(max(i_pots),max(i_icp)) +\
        max(np.mean(np.diff(i_pots)),np.mean(np.diff(i_icp)))
    
    axs = plt.subplot(gs[:-2,:],sharex=axb) 
    ytit = 'Current (arbitrary units)' ; axs.set_ylabel(ytit)
    axs.set_autoscale_on(False) ; axs.minorticks_on()
    axs.set_ylim(ymin,ymax) ; start, end = axs.get_xlim()
    axs.xaxis.set_ticks(np.arange(start, end, axis_val))
    ax.set_xticklabels([])
    
    axs.plot(ts_pots,i_pots,'k',label='Potentiostat')
    axs.plot((ts_icp-zero)/slope,i_icp,'r',label='ICP corrected')

    leg = axs.legend(loc=1) ; leg.draw_frame(False)

    # Save plot
    prefix = steps_icp.split('.')[0]
    plotfile = 'output/'+prefix+'_times.png'
    fig.savefig(plotfile)
    print('Times plot: ',plotfile)
    plt.show()
    sys.exit()
    return slope,zero
