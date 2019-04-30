**cv_icp** This codes takes simultaneous measurements with different equipment that have different internal clocks and produce files and plots correcting for this. To run it:
 1. Copy the input files into the *inputdata* folder
 2. Modify the top of cv_icp.py with the adequate:
	- Names for the input files. 
	- Area (in cm2) for getting the current density, j.
	- The column with the ICP Steps.
	- The height fraction. This parameter is used to calculate the starting points of the ICP steps for the time correction. This fractions divides the height of the first ICP peak, removing the upper variations.
	- If the time correction is to be done manually.
	- If plots are to be shown while running the code.
	- Format of the output files.
 3. Run the python program, for example typing in the command line: '''python cv_icp.py'''
 4. Check the time correction by looking that the two pop-up figures make senss (set 'showplots=True'). These can be close clicking the cross on the right top corner.
 5. Find your output files and plots in the output folder.

**Dependencies**
This code was developed using python3.7.1 and it requires the use of numpy, pathlib, matplotlib. From the command line these can be installed with (changing *pathlib* by the adecuate package):
'''
python -m pip install pathlib
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
