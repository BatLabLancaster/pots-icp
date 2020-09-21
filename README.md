**cv_icp.py** This codes takes simultaneous measurements with different equipment that have different internal clocks and produce files and plots correcting for this. To run it:
 1. Copy the input files into the *inputdata* folder
 2. Modify the top of cv_icp.py with the adequate:
	- steps_pots, ..., icp_file = Names for the input files.
	- If there are multiple CVfiles (multipleCVfiles=True) or just the input one.
	- area = Area (in cm2) for getting the current density, j.
	- stepcol_pots = The column number with the current steps.
	- icol_icp = The column number with the ICP steps.		
	- height_fraction = The height fraction. This parameter is used to calculate the starting points of the ICP steps for the time correction. This fractions divides the height of the first ICP peak, removing the upper variations. Vary this value if the red big dots in one of the Steps plots are not marking the beginning of the rise of the step for the ICP experiment.
	- correct_time_manually =If the time correction is to be done manually and the values to be used.
	- manual_slope = Value of the mannually set slope
	- manual_zero = Zero value for the mannually set time correction.	
	- showplots = If plots are to be shown while running the code.
	- plotformat = Format of the output files.
 3. Run the python program, for example typing in the command line: '''python3 cv_icp.py'''
 4. Check the time correction by looking that the two pop-up figures make senss (set 'showplots=True'). These can be close clicking the cross on the right top corner. Note that if the time correction has been done satisfactorly, the steps from the ICP will match reasonably well those from the potentiostat. If this does not happen, look to the initial step plots to see if the big red dots are not marking the beginning of the rise of the step, if this is the case, try to modify the parameter 'height_fraction', if problems still arise, correct the time manually.
 5. Find your output files and plots in the output folder.

**Dependencies**
This code was developed using python3.7.1 and it requires the use of numpy, matplotlib. From the command line these can be installed with (changing *numpy* by the adecuate package):
'''
python -m pip install numpy
'''

**Repository Organization**

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
├── README.md
│
├── cv_icp.py          <- Code for simultaneous measurements
├── inputdata          <- Folder containing the input data (files here are NOT tracked by git)
├── output             <- Folder containing the output data and plots (files here are NOT tracked by git)
└── src                <- Folder with functions used by main programs here.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
