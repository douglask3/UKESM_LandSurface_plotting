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

            tot.var_name  = 'total'
            tot.long_name = 'total'   
            dat.append(tot)

        elif (diff and len(dat) == 2):
            try:       
                nt = min(dat[0].shape[0], dat[1].shape[0])

                dat[0] = dat[0][0:nt]
                dat[1] = dat[1][0:nt]
            
                diff = dat[1].copy() 
                diff = diff - dat[0]

                diff.var_name = diff.long_name = 'difference'
                dat.append(diff)
            except:
                warnings.warn('unable to calculate difference between cubes')

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
            plt.figure(figsize = (24 + max(0, (N - 3)/2),  12 + max(0, (M - 3)/2)))
        else:
            plt.figure(figsize = (12,  12))
        return N, M

    def plot_cubes(self, figName, title,
                   TS = True, TSMean = False, TSUnits = None, running_mean= False,
                   levels = None, cmap = 'brewer_Greys_09', *args):    
        N, M = self.plot_setup(TS)
        
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
    
    def diff(self, opr):
        
        def diff_cube(cs1, cs2):
            if (cs1.ndim == 3 and cs2.ndim == 3):
                nt = min(cs1.shape[0], cs2.shape[1])
                cs1 = cs1[0:nt]
                cs2 = cs2[0:nt]
            cs1.data = cs1.data - cs2.data
            return cs1

        opr = opr.dat
        ncubes = min(len(self.dat), len(opr))

        cs1 = self.dat[0]
        cs2 = opr[0]
        
        self.dat = [diff_cube(self.dat[i], opr[i])for i in range(0, ncubes)] 

