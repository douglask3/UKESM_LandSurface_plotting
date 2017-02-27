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

try:
    datDirDefault = os.popen('echo $DATADIR').readlines()[0][:-1] +'/'
except:
    datDirDefault = 'data'

datDir       = Config.Default("FileInfo", "dir"         , default = datDirDefault)
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
    FigdCmap      =  Config.Default(section, "FigdCmap"     , "brewer_Spectral_11")
    VarStashCodes =  Config.Default(section, "VarStashCodes", "required"       , asList = True)
    
    VarNames_default = jobs if (len(jobs) > 1 and len(VarStashCodes) == 1) else VarStashCodes
	
    VarNames      =  Config.Default(section, "VarNames"     , VarNames_default    , asList = True)
    VarScaling    =  Config.Default(section, "VarScaling"   , 1.0  , "float"   )
    VarLbelv      =  Config.Default(section, "VarLbelv"     , None,  "int"     )
    VarLevels     =  Config.Default(section, "VarLevels"    , None,  "float"   )
    VardLevels    =  Config.Default(section, "VardLevels"   , None,  "float"   )
    VarCmap       =  Config.Default(section, "VarCmap"      , [FigCmap]           , asList = True)
    VardCmap      =  Config.Default(section, "VardCmap"     , [FigdCmap]          , asList = True)
    Total         =  Config.Default(section, "Total"        , False, "boolean" )
    Stream        =  Config.Default(section, "Stream"                          )
    FigTS         =  Config.Default(section, "FigTS"        , True , "boolean" )
    FigTSMean     =  Config.Default(section, "FigTSMean"    , True , "boolean" )
    FigTSUnits    =  Config.Default(section, "FigTSUnits")
    Diff          =  Config.Default(section, "FigDiff"      , True if len(jobs) == 2 else False, "boolean")
    
    def lenNone(x): return(0 if x is None else len(x))
    
    if (len(jobs) > 1 and (lenNone(VarStashCodes) > 1 or lenNone(VarLbelv) > 1)):
        opr = []
        for job, datD in zip(jobs, datDirs):
            datDirt = datD if Stream is None else datD + Stream + '/'
            FigNamei = jdir + '/' +  job + '-' + FigName
            files = sort(listdir_path(datDirt))
            
            opri = open_plot_return(files, VarStashCodes, VarLbelv, VarNames, FigUnits,
                               diff = Diff, total = Total, scale = VarScaling)
            opri.plot_cubes(FigNamei, FigTitle + ' ' + job, FigTS, FigTSMean, FigTSUnits,
                            running_mean, VarLevels, VarCmap)
            opr.append(opri)
        
        opr[1].diff(opr[0])
        
        ## needs new Levels and Cmap for diff.
        FigName = jdir + '/' + 'diff_' + jobs[1] + '-' + jobs[0] + FigName
        opr[1].plot_cubes(FigName, FigTitle + ' differnce', FigTS, FigTSMean, FigTSUnits,
                       running_mean, VardLevels, VardCmap)
        
        
    else:
        ## find files
        files = []
        for datD in datDirs:
	    datDirt = datD if Stream is None else datD + Stream + '/'        
	    files.append(sort(listdir_path(datDirt)))
       
        FigName = jdir + '/' + FigName

    
        opr = open_plot_return(files, VarStashCodes, VarLbelv, VarNames, FigUnits,
                               diff = Diff, total = Total, scale = VarScaling)
    
        opr.plot_cubes(FigName, FigTitle, FigTS, FigTSMean,
                       running_mean = running_mean,
                       levels = VarLevels, cmap = VarCmap)


