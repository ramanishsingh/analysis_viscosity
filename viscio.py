#!/usr/bin/env python

"""
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

import re
import numpy as np
from multiprocessing import Pool
from scipy.integrate import cumtrapz

def _list2float(seq):
    for x in seq:
        try:
            yield float(x)
        except ValueError:
            yield x

def autocorrelate (a):
    b=np.concatenate((a,np.zeros(len(a))),axis=0)
    c= np.fft.ifft(np.fft.fft(b)*np.conjugate(np.fft.fft(b))).real
    d=c[:int(len(c)/2)]
    d=d/(np.array(range(len(a)))+1)[::-1]
    return d


class HoomdLog():
    """
    Parser for LAMMPS log file (parse function).
    Saves the output properties (log file) in the form of a dictionary (LOG) with the key being
    the LAMMPS output property (see 'thermo_style custom' command in the LAMMPS documentation).
    For example, LOG['temp'] will return the temperature data array in the log file.
    """

    def __init__(self, llog, avgs=None):
        """
        Args:
            llog:
                Dictionary of lamps log
            avgs:
                Dictionary of averages, will be generated automatically if unspecified
        """

        self.llog = llog  # Dictionary LOG has all the output property data as numpy 1D arrays with the property name as the key

        if avgs:
            self.avgs = avgs  # Dictionary of averages for storage / query
        else:
            self.avgs = {}
            # calculate the average
            for key in self.llog.keys():
                self.avgs[str(key)] = np.mean(self.llog[key])

    @classmethod
    def from_file(cls, filename):
        """
        Parses the log file. 
        """
        md = 0  # To avoid reading the minimization data steps
        header = 0
        footer_blank_line = 0
        llog = {}
        llog['timestep']=1 # fs

        with open(filename) as logfile:
            for line in logfile:
                properties=line.split()
                break
            properties[0]='step'
            raw_data = []
            for line in logfile:
                if all(isinstance(x, float) for x in list(_list2float(line.split()))) and len(line)>=3:
                    raw_data.append(line.split())
                else:
                    break
                #if line == '\n':
                    #footer_blank_line += 1
            #print int(md_step/log_save_freq)

            #if total_lines >= header + md_step/log_save_freq:
            	#rawdata = np.genfromtxt(fname=filename,dtype=float,skip_header=header,skip_footer=int(total_lines-header-md_step/log_save_freq-1 )-footer_blank_line)

            #else:
                #rawdata = np.genfromtxt(fname=filename,dtype=float,skip_header=header,skip_footer=1)
            rawdata = np.array(raw_data,np.float)
            for column, property in enumerate(properties):
                llog[property] = rawdata[:, column]
            #converting units to lammps units https://docs.lammps.org/units.html
            # lammps has P in atm, and length in Angstrom
            # hoomd has P in 
            llog['pressure']= llog['pressure']/(6.02214076*1e-7*101325)
            
            llog['pressure_xx']= llog['pressure_xx']/(6.02214076*1e-7*101325)
            llog['pressure_xy']= llog['pressure_xy']/(6.02214076*1e-7*101325)
            llog['pressure_xz']= llog['pressure_xz']/(6.02214076*1e-7*101325)
            llog['pressure_yy']= llog['pressure_yy']/(6.02214076*1e-7*101325)
            llog['pressure_yz']= llog['pressure_yz']/(6.02214076*1e-7*101325)
            llog['pressure_zz']= llog['pressure_zz']/(6.02214076*1e-7*101325)
            llog['lx']=llog['lx']*10
            llog['temperature']=llog['temperature']/0.0083144626181532
            llog['vol']=llog['lx']**3
           
            return HoomdLog(llog)

    def list_properties(self):
        """
        print the list of properties
        """
        print(log.llog.keys())


    # viscosity
    def viscosity(self,cutoff):

        """
            cutoff: initial lines ignored during the calculation
            output: returns arrays for the time and the integration which is 
                    the viscosity in cP
        """

        NCORES=1
        p=Pool(NCORES)

        numtimesteps = len(self.llog['pressure_xy'])
        calcsteps = np.floor((numtimesteps-cutoff)/10000)*10000
        cutoff = int(numtimesteps - calcsteps)
        a1=self.llog['pressure_xy'][cutoff:]
        a2=self.llog['pressure_xz'][cutoff:]
        a3=self.llog['pressure_yz'][cutoff:]
        a4=self.llog['pressure_xx'][cutoff:]-self.llog['pressure_yy'][cutoff:]
        a5=self.llog['pressure_yy'][cutoff:]-self.llog['pressure_zz'][cutoff:]
        a6=self.llog['pressure_xx'][cutoff:]-self.llog['pressure_zz'][cutoff:]
        array_array=[a1,a2,a3,a4,a5,a6]
        pv=p.map(autocorrelate,array_array)
        pcorr = (pv[0]+pv[1]+pv[2])/6+(pv[3]+pv[4]+pv[5])/24
   	 
        temp=np.mean(self.llog['temperature'][cutoff:])
       
        visco = (cumtrapz(pcorr,self.llog['step'][:len(pcorr)]))*self.llog['timestep']*10**-15*1000*101325.**2*self.llog['vol'][-1]*10**-30/(1.38*10**-23*temp)
        Time = np.array(self.llog['step'][:len(pcorr)-1])*self.llog['timestep']
        p.close()
        return (Time,visco)

    @property
    def as_dict(self):
        return {"@module": self.__class__.__module__,
                "@class": self.__class__.__name__,
                "llog": self.llog,
                "avgs": self.avgs}

    @classmethod
    def from_dict(cls, d):
        return HoomdLog(d['llog'], d['avgs'])


if __name__ == '__main__':
    filename = 'visc.log'
    log = HoomdLog.from_file(filename)
    log.viscosity(100001)
