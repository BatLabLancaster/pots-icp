"""
.. moduleauthor:: Violeta Gonzalez-Perez <violetagp@protonmail.com>
"""

def ind_val_leq(arr,val):
    '''
    Given an array, find the index of the last element such that:
    element <= val


    Arg:
    arr: float array
    val: float, the value to compare the array to

    Retrun:
    index: integer, index of the element
    '''

    # Check that value is within the array
    if (val < arr[0] or val > arr[-1]):
        print('STOP (src/indexes) \n value={} is outside the given array [{},...,{}]'.format(val,arr[0],arr[-1]))
        exit()
    elif (val == arr[0]):
        return 0
    elif (val == arr[len(arr)-1]):
        return len(arr)-1
    else:
        # Loop over the array
        for ii, iarr in enumerate(arr):
            if iarr > val:
                return ii-1


def get_icp_subsets(prefix,t1,t2,tshift,t_icp,icp,icpDim):
    '''
    Get the time and current potentiostat subsets 
    for each experiment phases

    Arg:
    prefix: string, name of the experimental phase
    t1: float, first time value of the experiment
    t2: float, last time value of the experiment
    tshift: float, start of phase within the global running time
    t_icp: np.array of floats, potentiostat times
    icp: np.array of floats, potentiostat currents
    icpDim: integer, dimension of the matrix with currents

    Return:
    t_icp_subset: np.array of floats, subset of potentiostat times
    icp_subset: np.array of floats, subset of potentiostat currents
    '''
    if (t1 > t_icp[-1]):
        print('WARNING (indexes.get_icp_subsets): Potentiostate times={} > {} (ICP range)'.format(prefix,t1,t_icp[-1]))
        return t_icp, icp
        
    # Find the indexes for the icp subset interpolation
    if(tshift<t_icp[0]):
        ind1 = 0
    else:
        ind1 = ind_val_leq(t_icp,tshift)
    if ind1>1: ind1 = ind1 - 1

    if(t2+tshift>t_icp[-1]):
        ind2 = len(t_icp)-1
    else:
        ind2 = ind_val_leq(t_icp,t2+tshift)
    if (ind2<len(t_icp)-2): ind2 = ind2 + 1
    
    # Define the ICP subset 
    t_icp_subset = t_icp[ind1:ind2+1]

    if (icpDim == 1):
        icp_subset= icp[ind1:ind2+1]
    else:
        icp_subset= icp[:,ind1:ind2+1]

    return t_icp_subset, icp_subset
        
