"""
.. moduleauthor:: Violeta Gonzalez-Perez <violetagp@protonmail.com>
"""
import os
import numpy as np
import glob

def check_files(infiles):
    '''
    Check the existance of an array of files

    Args:
    files: string, list with files names (with paths)
    '''

    for ff in infiles:
        if not os.path.isfile(ff):
            print('STOP: file not found, \n {}'.format(ff)) ; exit()

    return

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


def joinCVfiles(overwrite=True):
    '''
    Join all the files CV_*_#.txt from the inputdata folder 
    into a single file

    Parameters:
    overwrite : boolean
       True to overwrite an existing file

    Return:
    cvnom : string
       Name of the output file
    '''

    inpath = 'inputdata/'

    # Find all the CV files
    files = glob.glob(inpath+'CV_*.txt') 
    nums = np.array([int(ff.split('_')[-1].split('.txt')[0]) for ff in files])
    isort = np.argsort(nums)
    
    # Check if any CV files are missing
    inarr = nums[isort] 
    narr = np.arange(inarr[0], inarr[-1]+1, 1, dtype=int)
    if (not np.array_equal(inarr,narr)):
        print('WARNING (joinCVfiles): there are missing CV files {}'.format(files))

    t0cv = files[isort[0]].split('CV_')[-1].split('_')[0]
    cvnom = 'CVall_'+t0cv+'.txt'
    cvfile = inpath+cvnom
    if (os.path.isfile(cvfile) and not overwrite):
        return
        
    # Write header in combined file
    with open(cvfile, 'w') as f:
        f.write("# Total time (s), Electrode_potential (V), Cell_Potential (V), I (A), Time (s), Cycle number \n")
        f.close
        
    # Add content from each CV file, following the isort order
    jj = 0 ; ndays = 0 ; tstart = 0.; first00 = True 
    for i in isort:
        ff = files[i]

        # Read the data
        ih = jumpheader(ff)
        time, ev, ucell, ia = np.loadtxt(ff, usecols=(0,1,2,3),
                          unpack=True, skiprows=ih)

        # Total time
        fft = ff.split('_')[1].split('_')[0]

        if (fft[:2] == '00' and first00):
            # Deal times passing midnight
            first00 = False
            ndays += 1
        elif (fft[:2] != '00'):
            first00 = True
            
        ffh = ndays*24 + float(fft[:2])
        ffsec = ffh*3600. + float(fft[2:4])*60. + float(fft[4:6])
        
        if (jj ==  0):
            totalt = time
            tstart = ffsec
        else:
            totalt = time + ffsec - tstart
            
        # Create an array with cycle number
        jj += 1  
        cycle = np.full(shape=len(time),fill_value=jj)

        tofile = np.column_stack((totalt,ev,ucell,ia,time,cycle))
        with open(cvfile,'a') as outf:
            np.savetxt(outf,tofile,fmt='%.10e %.5e %.5e %.5e %.5e %i')

    return cvnom


def read_columns(infile,columns,delimiter=None):
    '''
    Read the columns in a file

    Args:
    infile: string, name of file (with path)
    columns: integer or list of integers, position of the columns to be read
    delimiter: string, delimiter to be used when reading the file
    '''
    
    ih = jumpheader(infile) #; print('ih={}'.format(ih))
    if delimiter:
        values = np.loadtxt(infile, usecols= (columns),
                            unpack=True, skiprows=ih, delimiter=',')
    else:
        values = np.loadtxt(infile, usecols= (columns),
                            unpack=True, skiprows=ih)

    return values

def get_col_nom(infile,columns,delimiter=None):
    '''
    Read the names of the given columns in a file

    Args:
    infile: string, name of file (with path)
    columns: integer or list of integers, position of the columns to be read
    delimiter: string, delimiter to be used when reading the file
    '''

    colnames=[' ']*len(columns)

    ih = jumpheader(infile)

    with open(infile, 'r') as ff:
        ii = 0
        for line in ff:
            ii += 1
            if (ii == ih):
                head = line.rstrip().split(delimiter)
                break

    for ii,icol in enumerate(columns):
        colnames[ii] = head[icol]
    
    return colnames


def get_Dt(files):
    '''
    Get shift times to output continuous times
    across different output files

    Parameters:
    files : list of strings
       Names of files

    Return:
    Dt : numpy array of floats
       Shift times to be applied to output
    '''

    Dt0, Dt = [np.zeros(len(files)) for ii in range(2)]

    ndays = 0 ; first00 = True
    for ii, ff in enumerate(files[:-1]):
        # Check that the name format is the expected one
        try:
            tini = ff.split('_')[1].split('.txt')[0]
        except:
            return Dt0

        if (len(tini) != 6): return Dt0

        # Total time
        if (tini[:2] == '00' and first00):
            # Deal times passing midnight
            first00 = False
            ndays += 1
        elif (tini[:2] != '00'):
            first00 = True
            
        th = ndays*24 + float(tini[:2])
        tsec = th*3600. + float(tini[2:4])*60. + float(tini[4:6])

        if (ii == 0):
            t0pre = tsec
            Dt[0] = 0.
        else:
            Dt[ii] = tsec - t0pre

    return Dt
