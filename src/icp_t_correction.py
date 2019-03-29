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
    xx = xx_all[:-1]
    yy = np.interp(xx, ts_pots, i_pots)

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
    # Find the points of growth
    gt_icp = np.zeros(shape=len(xx))
    gi_icp = np.zeros(shape=len(xx))
    gjj = 0
    jj = 0 ; pval = i_icp3[jj]
    lastdiff = abs(i_icp3[1] - i_icp3[0])
    for j_icp in i_icp3:
        if ((j_icp - pval) > lastdiff):
           gt_icp[gjj] = ts_icp3[jj]
           gi_icp[gjj] = i_icp3[jj]
           if (gjj < len(xx)-1):
               gjj += 1
           else:
               break
           
        pval = j_icp
        jj += 1

    plt.plot(ts_pots,i_pots,'k')
    plt.plot(ts_icp1,i_icp1,'r.')
    plt.plot(ts_icp2,i_icp2,'g.')
    plt.plot(ts_icp3,i_icp3,'yx')
    plt.plot(gt_icp,gi_icp,'b.')
    plt.plot(xx,yy,'b.')
    plt.show()
    sys.exit()
    
    # Fit a straight line to time(pots) vs time(ICP)
    # time(icp) = slope*time(pots) + zero
    fit, res, dum1, dum2, dum3 = np.polyfit(xx,y_icp,1,full=True)
    slope = fit[0] ; zero = fit[1] 

    # Prefix = ICP file name
    prefix = steps_icp.split('.')[0]

    # Plot set up
    fig = plt.figure(figsize=(8.,9.))
    gs = gridspec.GridSpec(4,1)
    gs.update(wspace=0., hspace=0.)
    xtit = 't_pots (s)'
    xmin = xx[0] ; xmax = xx[-1]

    # t/t vs t
    ind = np.where((xx>0.) & (yy>0.))
    ratioy = (slope*xx[ind] + zero)/yy[ind]
    ratiox = (yy[ind]-zero)/slope/xx[ind]

    ymin = min(min(ratiox),min(ratioy)) - (ratiox[1]-ratiox[0])
    ymax = max(max(ratiox),max(ratioy)) + (ratiox[1]-ratiox[0])

    axb = plt.subplot(gs[3,:])
    axb.set_autoscale_on(False) ; axb.minorticks_on()
    axb.set_xlim(xmin,xmax) ; axb.set_ylim(ymin,ymax)
    axb.set_xlabel(xtit) 
    ytit = 'Fit/value' ; axb.set_ylabel(ytit)

    axb.plot(xx[ind],ratioy,color='b-')
    axb.plot(xx[ind],ratiox,color='r--')
    
    # t vs t
    ymin = yy[0] - (yy[1]-yy[0])
    ymax = yy[-1] + (yy[1]-yy[0])

    ax = plt.subplot(gs[:-1,:],sharex=axb) 
    ytit = 't_icp (s)' ; ax.set_ylabel(ytit)
    ax.set_autoscale_on(False) ; ax.minorticks_on()
    ax.set_ylim(ymin,ymax) ; start, end = ax.get_xlim()
    ax.xaxis.set_ticks(np.arange(start, end, 1.))

    ax.plot(xx,yy,'k.')
    ax.plot(xx,xx*slope + zero,'b-',label='y=x*slope+zero')
    ax.plot((yy-zero)/slope,yy,'r--',label='x=(y-zero)/slope')
    ax.text(xx[0], yy[-1]+0.05*(yy[-1]-yy[0]),
             'slope='+str(slope)+', zero='+str(zero))

    leg = ax.legend(loc=4) ; leg.draw_frame(False)

    # i vs t
    ymin = yy[0] - (yy[1]-yy[0])
    ymax = yy[-1] + (yy[1]-yy[0])

    ax = plt.subplot(gs[:-1,:],sharex=axb) 
    ytit = 't_icp (s)' ; ax.set_ylabel(ytit)
    ax.set_autoscale_on(False) ; ax.minorticks_on()
    ax.set_ylim(ymin,ymax) ; start, end = ax.get_xlim()
    ax.xaxis.set_ticks(np.arange(start, end, 1.))

    ax.plot(xx,yy,'k.')
    ax.plot(xx,xx*slope + zero,'b-',label='y=x*slope+zero')
    ax.plot((yy-zero)/slope,yy,'r--',label='x=(y-zero)/slope')
    ax.text(xx[0], yy[-1]+0.05*(yy[-1]-yy[0]),
             'slope='+str(slope)+', zero='+str(zero))

    leg = ax.legend(loc=4) ; leg.draw_frame(False)

    # Save plot
    plotfile = 'output/'+prefix+'_times.png'
    fig.savefig(plotfile)
    print('Times plot: ',plotfile)
    sys.exit()
    return slope,zero
