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
    result = list( 0 for x in l)

    for i in range( 0, N ):
        sum = sum + l[i]
        result[i] = sum / (i+1)

    for i in range( N, len(l) ):
        sum = sum - l[i-N] + l[i]
        result[i] = sum / N

    return result

def cube_TS(cube, running_mean = False, mean = False):
    cube.data =  np.ma.masked_invalid(cube.data)

    grid_areas = grid_area(cube)
    collapseFun = iris.analysis.MEAN if mean else iris.analysis.SUM
    try: cube = cube.collapsed(['latitude', 'longitude'], collapseFun, weights = grid_areas)
    except: pass
    
    if (running_mean): cube.data = running_N_mean(cube.data, 12)
    return cube 

def plot_cube_360(cube, *args, **kw):
    try:
        iplt.plot(cube, *args, **kw) 
    except:
        try: iris.coord_categorisation.add_month(cube, 'time')
        except: pass
        try: iris.coord_categorisation.add_day_of_month(cube, 'time')
        except: pass
        day_test = cube.coord('day_of_month').points > 28
        feb_test = cube.coord('month').points == 'Feb'
        rm_test  = [not i or not j for i,j in zip(day_test, feb_test)]
        cube = cube[np.where(rm_test)]

        try:
            iplt.plot(cube, *args, **kw)        
        except:
            browser()

def plot_cube_TS(cubes, running_mean, mean, units):    
    cubes = [cube_TS(cube, running_mean, mean) for cube in cubes]   
        
    if units is None: units = [cubes[0].units if mean else ''] 
    #browser()
    index = ['diff' in i.name() for i in cubes]
    for cube, i in zip(cubes, index):       
        if not i: plot_cube_360(cube, label = cube.name())
         
    loc = 'upper right' if any(index) else 'center'
    ncol = min(4 * int(len(cubes)**0.5), len(cubes))
    plt.legend(loc = loc, bbox_to_anchor = (0.5, -0.05),
               fancybox = True, shadow = True, ncol = ncol)

    if any(index):
        ax2 = plt.gca().twinx()
    
        for cube, i in zip(cubes, index): 
            if i: plot_cube_360(cube, '-r', label = cube.name())   

        plt.legend(loc = 'upper left', bbox_to_anchor = (0.5, -0.05),
               fancybox = True, shadow = True)

    plt.grid(True)    
    plt.axis('tight')
    
    plt.gca().set_ylabel(units, fontsize=16)
