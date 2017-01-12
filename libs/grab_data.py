import os
from   pdb   import set_trace as browser

def makeDir(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def grab_data(job, stream, codes, dir = 'data/'):
    #remove m01, s and i from codes    
    codes = [i.replace('m01', '') for i in codes]   
    codes = [i.replace(  'i', '') for i in codes]   
    codes = [i.replace(  's', '') for i in codes]
    ## make filter
    filter = 'begin \n\t stash = ('    
    for i in codes: filter += i + ', '
    filter = filter[:-2]
    filter += ') \n end'
        
    
    fname = 'temp/filter.fl'
    makeDir(fname)
    file = open(fname, "w")
    file.write(filter)
    file.close()
    
    makeDir(dir) 
    os.system('moo select ' + fname + ' moose://crum/' + job + '/' + stream + '.pp/ ' + dir)
