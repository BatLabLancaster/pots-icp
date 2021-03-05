"""
.. moduleauthor:: Violeta Gonzalez-Perez <violetagp@protonmail.com>
"""
import numpy as np
import sys
from .io import jumpheader
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

def show_corrected_steps(slope,zero,gt_pots,gt_icp,ts_pots,ts_icp,i_pots,i_icp,prefix,plot_format='pdf'):
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
    ax.text(gt_pots[0]+0.05*(gt_pots[-1]-gt_pots[0]),
            gt_icp[-1]-0.05*(gt_icp[-1]-gt_icp[0]),
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

    leg = axs.legend(loc=0) ; leg.draw_frame(False)

    # Save plot
    plotfile = 'output/'+'times_'+prefix+'.'+plot_format
    fig.savefig(plotfile)
    print('Time correction plot: {} \n'.format(plotfile))

    return


def show_pots_icp(xx,y_pots,iny_icp,tini,prop_label,prefix,
                  plot_format='pdf',icplabels=None):
    
    # Plot set up
    fig, ax1 = plt.subplots()
    
    ax2 = ax1.twinx()
    ax1.plot(xx, y_pots, 'k--', label='Pots')
    
    if (np.ndim(iny_icp) == 1):
        y_icp = iny_icp
        ax2.plot(xx, y_icp,label='ICP')
    else:
        for ii in range(np.shape(iny_icp)[1]):
            y_icp = iny_icp[:,ii]
            ax2.plot(xx, y_icp,label=icplabels[ii])

    ax1.set_xlabel('time (s, '+prefix+')')
    ax1.set_ylabel(prop_label, color='k')
    ax2.set_ylabel('ICP', color='b')

    plt.legend(loc=0)
    
    plotfile = 'output/'+prefix+'.'+plot_format
    fig.savefig(plotfile,bbox_inches='tight')
    print('Output plot: ',plotfile)

    return 
    
