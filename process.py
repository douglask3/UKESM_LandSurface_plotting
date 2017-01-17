import ConfigParser
import json
import sys
from   pdb   import set_trace as browser
from   libs.grab_data import grab_data


def ConfigGetList(section, field, type = '', asList = False, *arg):
    var = Config.get(section, field, *arg)
    var = [e.strip() for e in var.split(',')]

    ## replace with something shorter and cleverer
    if (type == 'float'  ): var = [float  (i) for i in var]
    if (type == 'boolean'):
        var = [i == 'True' for i in var]
    
    if (len(var) == 1 and not asList):
        return var[0]
    else:
        return var

def ConfigGetDefault(section, field, default = None, type = '', *arg, **kw):
    try:
        var = ConfigGetList(section, field, type, *arg, **kw)
    except:
        if (default == 'required'): sys.exit('Default required: ' + section + ': ' + field)
        var = default
    return var

Config = ConfigParser.ConfigParser()
Config.read(sys.argv[1])

ceh          = ConfigGetDefault("MachineInfo", "ceh", False, "boolean")
if (ceh): import libs.import_iris
from   libs.open_plot_return import *

datDir       = ConfigGetDefault("FileInfo", "dir"         )
job          = ConfigGetDefault("FileInfo", "job"         )
stream       = ConfigGetDefault("FileInfo", "Stream"      )
grab         = ConfigGetDefault("FileInfo", "grab"        , True,  "boolean")
running_mean = ConfigGetDefault("FileInfo", "running_mean", False, 'boolean')

if (datDir is None):
    if (job is None or stream is None):
        sys.exit('either a local dir for ESM output, or a suite code and ouput stream need to be defined')
    
    datDir = 'data/' + job + '/'
    ## collect stash codes
    stash = []
    for i in Config.sections():
        newStash = ConfigGetDefault(i, "VarStashCodes", asList = True)
        if (newStash is not None): stash.extend(newStash)
       
    if (grab): grab_data(job, stream, stash, datDir)    



for section in Config.sections():
    if (section == 'FileInfo' or section == 'MachineInfo'): continue
    
    FigName       =  ConfigGetDefault(section, "FigName"      , section          )
    FigTitle      =  ConfigGetDefault(section, "FigTitle"     , section          )
    FigUnits      =  ConfigGetDefault(section, "FigUnits"                        )
    FigCmap       =  ConfigGetDefault(section, "FigCmap"      , "brewer_Greys_09")
    VarNames      =  ConfigGetDefault(section, "VarNames"     , 'required'       , asList = True)
    VarStashCodes =  ConfigGetDefault(section, "VarStashCodes", "required"       , asList = True)
    VarScaling    =  ConfigGetDefault(section, "VarScaling"   , 1.0  , "float"   )
    Total         =  ConfigGetDefault(section, "Total"        , False, "boolean" )
    Stream        =  ConfigGetDefault(section, "Stream"                          )
    
    if (Stream is not None):
        datDirt = datDir + Stream + '/'
    else:
        datDirt = datDir
        
    files = sort(listdir_path(datDirt))
    opr   = open_plot_return(files, total = Total, running_mean = running_mean)
    opr.open_plot_and_return(FigName, FigTitle, VarStashCodes, VarNames,  FigUnits, FigCmap, scale = VarScaling)


