import numpy as np
import scipy
import matplotlib.pyplot as plt
import os

def readlogfile(filename):
    Log={}
    line_number=0
    with open(filename) as file_in:
        for line in file_in:
            if line_number==0:
                properties=line.split()

                for oneproperty in properties:
                    Log[oneproperty]=[]
                line_number+=1
            else:

                content=line.split()
                #print(content)
                i=0
                while i<len(content):
                    Log[properties[i]].append(float(content[i]))
                    i+=1
    return Log

os.chdir('../simulations')
timestep=0.0005 # ps
for i in range(1,65):
    os.chdir('{}/'.format(i))
    print('current directory is {}'.format(i))

    a=readlogfile('log-output_nvt.log')

    a['time']=[x*timestep for x in a['timestep']]
    plt.plot(a['time'],a['temperature'])
    plt.ylim([1.3,1.6])
    plt.savefig('temperature.png')
    plt.close()
    plt.figure()
    a['time']=[x*timestep for x in a['timestep']]
    plt.plot(a['time'],a['pressure'])
    plt.ylim([125,200])
    plt.savefig('pressure.png')
    plt.close()
    plt.figure()
    a['time']=[x*timestep for x in a['timestep']]
    plt.plot(a['time'],a['potential_energy'])
    plt.ylim([-71000,-68000])
    plt.savefig('potential.png')
    plt.close()
    os.chdir('..')
#a=readlogfile('log-output_nvt.log',['kinetic_energy','potential_energy','temperature','pressure','pressure_xx', 'pressure_xy', 'pressure_xz', 'pressure_yy', 'pressure_yz', 'pressure_zz', 'lx','ly','lz'])
