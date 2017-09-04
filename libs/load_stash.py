import iris
import iris.coord_categorisation
import sys
import warnings
import numpy as np
from pdb import set_trace as browser


class load_stash(object):

    def extractMonths(self, months):
        iris.coord_categorisation.add_month(self.dat, 'time')
        iris.coord_categorisation.add_year(self.dat, 'time')

        if months == 'winter':
            tConstraint = iris.Constraint(month=lambda cell: cell.point=='Dec' or cell.point == 'Jan' or cell.point == 'Feb')
        elif months == 'spring':
            tConstraint = iris.Constraint(month=lambda cell: cell.point=='Mar' or cell.point == 'Apr' or cell.point == 'May')       
        elif months == 'summmer':
            tConstraint = iris.Constraint(month=lambda cell: cell.point=='Jun' or cell.point == 'Jul' or cell.point == 'Aug')         
        elif months == 'autumn':
            tConstraint = iris.Constraint(month=lambda cell: cell.point=='Set' or cell.point == 'Oct' or cell.point == 'Nov')    

        self.dat = self.dat.extract(tConstraint)
        self.dat = self.dat.aggregated_by('year', iris.analysis.MEAN)
        self.dat.remove_coord('year')
        self.dat.remove_coord('month')

    def convert2Climatology(self):
        iris.coord_categorisation.add_month(self.dat, 'time')
        self.dat = self.dat.aggregated_by('month', iris.analysis.MEAN)
        self.dat.remove_coord('month')

    def __init__(self, files, code, lbelvs, name, units = None,
                 change = False, accumulate = False, months = None, climatology = False):
        
        self.dat = self.stash_code(files, code)
        
        if self.dat is not None:
            if months is not None: self.extractMonths(months)
            elif climatology: self.convert2Climatology()

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
        
            if accumulate:
                self.dat.data[0] = 0.0
                for t in range(1, self.dat.shape[0]): self.dat.data[t] += self.dat.data[t-1]
            
            if change:
                varname  = self.dat.var_name
                longname = self.dat.long_name
                self.dat -= self.dat[0]                
                self.dat = self.dat[1:]
                self.dat.var_name  = varname
                self.dat.long_name = longname
                
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
            try: 
                cube = iris.load(files, stash_constraint)[0]
                return cube
            except:
                warnings.warn('unable to open variable: ' + code)
                pass 

    def stash_levels(self, lbelv):
        print(lbelv)
        index = np.where(self.dat.coord('pseudo_level').points == lbelv)[0]
        try:
            cube  = self.dat[index][0]
        except:
            browser()
        return cube
     
