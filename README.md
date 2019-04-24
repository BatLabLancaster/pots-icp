**cv_icp** This codes takes simultaneous measurements with different equipment that have different internal clocks and produce files and plots correcting for this. To run it:
 1. Copy the input files into the inputdata folder
 2. Modify the top of cv_icp.py with the adequate:
	- Names for the input files. 
	- Area (in cm2) for getting the current density, j.
	- If plots are to be shown while running the code.
	- Format of the output files.
 3. Run the python program, for example typing in the command line: '''python cv_icp.py'''
 4. Check the time correction by looking that the two pop-up figures make senss (set 'showplots=True'). These can be close clicking the cross on the right top corner.
 5. Find your output files and plots in the output folder.


**Repository Organization**

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
├── README.md
│
├── cv_icp.py          <- Code for simultaneous measurements
├── inputdata          <- Folder containing the input data (files here are NOT tracked by git)
├── output             <- Folder containing the output data and plots (files here are NOT tracked by git)
└── src                <- Folder with general functions used by main programs here.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
