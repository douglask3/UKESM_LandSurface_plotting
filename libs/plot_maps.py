import iris
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

def hist_limits(dat, lims = None, nlims = 5, symmetrical = True):
    if (lims is None):
        nlims0 = nlims
        for p in range(0,100 - nlims0):
            nlims = nlims0 + p
        
            lims = np.percentile(dat.data[~np.isnan(dat.data)], range(0, 100, 100/nlims))
            #lims = lims[lims != -inf]
            if (lims[0]==-inf): lims.pop(0)
            
            lims = [to_precision(i, 2) for i in lims]
            lims = np.unique(lims)
            if (len(lims) >= nlims0): break
        new_lims = True
    else:
        nlims = len(lims) + 1
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
    return (lims, extend)


def plot_cube(cube, N, M, n, levels = None, cmap = 'brewer_Greys_09'):
    
    plt.subplot(N, M, n, projection=ccrs.Robinson())
    print cube.name()
    try:
        cube = cube.collapsed('time', iris.analysis.MEAN)
    except:
        cube = cube.collapsed('forecast_reference_time', iris.analysis.MEAN)
    
    cmap = plt.get_cmap(cmap)   
    levels, extend = hist_limits(cube, levels, 7)
    
    if (extend =='max'): 
        norm = BoundaryNorm(levels, ncolors=cmap.N - 1)
    else:
        norm = BoundaryNorm(levels, ncolors=cmap.N)
    
    try:
        qplt.contourf(cube, levels = levels, cmap = cmap, norm = norm, extend = extend)
    except:
        qplt.contourf(cube, levels = levels, cmap = cmap, norm = norm)
    
    plt.gca().coastlines()
    

def plot_cubes_map(cubes, N, M, levels, cmap, *args):
    
    nplots = len(cubes) + 1
    if (type(cmap) is list and len(cmap) == 1): cmap = cmap[0]
    for i in range(0, nplots - 1):    
        cmapi   = cmap   if type(cmap)      is str   else cmap[i]
        levelsi = levels if type(levels[0]) is float else levels[i]
        
        plot_cube(cubes[i], N, M, i + 1, levelsi, cmapi   , *args)

    
