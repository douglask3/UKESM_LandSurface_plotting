import ConfigParser
import json
import sys
from   pdb   import set_trace as browser
from   libs.grab_data import *
from   libs.ConfigGet import ConfigGet
import warnings

Config = ConfigGet(sys.argv[1])

ceh          = Config.Default("MachineInfo", "ceh", False, "boolean")
if (ceh): import libs.import_iris
from   libs.open_plot_return import *

datDir       = Config.Default("FileInfo", "dir"         , default = 'data/')
jobs         = Config.Default("FileInfo", "job"         , asList = True)
jdir         = Config.Default("FileInfo", "subDir"      )
stream       = Config.Default("FileInfo", "Stream"      )
grab         = Config.Default("FileInfo", "grab"        , True,  "boolean")
running_mean = Config.Default("FileInfo", "running_mean", False, 'boolean')

datDirs = []
for job in jobs:
    if (job is None or stream is None):
        sys.exit('either a local dir for ESM output, or a suite code and ouput stream need to be defined')
    
    datDiri = datDir + job + '/' + jdir + '/'
    datDirs.append(datDiri)
    ## collect stash codes
    stash = []
    for i in Config.sections():
        newStash = Config.Default(i, "VarStashCodes", asList = True)
        if (newStash is not None): stash.extend(newStash)
    
    if (grab): grab_data(job, stream, stash, datDiri)    


	
for section in Config.sections():
    if (section == 'FileInfo' or section == 'MachineInfo'): continue
    
    FigName       =  Config.Default(section, "FigName"      , section          )
    FigTitle      =  Config.Default(section, "FigTitle"     , section          )
    FigUnits      =  Config.Default(section, "FigUnits"                        )
    FigCmap       =  Config.Default(section, "FigCmap"      , "brewer_Greys_09")
    VarStashCodes =  Config.Default(section, "VarStashCodes", "required"       , asList = True)
    
    if (len(jobs) > 1 and len(VarStashCodes) > 1):
	warnings.warn('More than one stash code for a multi-job plot. Only first one uses')
	VarStashCodes = [VarStashCodes[0]]
	
    VarNames_default = jobs if (len(jobs) > 1) else VarStashCodes
	
    VarNames      =  Config.Default(section, "VarNames"     , VarNames_default    , asList = True)
    VarScaling    =  Config.Default(section, "VarScaling"   , 1.0  , "float"   )
    VarLbelv      =  Config.Default(section, "VarLbelv"     , None,  "int"     )
    VarLevels     =  Config.Default(section, "VarLevels"    , None,  "float"   )
    Total         =  Config.Default(section, "Total"        , False, "boolean" )
    Stream        =  Config.Default(section, "Stream"                          )
    FigTSMean     =  Config.Default(section, "FigTSMean"    , True , "boolean" )
    
    ## find files
    files = []
    for datD in datDirs:
	datDirt = datD if Stream is None else datD + Stream + '/'        
	files.append(sort(listdir_path(datDirt)))
       
    FigName = jdir + '/' + FigName

    ## adapt for multi files jobs
    opr = open_plot_return(files, VarStashCodes, VarLbelv, VarNames, FigUnits,
                           total = Total, scale = VarScaling)
    opr.plot_cubes(FigName, FigTitle, FigTSMean, running_mean, VarLevels, FigCmap)


