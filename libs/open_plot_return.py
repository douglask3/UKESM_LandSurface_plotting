import iris

from   pylab import sort      
import matplotlib.pyplot as plt

from   libs              import git_info
from   libs.plot_maps    import *
from   libs.plot_TS      import *
from   libs.listdir_path import *
from   libs.load_stash   import *
from   libs.grab_data    import makeDir

from   pdb   import set_trace as browser

#############################################################################
## Funs                                                                    ##
#############################################################################

class open_plot_return(object):
    def __init__(self, files = None, codes = None, lbelv = None, names = None,
                 lon = None, lat = None,
                 units  = None, dat = None, diff = False, total = False, ratio = False,  **kw):
        if (dat is None):
            dat = self.load_group(files, codes, lbelv, names, diff,
                                       total, ratio, units = units, **kw)
        
        
        def coordRange2List(c, r):
            if c is not None:
                if not isinstance(c, list) or len(c) == 1: c = [c, c]
            return c
                
        self.lon = coordRange2List(lon, [-180, 180])
        self.lat = coordRange2List(lat, [-90 ,  90])
        
        def lonRange(cell): return self.lon[0] <= cell <= self.lon[1]
        def latRange(cell): return self.lat[0] <= cell <= self.lat[1]

        if self.lon is not None: dat = [cube.extract(iris.Constraint(longitude = lonRange)) for cube in dat]
        if self.lat is not None: dat = [cube.extract(iris.Constraint(latitude  = latRange)) for cube in dat]
        
        self.dat = dat

    
    def load_group_cubes(self, files, codes, names, lbelvs, **kw):
        if (len(files) == 1 and isinstance(files, list)): files = files[0] 

        if isinstance(files[0], str):
            if len(codes) == 1 and len(names) > 1 and lbelvs is not None: names = [names]
            dat = [load_stash(files, code, lbelvs, name, **kw).dat for code, name in zip(codes, names)]
            if len(codes) == 1 and lbelvs is not None: dat = dat[0]
        else:            
            dat = [load_stash(file, codes[0], lbelvs, name, **kw).dat for file, name in zip(files, names)]
            
        dat = [i for i in dat if i is not None]
        return(dat)

    def load_group(self, files, codes, lbelvs, names,
                   diff = False, total = False, ratio = False, scale = None, **kw):
        
        dat = self.load_group_cubes(files, codes, names, lbelvs, **kw)
        
        for i in range(0, len(dat)):
            if (dat[i].coords()[0].long_name == 'pseudo_level'):
                print('warning: ' + names[i] + ' has pseudo_levels, which will be meaned')
                dat[i] = dat[i].collapsed('pseudo_level', iris.analysis.MEAN)             
        
        if (scale is not None):
            for i in range(0, len(dat)): 
                sc = scale[i] if scale is list else scale
                dat[i].data = dat[i].data * sc   
        
        if (total):
            tot = dat[0].copy()
            for i in dat[1:]: tot.data += i.data

            tot.var_name  = tot.long_name = 'total'   
            dat.append(tot)

        elif (diff and len(dat) == 2):
            try:                       
                dat = self.diff_cube(dat[0], dat[1])
                dat[2].var_name = dat[2].long_name = 'diff'
            except:
                warnings.warn('unable to calculate difference between cubes')
                browser()

        if ratio:
            rat = iris.analysis.maths.divide(dat[0], dat[1])
            rat.var_name = rat.long_name = 'ratio'
            dat.append(rat)

        return dat
    
    def plot_setup(self, TS):
        nplots = len(self.dat)
        
        if (nplots == 1):
            N = 1
            M = 1
        else:
            N = int(nplots**0.5)
            M = round(nplots/float(N))
            if ((N * M) < nplots): N = N + 1
            N = N
        
        if (TS): N = N + 1
        if (N > 1 and M > 1):
            plt.figure(figsize = (24 + max(0, (N - 3.0)/1.5),  12 + max(0, (M - 3.0)/2.0)))
        else:
            plt.figure(figsize = (12,  12))
        return N, M

    def plot_cubes(self, figName, title,
                   TS = True, TSMean = False, TSUnits = None, running_mean= False,
                   levels = None, cmap = 'brewer_Greys_09', *args):    
        N, M = self.plot_setup(TS)
        print figName
        plot_cubes_map(self.dat, N, M, levels, cmap = cmap, *args)        
    
        if (TS):
            plt.subplot(N, 1, N)
            plot_cube_TS(self.dat, running_mean, TSMean, TSUnits)      
    
        plt.gcf().suptitle(title, fontsize=18, fontweight='bold')

        git = 'rev:  ' + git_info.rev + '\n' + 'repo: ' + git_info.url
        plt.gcf().text(.05, .95, git, rotation = 270, verticalalignment = "top")

        figName = 'figs/' + figName + '.png'
        makeDir(figName)
        plt.savefig(figName, bbox_inches='tight')

        return self.dat
    
    def diff(self, opr, cubeN = None, names = None):
        
        if cubeN is not None:
            cs1 = self.dat[cubeN-1]
            cs2 =  opr.dat[cubeN-1]
            self.dat = self.diff_cube(cs1, cs2)
            
            if names is not None:
                names.append(names[0] + '-' + names[1])
                for i,j in zip(self.dat, names): i.var_name = i.long_name = j
        else:
            opr = opr.dat
            ncubes = min(len(self.dat), len(opr))

            cs1 = self.dat[0]
            cs2 = opr[0]
        
            self.dat = [self.diff_cube(self.dat[i], opr[i])[2] for i in range(0, ncubes)] 


    def diff_cube(self, cs1, cs2):
            if (cs1.ndim == 3 and cs2.ndim == 3):
                

                t1 = cs1.coord('time').points
                t2 = cs2.coord('time').points
                tmin = np.max([t1.min(), t2.min()])
                tmax = np.min([t1.max(), t2.max()])

                t = np.unique(np.append(t1, t2))
                t = t[t < tmax]
                t = t[t > tmin]

                cs1 = cs1.interpolate([('time', t)], iris.analysis.Linear())
                cs2 = cs2.interpolate([('time', t)], iris.analysis.Linear())

            cs3 = cs1.copy()
            cs3.data = cs1.data - cs2.data
            return [cs1, cs2, cs3]
