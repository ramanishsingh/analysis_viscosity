# analysis_viscosity
This package calcuates viscosity from HOOMD log files. The main analysis code is taken from PyLat (https://github.com/MaginnGroup/PyLAT).

## How to use this package
Run the parameters_main.py to calculate viscosty for the log files stored in ../simulation/{$i} folder (the relative path can be changed).
Please check unit conversion in viscio.py (lines 100-115) and timestep (llog['timestep']). Default units are L:nm, E: kJ/mol, and Mass: au.


## Relevant papers
- https://pubs.acs.org/doi/abs/10.1021/acs.jcim.9b00066
- https://pubs.acs.org/doi/abs/10.1021/acs.jctc.5b00351
- https://pubs.acs.org/doi/pdf/10.1021/jp062885s

