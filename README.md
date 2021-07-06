# analysis_viscosity
Calcuate viscosity from HOOMD log files. 
The main analysis code is taken from PyLat (https://github.com/MaginnGroup/PyLAT).
Run the parameters_main.py to calculate viscosty for the log files stored in ../simulation/{$i} folder (the relative path can be changed).
Please check unit conversion in viscio.py (lines 103-114). Default units are L:nm, E: kJ/mol, and Mass: au.

