from calcVisc import calcVisc
cv = calcVisc()
visc_dir = '../simulations/'
visc_num = 56
visc_skip = 2000000/5
visc_log = 'log-output_nvt.log'
verb = 65
output = {}
visc_samples = 34
visc_num_boots = 12
visc_plot=True
visc_guess = [1e-3,0.9,1e2,1e3]

output = cv.calcvisc(visc_num,visc_skip,visc_dir,visc_log,output,verb,visc_samples,visc_num_boots,visc_plot,visc_guess)

print('Viscosity: {} plus or minus {} cP'.format(output["Viscosity"]["Average Value"],output["Viscosity"]["Standard Deviation"]))
