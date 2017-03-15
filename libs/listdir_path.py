import os

def listFiles(datD, Stream, files = None):
        
        datDirt = datD if Stream is None else datD + Stream + '/'        
	if files in None: 
            files = sort(listdir_path(datDirt))
        else:
            files.append(sort(listdir_path(datDirt)))
        return files


def listdir_path(path):    
    return [os.path.join(dp, f) for dp, dn, fn in os.walk(os.path.expanduser(path)) for f in fn]
    
