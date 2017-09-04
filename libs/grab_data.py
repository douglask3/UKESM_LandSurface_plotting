import os
from   pdb   import set_trace as browser

def makeDir(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def grab_data(job, stream, codes, dir = None, startYr = None, endYr = None):
    #remove m01, s and i from codes    
    codes = [i.replace('m01', '') for i in codes]   
    codes = [i.replace(  'i', '') for i in codes]   
    codes = [i.replace(  's', '') for i in codes]
    
   
    filter = 'begin \n'
    if startYr is not None and endYr is not None:
        filter += 'year = [' + str(startYr) + '..' + str(endYr) + ']\n'
    filter += '\t stash = '
    if len(codes) != 1: filter += '('    
    for i in codes: filter += i + ', '
    filter = filter[:-2]
    if len(codes) != 1: filter += ')'
    filter += ' \n end'
    
    fname = 'temp/filter.fl'
    makeDir(fname)
    file = open(fname, "w")
    file.write(filter)
    file.close()
    
    if (not isinstance(stream, list)): stream = [stream]
    
    for st in stream:
        if (dir is None):
            dirt = 'data/' + job + '/' + st + '/'  
        else:
            dirt = dir + st + '/'
        os.system('rm -r ' + dirt)
        makeDir(dirt) 
        if (st[-5:] == '.file'): st = st + '/'
        else: st = st + '.pp/' 
        
        command = 'moo select ' + fname + ' moose://crum/' + job + '/' + st + ' ' + dirt
        print(command)
        os.system(command)
