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

def hist_limits(dat, nlims, symmetrical = True):
    nlims0 = nlims
    for p in range(0,100 - nlims0):
        nlims = nlims0 + p
        
        lims = np.percentile(dat.data[~np.isnan(dat.data)], range(0, 100, 100/nlims))
        #lims = lims[lims != -inf]
        if (lims[0]==-inf): lims.pop(0)
            
        lims = [to_precision(i, 2) for i in lims]
        lims = np.unique(lims)
        if (len(lims) >= nlims0): break
   
    if (lims[0] < 0.0):        
        if (sum(lims <0.0) > sum(lims >0.0)):
            lims = lims[lims < 0.0]
            lims = np.concatenate((lims,-lims[::-1]))  
        else:
            lims = lims[lims > 0.0]
            lims = np.concatenate((-lims[::-1],lims))     
        extend = 'both'
    else:
        extend = 'max'
    return (lims, extend)


def plot_cube(cube, Ns, N, cmap):
    if (Ns > 1): Ns = Ns -1
    plt.subplot(Ns, 2, N, projection=ccrs.Robinson())
    print cube.name()
    try:
        cube = cube.collapsed('time', iris.analysis.MEAN)
    except:
        cube = cube.collapsed('forecast_reference_time', iris.analysis.MEAN)
    
    cmap = plt.get_cmap(cmap)
    levels, extend = hist_limits(cube, 7)
    
    if (extend =='max'): 
        norm = BoundaryNorm(levels, ncolors=cmap.N - 1)
    else:
        norm = BoundaryNorm(levels, ncolors=cmap.N)

    qplt.contourf(cube, levels = levels, cmap = cmap, norm = norm, extend = extend)
    plt.gca().coastlines()


def plot_cubes_map(cubes, cmap, *args):
    nplots = len(cubes)
    for i in range(0, nplots - 1): 
        print i 
        
        if (type(cmap) is str): 
            plot_cube(cubes[i], nplots, i * 2 + 1, cmap, *args)
        else: 
            plot_cube(cubes[i], nplots, i * 2 + 1, cmap[i], *args)
    
    if (nplots == 1):
        i = -1
        p = 1
    else: p = 2
    if (type(cmap) is str):
        plot_cube(cubes[i + 1], nplots, p, cmap, *args)
    else:        
        plot_cube(cubes[i + 1], nplots, p, cmap[i+1], *args)


