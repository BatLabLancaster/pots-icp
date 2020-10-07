"""
.. moduleauthor:: Violeta Gonzalez-Perez <violetagp@protonmail.com>
"""
import numpy as np
import glob

def jumpheader(infile):
    '''
    Given a file with a structure: header+data, 
    counts the number of header lines

    Args:
    infile: string, input file

    Returns:
    ih: integer, number of lines with the header text
    '''
    ih = 0
    ff = open(infile,'r')
    for line in ff:
        if not line.strip():
            # Count any empty lines in theh header
            ih += 1
        else:
            # Check that the first character is not a digit
            char1 = line[0]
            if not char1.isdigit():
                ih += 1
            else:
                return ih
    return ih


def joinCVfiles():
    '''
    Join all the files CV_*_#.txt from the inputdata folder 
    into a single file

    Returns:
    cvfile : string
       Name of the new single file 
    '''
    cvfile = 'CVall.txt'
    
    files = glob.glob('inputdata/CV*.txt')
    nums = np.array([int(ff.split('_')[-1].split('.txt')[0]) for ff in files])
    isort = np.argsort(nums)

    # Check if any CV files are missing
    inarr = nums[isort]
    narr = np.arange(inarr[0], inarr[-1]+1, 1, dtype=int)
    if (not np.array_equal(inarr,narr)):
        print('WARNING (joinCVfiles): there are missing CV files {}'.format(files))

    # Add content from each CV file, followint the isort order
    for i in isort:
        ff = files[i]
        #here: read, deal with header, etc
        print(ff)
        
    return cvfile
