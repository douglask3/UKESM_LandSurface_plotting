import libs.import_iris #comment out this line if not run on CEH linux box
import iris

from   pylab import sort      
import matplotlib.pyplot as plt

from   libs              import git_info
from   libs.plot_maps    import *
from   libs.plot_TS      import *
from   libs.listdir_path import *
from   libs.load_stash   import *

from   pdb   import set_trace as browser

#############################################################################
## Funs                                                                    ##
#############################################################################

class open_plot_return(object):
    def __init__(self, files = None, dat = None, running_mean = False):   
        self.files = files
        self.dat   = dat
        self.running_mean = running_mean


    def load_group(self, codes, names, scale = None, **kw):
        dat = self.dat
        if (dat is None):        
            dat = [load_stash(self.files, code, name, **kw) for code, name in zip(codes, names)]
        
        for i in range(0, len(dat)):
                if (dat[i].coords()[0].long_name == 'pseudo_level'):
                    print('warning: ' + names[i] + ' has pseudo_levels')
                    dat[i] = dat[i].collapsed('pseudo_level', iris.analysis.MEAN)             
    
        if (scale is not None):
            for i in range(0, len(dat)):  dat[i].data = dat[i].data * scale[i]    
   
        tot = dat[0].copy()
        for i in dat[1:]: tot.data += i.data

        tot.var_name  = 'total'
        tot.long_name = 'total'   
        dat.append(tot)
    
        return dat


    def plot_cubes(self, cubes, title, *args):
        nplots = len(cubes)    
        plot_cubes_map(cubes, *args)  
    
        plt.subplot(nplots - 1, 2, 4)
        plot_cube_TS(cubes, self.running_mean)      
    
        plt.gcf().suptitle(title, fontsize=18, fontweight='bold')
 
    def open_plot_and_return(self, figName, title,
                             codes = None, names = None,  units  = None,
                             cmap = 'brewer_Greys_09', **kw):
    
        fig_name = '' + figName + '.pdf'
        git = 'repo: ' + git_info.url + '\n' + 'rev:  ' + git_info.rev
   
        dat = self.load_group(codes, names, units = units, **kw)
    
        plt.figure(figsize = (15, 5 * (len(dat) - 1)))
        self.plot_cubes(dat, title, cmap)

        plt.gcf().text(.05, .95, git, rotation = 90)
        plt.savefig(fig_name)
    
        dat[-1].long_name = title
    
        return dat[-1]

 
