import iris
import iris.coord_categorisation

import numpy as np
import cartopy.crs as ccrs

import iris.plot as iplt
import iris.quickplot as qplt
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from to_precision import *
from pdb import set_trace as browser
from numpy import inf

class plot_cubes_map(object):

    def __init__(self, cubes, N, M, levels, cmap, *args, **kw):
        
        nplots = len(cubes) + 1
        if (type(cmap) is list and len(cmap) == 1): cmap = cmap[0]
        for i in range(0, nplots - 1):  
            if levels is not None:
                if type(levels) is list and len(levels) == 1 and levels[0] is None:
                    levelsi = None
                else:
                    levelsi = levels[i] if type(levels[0]) is list or levels[0] is  None else levels            
            else:
                levelsi = None        
            cmapi = cmap if type(cmap) is str else cmap[i]   
            
            self.plot_cube(cubes[i], N, M, i + 1, levelsi, cmapi, *args, **kw)


    def plot_cube(self, cube, N, M, n, levels = None, cmap = 'brewer_Greys_09', MapEndYrsN = None):
    
        if MapEndYrsN is not None:            
            try:
                iris.coord_categorisation.add_year(cube, 'time')
            except:
                pass
            try:
                self.endYr = cube.coord('year').points.max()
                self.startYr = self.endYr - MapEndYrsN
                def dateRange1(cell): return self.startYr <= cell
                def dateRange2(cell): return cell <= self.endYr
                #tConstraint = iris.Constraint(year = dateRange1)
                cube = cube[dateRange1(cube.coord('year').points)]
                cube = cube[dateRange2(cube.coord('year').points)]
                cube.var_name = cube.long_name = cube.var_name + '_' + str(self.startYr) + '-' + str(self.endYr)
            except:
                pass

        plt.subplot(N, M, n, projection=ccrs.Robinson())
        
        try: cube = cube.collapsed('time', iris.analysis.MEAN)
        except: pass
        if cube.ndim == 3:
            try:
                cube[0].data = np.nanmean(cube.data, 0)
            except:
                browser()
            cube = cube[0]
        
        try:
            cmap = plt.get_cmap(cmap)   
        except:
            cmap = plt.get_cmap(cmap[0])
        levels, extend = self.hist_limits(cube, levels, 7)
    
        if extend =='max': 
            norm = BoundaryNorm(levels, ncolors=cmap.N - 1)
        else:
            norm = BoundaryNorm(levels, ncolors=cmap.N)
        
        try:
            qplt.contourf(cube, levels = levels, cmap = cmap, norm = norm, extend = extend)
        except:
            try:
                qplt.contourf(cube, levels = levels, cmap = cmap, norm = norm)
            except:
                qplt.pcolormesh(cube, cmap = cmap, norm = norm)
        plt.gca().coastlines()
    

    def hist_limits(self,dat, lims = None, nlims = 5, symmetrical = True):
        def select_lims(prec, nlims):
            nlims0 = nlims
            for p in range(0,100 - nlims0):
                nlims = nlims0 + p
                lims  = np.percentile(dat.data[~np.isnan(dat.data)], range(0, 100, 100/nlims))
            
                if (lims[0]==-inf): lims.pop(0)
            
                lims = [to_precision(i, prec) for i in lims]
                lims = np.unique(lims)
                if (len(lims) >= nlims0): break
            return lims
        if (lims is None):
            for prec in range(1,5):
                lims = select_lims(prec, nlims)
                if len(lims) > 3: break

            new_lims = True
        else:
            new_lims = False
        if (lims[0] < 0.0):
            if (new_lims): 
                # are the more levels less than zero or gt  then zero  
                if (sum(i < 0.0 for i in lims) > sum(i > 0.0 for i  in lims)):
                    # if more gt zero
                    lims = [i for i in lims if i < 0.0]
                    lims = np.concatenate((lims,[-i for i in lims[::-1]]))  

                else:
                    # if more lt zero
                    lims = [i for i in lims if i > 0.0]
                    lims = np.concatenate(([-i for i in lims[::-1]], lims))     
            extend = 'both'
        
        else:
            extend = 'max'

        if len(lims) == 1: 
            lims = [-0.0001, -0.000001, 0.000001, 0.0001] if lims == 0.0 else [lims[0] * (1 + i) for i in [-0.1, -0.01, 0.01, 0.1]]
            extend = 'neither'

        if np.log10(lims[0]/lims[1]) > 3: lims[0] = 1000 * lims[1]
        if np.log10(lims[-1] / lims[-2]) > 3: lims[-1] = 1000 * lims[-2]
        if len(lims) < 4:
            lims = np.interp(np.arange(0, len(lims), len(lims)/6.0), range(0, len(lims)), lims)
    
        return (lims, extend)



