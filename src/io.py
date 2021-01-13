"""
.. moduleauthor:: Violeta Gonzalez-Perez <violetagp@protonmail.com>
"""
import os
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


def joinCVfiles(cvf_name,overwrite=True):
    '''
    Join all the files CV_*_#.txt from the inputdata folder 
    into a single file

    Parameters:
    cvf_name : string
       Name of the new single file
    overwrite : boolean
       True to overwrite an existing file
    '''

    inpath = 'inputdata/'
    cvfile = inpath+cvf_name
    if (os.path.isfile(cvfile) and not overwrite):
        return

    # Find all the CV files
    files = glob.glob(inpath+'CV_*.txt') 
    nums = np.array([int(ff.split('_')[-1].split('.txt')[0]) for ff in files])
    isort = np.argsort(nums)
    
    # Check if any CV files are missing
    inarr = nums[isort] 
    narr = np.arange(inarr[0], inarr[-1]+1, 1, dtype=int)
    if (not np.array_equal(inarr,narr)):
        print('WARNING (joinCVfiles): there are missing CV files {}'.format(files))

    # Write header in combined file
    with open(cvfile, 'w') as f:
        f.write("# Total time (s), Electrode_potential (V), Cell_Potential (V), I (A), Time (s), Cycle number \n")
        f.close
        
    # Add content from each CV file, following the isort order
    jj = 0 ; ndays = 0 ; tlast = 0.
    for i in isort:
        ff = files[i]
        fft = ff.split('_')[1].split('_')[0]
        ffh = ndays*24+float(fft[:2])
        
        ffsec = ffh*3600. + float(fft[2:4])*60. + float(fft[4:6])
        # What about experiments passing  midnight??
        ih = jumpheader(ff)
        time, ev, ucell, ia = np.loadtxt(ff, usecols=(0,1,2,3),
                          unpack=True, skiprows=ih)

        jj += 1
        cycle = np.full(shape=len(time),fill_value=jj)

        if (ff ==  0):
            totalt = time
        else:
            totalt = time + ffsec - tlast

        tlast = ffsec + time[-1]

        tofile = np.column_stack((totalt,ev,ucell,ia,time,cycle))
        with open(cvfile,'a') as outf:
            np.savetxt(outf,tofile,fmt='%.5e')

    return 
