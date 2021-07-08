from calcVisc import calcVisc
cv = calcVisc()
visc_dir = '../simulations/' #relative path of the simulations folder
visc_num = 35            # total number of independent simulations
visc_skip = 1e5        # Initial lines to be skipped in each trajectory log file i.e. eqlb period
visc_log = 'log-output_nvt.log'
verb = 65                    
output = {}
visc_samples = 25            # Number of trajectories to be included in each bootstrap
visc_num_boots = 7          # Number of bootstraps you want
visc_plot=True               
visc_guess = [1e-3,0.9,1e2,1e4] # Might need to change according to the fit

output = cv.calcvisc(visc_num,visc_skip,visc_dir,visc_log,output,verb,visc_samples,visc_num_boots,visc_plot,visc_guess)

print('Viscosity: {} plus or minus {} cP'.format(output["Viscosity"]["Average Value"],output["Viscosity"]["Standard Deviation"]))
