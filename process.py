import ConfigParser
import json
import sys
from   pdb   import set_trace as browser
from   libs.open_plot_return import *
from libs.grab_data import grab_data


def ConfigGetList(type = '', *arg):
    var = Config.get(*arg)
    var = [e.strip() for e in var.split(',')]

    ## replace with something shorter and cleverer
    if (type == 'float'  ): var = [float  (i) for i in var]
    if (type == 'boolean'): var = [boolean(i) for i in var]

    if (len(var) == 1):
        return var[0]
    else:
        return var

def ConfigGetDefault(section, field, type = '', default = None):
    try:
        var = ConfigGetList(type, section, field)
    except:
        if (default == 'required'): sys.exit('Default required: ' + section + ': ' + field)
        var = default
    return var

Config = ConfigParser.ConfigParser()
Config.read(sys.argv[1])


datDir       = ConfigGetDefault("FileInfo", "dir"         )
job          = ConfigGetDefault("FileInfo", "job"         )
stream       = ConfigGetDefault("FileInfo", "stream"      )
running_mean = ConfigGetDefault("FileInfo", "running_mean", 'boolean', False)

if (datDir is None):
    if (job is None or stream is None):
        sys.exit('either a local dir for ESM output, or a suite code and ouput stream need to be defined')
    datDir = 'data/' + job + '/' + stream + '/'
    ## collect stash codes
    stash = []
    for i in Config.sections():
        newStash = ConfigGetDefault(i, "VarStashCodes")
        if (newStash is not None): stash.extend(newStash)

    grab_data(job, stream, stash, datDir)    

browser()
files = sort(listdir_path(datDir))
opr   = open_plot_return(files, running_mean = running_mean)

for section in Config.sections():
    if (section == 'FileInfo'): continue
    
    FigName       =  ConfigGetList(''     , section, "FigName"      )
    FigTitle      =  ConfigGetList(''     , section, "FigTitle"     )
    FigUnits      =  ConfigGetList(''     , section, "FigUnits"     )
    FigCmap       =  ConfigGetList(''     , section, "FigCmap"      )
    VarNames      =  ConfigGetList(''     , section, "VarNames"     )
    VarStashCodes =  ConfigGetList(''     , section, "VarStashCodes")
    VarScaling    =  ConfigGetList('float', section, "VarScaling"   )

    opr.open_plot_and_return(FigName, FigTitle, VarStashCodes, VarNames,  FigUnits, FigCmap, scale = VarScaling)


