import os

def makeDir(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def grab_data(job, stream, codes, dir = 'data/'):
    ## make filter
    filter = 'begin \n\t'
    for i in codes: filter += codes + ', '
    filter = '\n end'
    
    fname = 'temp/filter.fl'
    makeDir(fname)
    file = open(fname, "w")
    file.write(filter)
    file.close()
    
    os.system('moo select ' + fname + ' moose://crum/' + job + '/' + stream + '.pp/' + dir)
