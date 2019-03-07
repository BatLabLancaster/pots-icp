**cv_icp** This codes takes simultaneous measurements with different equipment that have different internal clocks and produce files and plots correcting for this. To run it:
 1. Copy the input files into the inputdata folder
 2. Modify the names for the input files at the top of cv_icp.py
 3. Run the python program, for example typing in the command line: '''python cv_icp.py'''


**Repository Organization**

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
├── README.md
│
├── cv_icp.py          <- Code for simultaneous measurements
├── inputdata          <- Folder to contain the input data (files here are NOT tracked by git)
├── output             <- Folder to contain the output data and plots (files here are NOT tracked by git)
└── src                <- Folder with general functions used by main programs here.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


Three plots should be generated all of them with two Y-axis and a common time (x) axis. 
First plot 
* Pre OCV: 
Y-axis: Voltage [ column B (Ewe/V)  on file preoCV.txt] and ICP (Columm  C , Zn (213.857), on file ICP.csv)
x-axis: time/s
* CV: 
Y-axis: current [ column d (I/mA)  on file CV.txt] and ICP (Columm  C , Zn (213.857), on file ICP.csv)
x-axis: time/s
* Post OCV: 
Y-axis: current [ column B (Ewe/V)  on file postocV.txt] and ICP (Columm  C , Zn (213.857), on file ICP.csv)
x-axis: time/s
