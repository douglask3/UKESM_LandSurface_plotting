import ConfigParser
import json
import sys
from   pdb   import set_trace as browser
from   libs.grab_data import *
from   libs.ConfigGet import ConfigGet

Config = ConfigGet(sys.argv[1])

ceh          = Config.Default("MachineInfo", "ceh", False, "boolean")
if (ceh): import libs.import_iris
from   libs.open_plot_return import *

datDir       = Config.Default("FileInfo", "dir"         )
job          = Config.Default("FileInfo", "job"         )
jdir         = Config.Default("FileInfo", "subDir"      )
stream       = Config.Default("FileInfo", "Stream"      )
grab         = Config.Default("FileInfo", "grab"        , True,  "boolean")
running_mean = Config.Default("FileInfo", "running_mean", False, 'boolean')

if (datDir is None):
    if (job is None or stream is None):
        sys.exit('either a local dir for ESM output, or a suite code and ouput stream need to be defined')
    
    datDir = 'data/' + job + '/' + jdir + '/'
    ## collect stash codes
    stash = []
    for i in Config.sections():
        newStash = Config.Default(i, "VarStashCodes", asList = True)
        if (newStash is not None): stash.extend(newStash)
    
    if (grab): grab_data(job, stream, stash, datDir)    

for section in Config.sections():
    if (section == 'FileInfo' or section == 'MachineInfo'): continue
    
    FigName       =  Config.Default(section, "FigName"      , section          )
    FigTitle      =  Config.Default(section, "FigTitle"     , section          )
    FigUnits      =  Config.Default(section, "FigUnits"                        )
    FigCmap       =  Config.Default(section, "FigCmap"      , "brewer_Greys_09")
    VarStashCodes =  Config.Default(section, "VarStashCodes", "required"       , asList = True)
    VarNames      =  Config.Default(section, "VarNames"     , VarStashCodes    , asList = True)
    VarScaling    =  Config.Default(section, "VarScaling"   , 1.0  , "float"   )
    Total         =  Config.Default(section, "Total"        , False, "boolean" )
    Stream        =  Config.Default(section, "Stream"                          )
    FigTSMean     =  Config.Default(section, "FigTSMean"    , True , "boolean" )
    
    if (Stream is not None): datDirt = datDir + Stream + '/'
    else: datDirt = datDir
        
    files = sort(listdir_path(datDirt))
    
    FigName = jdir + '/' + FigName
    opr   = open_plot_return(files, total = Total, running_mean = running_mean)
    opr.open_plot_and_return(FigName, FigTitle, VarStashCodes, VarNames,  FigUnits, FigTSMean, FigCmap, scale = VarScaling)


