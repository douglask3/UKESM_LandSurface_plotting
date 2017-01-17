import iris
import sys
import warnings
from pdb import set_trace as browser

def load_stash(files, code, name, units = None):
    print name
    print code
    try:
        codeNum = int(code)
        if   (len(code) == 5): code = 'm01s' + code[0:2] + 'i' + code[2:]
        elif (len(code) == 7): code = 'm' + code[0:2] + 's' + code[2:4] + 'i' + code[4:]
    except:
        pass

    
    stash_constraint = iris.AttributeConstraint(STASH = code)
    
    try:
        cube = iris.load_cube(files, stash_constraint)
        cube.var_name = name
        cube.standard_name = None
        if (units is not None): cube.units = units
        return cube
    except:    
        warnings.warn('unable to open variable: ' + code)
        pass  
