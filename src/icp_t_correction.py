import numpy as np
import sys, os.path
from .io import jumpheader
import matplotlib.pyplot as plt

def icp_t_correction(steps_icp,steps_pots):
    # Check that the calibration files exist in the inputdata folder
    for steps_f in [steps_pots,steps_icp]:
        ff = 'inputdata/'+steps_f
        if not os.path.isfile(ff):
            print('STOP: file not found, \n {}'.format(ff)) ; sys.exit()

    # Read the step times
    ih = jumpheader('inputdata/'+steps_pots)
    ts_pots = np.loadtxt('inputdata/'+steps_pots,
                         usecols= (0,),unpack=True, skiprows=ih)

    ih = jumpheader('inputdata/'+steps_icp)
    ts_icp = np.loadtxt('inputdata/'+steps_icp, delimiter=',',
                        usecols= (0,),unpack=True, skiprows=ih)
    ts_icp = ts_icp*60. # in seconds
    xx = ts_icp
    
    # Fit a straight line to time(pots) vs time(ICP)
    # time(pots) = fit_a*time(icp) + fit_b
    fit, res, dum1, dum2, dum3 = np.polyfit(xx,yy,1,full=True)
    slope = fit[0] ; zero = fit[1] 

    # Prefix
    prefix = steps_icp.split('.')[0]
    print(prefix) ; sys.exit()

    # Plot
    plt.plot(ts_icp,ts_pots,'o')
    plt.plot(ts_icp,fit_a*ts_icp + fit_b,'-')
    plt.xlabel('t_icp (s)') ; plt.ylabel('t_pots (s)')
    plt.text(ts_icp[0], ts_pots[-1], r'$residual=$'+res)
    plotfile = 'output/'+prefix+'_times.png'
    fig.savefig(plotfile)
    print('Times plot: ',plotfile)

    return slope,zero
