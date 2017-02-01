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
    def __init__(self, files = None, dat = None, total = False, running_mean = False):   
        self.files = files
        self.dat   = dat
        self.total = total
        self.running_mean = running_mean  


    def load_group(self, codes, lbelvs, names, scale = None, **kw):
        dat = self.dat
        if (dat is None):
            if (len(codes) == 1): codes = [codes[0] for i in names]     
            dat = [load_stash(self.files, code, lbelv, name, **kw) for code, lbelv, name in zip(codes, lbelvs, names)]
        
        dat = [i for i in dat if i is not None]
        for i in range(0, len(dat)):
                if (dat[i].coords()[0].long_name == 'pseudo_level'):
                    print('warning: ' + names[i] + ' has pseudo_levels')
                    dat[i] = dat[i].collapsed('pseudo_level', iris.analysis.MEAN)             
        
        if (scale is not None):
            for i in range(0, len(dat)): 
                sc = scale[i] if scale is list else scale
                dat[i].data = dat[i].data * sc   
        
        if (self.total):
            tot = dat[0].copy()
            for i in dat[1:]: tot.data += i.data

            tot.var_name  = 'total'
            tot.long_name = 'total'   
            dat.append(tot)
        
        return dat


    def plot_cubes(self, cubes, figName, title, TSMean, *args):
        nplots = len(cubes)   
        
        if (nplots == 1):
            N = 2
            M = 1
            p = 2
        else:
            N = int(nplots**0.5) + 1
            M = round(nplots/float(N))
            p = 4
        plt.figure(figsize = (3 * N, 6 * M))
        plot_cubes_map(cubes, N, M, *args)        

        plt.subplot(N, 1, N)
        plot_cube_TS(cubes, self.running_mean, TSMean)      
    
        plt.gcf().suptitle(title, fontsize=18, fontweight='bold')

        git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
        plt.gcf().text(.05, .67, git, rotation = 90)

        figName = 'figs/' + figName + '.png'
        makeDir(figName)
        plt.savefig(figName, bbox_inches='tight')
 
    def open_plot_and_return(self, figName, title,
                             codes = None, lbelv = None, names = None,  units  = None,
                             TSMean = False,
                             cmap = 'brewer_Greys_09', **kw):
           
        dat = self.load_group(codes, lbelv, names, units = units, **kw)
        
        self.plot_cubes(dat, figName, title, TSMean, cmap)
        
        dat[-1].long_name = title
        if (self.total): return dat[-1]
 
