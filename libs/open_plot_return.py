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
                 units  = None, dat = None, total = False, **kw): 
        if (dat is None):
            self.dat = self.load_group(files, codes, lbelv, names, total, units = units, **kw)
        else:
            self.dat = dat 


    def load_group(self, files, codes, lbelvs, names,total = False, scale = None, **kw):
        
        if (len(codes) == 1): codes = [codes[0] for i in names]     
        dat = [load_stash(files, code, lbelv, name, **kw) for code, lbelv, name in zip(codes, lbelvs, names)]
        
        dat = [i for i in dat if i is not None]
        for i in range(0, len(dat)):
                if (dat[i].coords()[0].long_name == 'pseudo_level'):
                    print('warning: ' + names[i] + ' has pseudo_levels')
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
        
        return dat
    
    def plot_setup(self):
        nplots = len(self.dat)
        
        if (nplots == 1):
            N = 2
            M = 1
        else:
            N = int(nplots**0.5)
            M = round(nplots/float(N))
            if ((N * M) < nplots): N = N + 1
            N = N + 1

        plt.figure(figsize = (4 * N, 4 * M))
        return N, M

    def plot_cubes(self, figName, title, TSMean = False, running_mean= False,
                   levels = None, cmap = 'brewer_Greys_09', *args):   
       
        N, M = self.plot_setup()
        
        plot_cubes_map(self.dat, N, M, levels, cmap = cmap, *args)        

        plt.subplot(N, 1, N)
        plot_cube_TS(self.dat, running_mean, TSMean)      
    
        plt.gcf().suptitle(title, fontsize=18, fontweight='bold')

        git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
        plt.gcf().text(.05, .67, git, rotation = 90)

        figName = 'figs/' + figName + '.png'
        makeDir(figName)
        plt.savefig(figName, bbox_inches='tight')

        return self.dat
 

