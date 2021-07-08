# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 09:16:20 2015
@author: mhumbert
PyLAT: Python LAMMPS Analysis Tools
Copyright (C) 2018  Michael Humbert, Yong Zhang and Ed Maginn
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import numpy as np
import sys
from random import randint

from fitVisc import fitVisc
from viscio import LammpsLog
import matplotlib
matplotlib.use('pdf')
import matplotlib.pyplot as plt


def reject_outliers(data, m=2):
    out=data[abs(data - np.mean(data)) < m * np.std(data)]
    print("In data was\n", data)
    print("Out data is \n",out)
    list1 = data.tolist() 
    list2 = out.tolist()
    thrown=list(set(list1).symmetric_difference(set(list2)))
    print('Rejected viscosity values are {}'.format(thrown))
    return data[abs(data - np.mean(data)) < m * np.std(data)]

class calcVisc:
   
 
    def calcvisc(self,numtrj,numskip,dirbase,logname,output,ver,numsamples,numboot,plot, popt2):
        '''
        
        Calculates average and standard deviation of the integral of the 
        pressure tensor autocorrelation function over numtrj lammps trajectories
        
        '''
        output['Viscosity']={}
        output['Viscosity']['Units']='cP'
        if dirbase==None:
            dirbase='./'
        filename=dirbase+'1/'+logname
        Log = LammpsLog.from_file(filename)
        print('comp is reading'+filename)
        (Time,visco)=Log.viscosity(numskip)
        print("Time after reading log")
        print(Time)
        print("visco after reading log")
        print(visco)
        trjlen = len(Time)
        viscosity = np.zeros((numtrj,trjlen))
        for i in range(0,len(visco)):
            viscosity[0][i] += visco[i]
        if ver>=1:
            sys.stdout.write('Viscosity Trajectory 1 of {} complete'.format(numtrj))
        
        
        for i in range(2,numtrj+1):
            filename=dirbase+str(i)+'/'+logname
            Log = LammpsLog.from_file(filename)
            (Time,visco)=Log.viscosity(numskip)
            if len(visco) < trjlen:
                trjlen = len(visco)
            for j in range(0,trjlen):
                viscosity[i-1][j] += visco[j]
            if ver>=1:
                sys.stdout.write('\rViscosity Trajectory {} of {} complete'.format(i,numtrj))
        if ver>=1:
            sys.stdout.write('\n')
        plt.figure()
        for i in range(0,numtrj):

            plt.plot(Time/1e5, viscosity[i][:], alpha=0.25)
        visc_mean=np.mean(viscosity,axis=0)
        plt.plot(Time/1e5, visc_mean,'k',label="mean of all trajs")
        plt.yticks(np.arange(-1, 1.2, 0.2))
        plt.legend()
        plt.grid()
        plt.ylabel('Viscosity (mPa*s)')
        plt.xlabel('Time (ns)')
        plt.savefig('allinone.pdf')
        plt.close()
        #Begin Bootstrapping for error estimate
        Values = []
        fv = fitVisc()
        print("viscosity is")
        print(viscosity)
        print("Time is")
        print(Time)
        for i in range(0,numboot):
            Values.append(self.Bootstrap(numsamples,trjlen,numtrj,viscosity,Time,fv,plot, popt2))
            if ver > 1:
                sys.stdout.write('\rViscosity Bootstrap {} of {} complete'.format(i+1,numboot))
        if ver > 1:
            sys.stdout.write('\n')
        Values=np.asarray(Values)
    #    Values=reject_outliers(Values)
        (ave,stddev,Values) = self.getAverage(Values,numsamples,trjlen,numtrj,viscosity,Time,fv)
        
        output['Viscosity']['Average Value'] = ave
        output['Viscosity']['Standard Deviation'] = stddev
        #output['Viscosity']['Average Integral']=average.tolist()
        #output['Viscosity']['Standard Deviation']=stddev.tolist()
        #output['Viscosity']['Time']=Time[:trjlen].tolist()
        
        return(output)
    
    def getAverage(self, Values,numsamples,trjlen,numtrj,viscosity,Time,fv):
        #calculate average and standard deviation of Values array
        #Was originally implemented to perform a z-test on the values to determine outliers
        ave = np.average(Values)
        stddev = np.std(Values)
        #maxval = np.max(Values)
        #minval = np.min(Values)
        #if ((maxval-ave)>(3*stddev)):
            #Values.remove(maxval)
            #print('{} removed from values'.format(maxval))
            #Values.append(self.Bootstrap(numsamples,trjlen,numtrj,viscosity,Time,fv))
            #(ave, stddev,Values) = self.getAverage(Values,numsamples,trjlen,numtrj,viscosity,Time,fv)
        #elif ((ave-minval)>(5*stddev)):
            #Values.remove(minval)
            #print('{} removed from values'.format(minval))
            #Values.append(self.Bootstrap(numsamples,trjlen,numtrj,viscosity,Time,fv))
            #(ave, stddev,Values) = self.getAverage(Values,numsamples,trjlen,numtrj,viscosity,Time,fv)
        return (ave,stddev,Values)
            

    def Bootstrap(self,numsamples,trjlen,numtrj,viscosity,Time,fv,plot,popt2):
        #Perform calculate the viscosity of one bootstrapping sample
        Bootlist = np.zeros((numsamples,trjlen))
        for j in range(0,numsamples):
            rint=randint(0,numtrj-1)
            print('trajectory {} is chosen'.format(rint))
            for k in range(0,trjlen):
                Bootlist[j][k] = viscosity[rint][k]
        
        average = np.zeros(trjlen)
        stddev = np.zeros(trjlen)

        for j in range(0,trjlen):
            average[j] = np.average(Bootlist.transpose()[j])
            stddev[j] = np.std(Bootlist.transpose()[j])
        Value = fv.fitvisc(Time,average,stddev,plot,popt2)
        plt.figure()
        plt.plot(Time, average)
        plt.plot(Time, stddev)
        plt.savefig("one_bootstrap.pdf")
        plt.close()
        return Value
