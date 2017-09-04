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
    def __init__(self, files = None, codes = None, lbelv = None, VarPlotN = None, names = None,
                 plotNames = None, lon = None, lat = None,
                 units  = None, dat = None, diff = False, ratio = False, total = False,  **kw):
        
        if (dat is None):
            dat      = self.load_group(files, codes, lbelv, VarPlotN, names,
                                       plotNames, diff, ratio, total, units = units, **kw)
        
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

   
    def load_group_cubes(self, files, codes, names, lbelvs, VarPlotN, plotNames,
                         change = False, accumulate = False, **kw):
        
        if len(files) == 1 and isinstance(files, list): files = files[0] 

        if len(change) == 1 and len(codes) > 1 : change = change * len(codes)
        if len(accumulate) == 1 and len(codes) > 1 : accumulate = accumulate * len(codes)
        
        if isinstance(files[0], str):
 
            if len(codes) == 1 and len(names) > 1 and lbelvs is not None: names = [names]
            dat = [load_stash(files, code, lbelvs, name, change = ch, accumulate = acc, **kw).dat for code, name, ch, acc in zip(codes, names, change, accumulate)]
            if len(codes) == 1 and lbelvs is not None: dat = dat[0]
        else:           
            dat = [load_stash(file, codes[0], lbelvs, name, change = change[0], accumulate = accumulate[0], **kw).dat for file, name in zip(files, names)]    

        if VarPlotN is not None:     
            nplts = max(VarPlotN)
            datOut = dat[0].copy()
            datOut.data[:] = 0.0
            datOut = [datOut.copy() for i in range(nplts)] 
            for pn, cube in zip(VarPlotN, dat):
                try: datOut[pn-1].data += cube.data
                except: pass
            
            if plotNames is None: plotNames = [str(i) for i in range(1, nplts + 1)]
            for cube, pname in zip(datOut, plotNames): cube.long_name = cube.var_name = pname
            dat = datOut

        dat = [i for i in dat if i is not None]
        
        return(dat)


    def load_group(self, files, codes, lbelvs, VarPlotN, names, plotNames,
                   diff = False, ratio = False, total = False, totalOnly = False, 
                   scale = None, **kw):
        
        dat = self.load_group_cubes(files, codes, names, lbelvs, VarPlotN, plotNames, **kw)
        
        for i in range(0, len(dat)):
            if (dat[i].coords()[0].long_name == 'pseudo_level'):
                print('warning: ' + names[i] + ' has pseudo_levels, which will be meaned')
                dat[i] = dat[i].collapsed('pseudo_level', iris.analysis.MEAN)             
        
        if (scale is not None):
            for i in range(0, len(dat)): 
                sc = scale[i] if type(scale) is list else scale
                dat[i].data = dat[i].data * sc   
        
        if total:
            times = dat[0].coord('time').points
            for i in dat[1:]: times = np.intersect1d(times, i.coord('time').points)
            dat = [i.extract(iris.Constraint(time = times)) for i in dat]
            
            tot = dat[0].copy()
            for i in dat[1:]: tot.data += i.data


            tot.var_name  = 'total'
            tot.long_name = 'total' 
            if totalOnly:
                dat = [tot]
            else:  
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
        try:
            plt.savefig(figName, bbox_inches='tight')
        except:
            browser()
        return self.dat
        
        plt.close()
    
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
