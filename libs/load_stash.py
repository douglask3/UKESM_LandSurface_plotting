import iris
import sys
import warnings
import numpy as np
from pdb import set_trace as browser


class load_stash(object):
    def __init__(self, files, code, lbelvs, name, units = None):
        
        self.dat = self.stash_code(files, code)
        
        if (self.dat is not None):
            if (lbelvs is not None):
                self.dat = [self.stash_levels(lbelv) for lbelv in lbelvs]
            #stick in function            
            if (isinstance(self.dat, list)):
                for i in range(0, len(self.dat)):
                    print "opening: " + name[i]
                    self.dat[i].var_name      = name[i]
                    self.dat[i].long_name     = name[i]
                    self.dat[i].standard_name = None
                    if (units is not None): self.dat[i].units = units
            else: 
                print "opening: " + name
                self.dat.var_name      = name
                self.dat.long_name     = name
                self.dat.standard_name = None
                if (units is not None): self.dat.units = units 

    def stash_code(self, files, code):    
        try:
            codeNum = int(code)
            if   (len(code) == 5): code = 'm01s' + code[0:2] + 'i' + code[2:]
            elif (len(code) == 7): code = 'm' + code[0:2] + 's' + code[2:4] + 'i' + code[4:]
        except:
            pass
       
        stash_constraint = iris.AttributeConstraint(STASH = code)    
        try:
            cube = iris.load(files, stash_constraint)
            if len(cube) > 1:
                warnings.warn('more then one instance of ' + 
                              code + ' available. Choosing one with shortest time dimension')
                nt = [i.coord('time').shape[0] for i in cube]
                nt = np.where(nt == np.min(nt))[0][0]
            else:
                nt = 0
            return cube[nt]
        except:    
            warnings.warn('unable to open variable: ' + code)
            pass 

    def stash_levels(self, lbelv):
        print(lbelv)
        index = np.where(self.dat.coord('pseudo_level').points == lbelv)[0]
        cube  = self.dat[index][0]

        return cube
     
