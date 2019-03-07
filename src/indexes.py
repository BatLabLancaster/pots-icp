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
    if (val < arr[0] or val > arr[len(arr)-1]):
        print('STOP indexes.py \n value={} is outside the given array'.format(val))
    elif (val == arr[0]):
        return 0
    elif (val == arr[len(arr)-1]):
        return len(arr)-1
    else:
        # Loop over the array
        for ii, iarr in enumerate(arr):
            if iarr > val:
                return ii-1
        
