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
    cube = cube.collapsed(['latitude', 'longitude'], collapseFun, weights = grid_areas)
    
    if (running_mean): cube.data = running_N_mean(cube.data, 12)
    cube.units = 'g C'
    return cube   

def plot_cube_TS(cubes, running_mean, mean):    
    cubes = [cube_TS(cube, running_mean, mean) for cube in cubes]    
    
    for cube in cubes: iplt.plot(cube, label = cube.name())
    plt.ylabel('g C')
    
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=len(cubes))

    plt.grid(True)    
    plt.axis('tight')
    
    plt.gca().set_ylabel(cubes[0].units, fontsize=16)
