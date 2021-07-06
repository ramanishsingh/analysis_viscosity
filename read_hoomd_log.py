import numpy

def readlogfile(filename,properties):
    Log={}
    with open(filename) as file_in:
        for line in file_in:
            content=line.split()
            print(content)
            i=0
            while i<len(content):
                Log[properties(i)].append(content[i])
    return Log


