import iris
import numpy as np
import cartopy.crs as ccrs

import iris.plot as iplt
import matplotlib.pyplot as plt
from pdb import set_trace as browser


def grid_area(cube):
    if cube.coord('latitude').bounds is None:
        cube.coord('latitude').guess_bounds()
        cube.coord('longitude').guess_bounds()
    return iris.analysis.cartography.area_weights(cube)    

### Running mean/Moving average
def running_N_mean(l, N):
    sum = 0
    
    result = list( np.float('NAN') for x in l)
    
    for i in range( 0, N ):
        try:
            sum = sum + l[i]
        except:
            browser()
        #result[i] = sum / (i+1)

    for i in range( N, len(l) ):
        sum = sum - l[i-N] + l[i]
        result[i] = sum / N

    return result

def cube_TS(cube, running_mean = False, mean = False):
    cube.data =  np.ma.masked_invalid(cube.data)

    grid_areas = grid_area(cube)
    collapseFun = iris.analysis.MEAN if mean else iris.analysis.SUM
    cube = cube.collapsed(['latitude', 'longitude'], collapseFun, weights = grid_areas)
    
    if (running_mean): cube.data = running_N_mean(cube.data, 12)
    return cube   

def plot_cube_TS(cubes, running_mean, diff, mean, units):   
     
    cubes = [cube_TS(cube, running_mean, mean) for cube in cubes]   
        
    if units is None: units = [cubes[0].units if mean else ''] 

    index = [i.name()=='diff' for i in cubes]
    for cube, i in zip(cubes, index): 
        if not i: iplt.plot(cube, label = cube.name()) 
    
    ncol = min(4 * int(len(cubes)**0.5), len(cubes))
    plt.legend(loc = 'upper right', bbox_to_anchor = (0.5, -0.05),
               fancybox = True, shadow = True, ncol = ncol)

    if any(index) and diff:
        ax2 = plt.gca().twinx()
    
        for cube, i in zip(cubes, index): 
            if i: iplt.plot(cube, '-r', label = cube.name())   

        plt.legend(loc = 'upper left', bbox_to_anchor = (0.5, -0.05),
               fancybox = True, shadow = True)

    plt.grid(True)    
    plt.axis('tight')
    
    plt.gca().set_ylabel(units, fontsize=16)
