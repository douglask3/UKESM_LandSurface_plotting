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


    def plot_cubes(self, cubes, title, TSMean, *args):
        nplots = len(cubes) 
        plot_cubes_map(cubes, *args)  
        
        if (nplots == 1):
            N = 1
            p = 2
        else:
            N = nplots 
            p = 4
        plt.subplot(max([1, nplots]), 2, 2)
        plot_cube_TS(cubes, self.running_mean, TSMean)      
    
        plt.gcf().suptitle(title, fontsize=18, fontweight='bold')
 
    def open_plot_and_return(self, figName, title,
                             codes = None, lbelv = None, names = None,  units  = None,
                             TSMean = False,
                             cmap = 'brewer_Greys_09', **kw):
    
        fig_name = 'figs/' + figName + '.pdf'
        makeDir(fig_name)
        git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
           
        dat = self.load_group(codes, lbelv, names, units = units, **kw)
        
        plt.figure(figsize = (15, 5 * max([1, len(dat) - 1])))
        self.plot_cubes(dat, title, TSMean, cmap)

        plt.gcf().text(.05, .95, git, rotation = 90)
        plt.savefig(fig_name, bbox_inches='tight')
    
        dat[-1].long_name = title
    
        if (self.total): return dat[-1]
 
