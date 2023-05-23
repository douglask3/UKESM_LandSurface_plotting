import configparser
import json
import sys

class ConfigGet(object):
    def __init__(self, fname):  
        self.Config = configparser.ConfigParser()
        self.Config.read(fname)
    
    def sections(self, *args, **kw):
        return self.Config.sections(*args, **kw)
        
    def List(self, section, field, type = '', asList = False, *arg):
        var = self.Config.get(section, field, *arg)
        var = [e.strip() for e in var.split(',')]

        ## replace with something shorter and cleverer
        if (type == 'float'  ): var = [float(i) for i in var]
        if (type == 'int'    ): var = [int  (i) for i in var]
        if (type == 'boolean'):
            var = [i == 'True' for i in var]
    
        if (len(var) == 1 and not asList):
            return var[0]
        else:
            return var

    def Default(self, section, field, default = None, type = '', *arg, **kw):
        try:
            var = self.List(section, field, type, *arg, **kw)
        except:
            if (default == 'required'): sys.exit('Default required: ' + section + ': ' + field)
            var = default
        return var
