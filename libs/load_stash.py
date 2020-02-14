import iris
import iris.coord_categorisation
import sys
import warnings
import numpy as np
from pdb import set_trace as browser

class coordRangeExtract(object):
    def __init__(self, dat, lon = None, lat = None, point = None, point_as_ij = False):
        def coordRange2List(c, r):
            if c is not None:
                if  isinstance(c, list) and  len(c) == 1: c = c[0]
            return c    
        
        if point is not None and point != "" and point != [""]:
            latlon = point.split(';')  
            latlon = [i.split(':') for i in latlon]
            lon, lat = [[float(j) for j in i] for i in latlon]
            if point_as_ij:                
                lon = dat.coord('longitude').points[lon][0]
                lat = dat.coord('latitude' ).points[lat][0]
                dat.long_name += '-' + 'ijs:'
            dat.long_name += '-' + point
       
        self.lon = coordRange2List(lon, [-180, 180])
        self.lat = coordRange2List(lat, [-90 ,  90])

        if isinstance(self.lon, list):
            def lonRange(cell): return self.lon[0] <= cell <= self.lon[1]
        else:
            def lonRange(cell): return cell == self.lon

        if isinstance(self.lat, list):
            def latRange(cell): return self.lat[0] <= cell <= self.lat[1]
        else:
            def latRange(cell): return cell == self.lat

        try: dat.coord('latitude' ).guess_bounds()
        except: pass
        try: dat.coord('longitude').guess_bounds() 
        except: pass
        
        if self.lon is not None: dat = dat.extract(iris.Constraint(longitude = lonRange))
        if self.lat is not None: dat = dat.extract(iris.Constraint(latitude  = latRange))
        try:
            if self.lat[0] == self.lat[1] and self.lon[0] == self.lon[1]:
                if dat.coord('latitude').shape != (1,) or dat.coord('longitude').shape != (1,):
                    dat = [i.collapsed(['latitude', 'longitude'], iris.analysis.MEAN) for i in dat]
        except:
            pass
        self.dat = dat

class load_stash(object):

    def __init__(self, files, code, lbelvs, lbelvCoord, soillvs, name, units = None,
                 change = False, accumulate = False, months = None, climatology = False,
                 lon = None, lat = None, point = None, point_as_ij = False):
       
        self.dat = self.stash_code(files, code)
        
        if self.dat is not None:
            if months is not None: self.extractMonths(months)
            elif climatology: self.convert2Climatology()
            if soillvs is not None:
                if isinstance(soillvs, int): self.dat = self.stash_levels(soillvs, 'soil_model_level_number')
                else: self.dat = [self.stash_levels(soillv, 'soil_model_level_number') for soillv in soillvs]
            if lbelvs is not None:
                self.dat = [self.stash_levels(lbelv, lbelvCoord) for lbelv in lbelvs]
                if len(lbelvs) == 1: self.dat = self.dat[0]
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
            
            if isinstance(self.dat, list):     
                self.dat = [coordRangeExtract(i, lon, lat, point, point_as_ij).dat for i in self.dat]
            else:
                try:
                    self.dat = coordRangeExtract(self.dat, lon, lat, point, point_as_ij).dat
                except:
                    browser()

                
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

    def stash_levels(self, lbelv, coord = 'pseudo_level'):
        #browser()
        if coord is None:  coord = 'pseudo_level'   
        if coord == 'pseudo_level':
            index = np.where(self.dat.coord(coord).points == lbelv)[0]
            try:
                cube  = self.dat[index][0]
            except:
                browser()

        elif coord == 'soil_model_level_number':
            cube = self.dat.extract(iris.Constraint(soil_model_level_number = 3))

        elif coord == 'pressure':
            index = np.abs(self.dat.coord(coord).points - lbelv)
            index = np.where(index == index.min())[0][0]
            index = self.dat.coord(coord).points[index]
            cube = self.dat.extract(iris.Constraint(pressure = index))
            
        return cube



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
        start = np.where(self.dat.coord('month').points == 'Jan')[0][0]
        end   = np.where(self.dat.coord('month').points == 'Dec')[0][-1]
        end   = end + 1
        self.dat = self.dat[start:end]
        
        self.dat = self.dat.aggregated_by('month', iris.analysis.MEAN)
        self.dat.remove_coord('month')
     
