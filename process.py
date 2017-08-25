import ConfigParser
import json
import sys, os
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
fdirSub      = Config.Default("FileInfo", "figSubDir"   )
stream       = Config.Default("FileInfo", "Stream"      )
grab         = Config.Default("FileInfo", "grab"        , True,  "boolean")
running_mean = Config.Default("FileInfo", "running_mean", False, 'boolean')
namelistDoc  = Config.Default("FileInfo", "namelistDoc" , "")
namelists    = Config.Default("FileInfo", "namelist"    , [""]    , asList = True)

namelists = [namelistDoc + '/' + i for i in namelists]
with open('temp/fullNamelist.ini', 'w') as fullNL:
    for file in sys.argv[1:] + namelists:
        try:
            for line in open (file, 'r'):
                fullNL.write(line)
        except:
            pass

Config = ConfigGet('temp/fullNamelist.ini')
fdir0  = Config.Default("FileInfo", "figsDir"     , jdir)
fdir   = fdirSub + '/' + fdir0
os.system('rm -r figs/' + fdir + '/*')

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
    FigLon        =  Config.Default(section, "FigLon"       , None, "float"    ) 
    FigLat        =  Config.Default(section, "FigLat"       , None, "float"    ) 
    
    titleDefault  = section + '\n'
    if FigLon is not None: titleDefault += '| Longitude: ' + str(FigLon) + ' |'
    if FigLat is not None: titleDefault += '| Latitude: '  + str(FigLat) + ' |' 

    FigTitle      =  Config.Default(section, "FigTitle"     , titleDefault     )
    FigUnits      =  Config.Default(section, "FigUnits"                        )
    FigCmap       =  Config.Default(section, "FigCmap"      , "brewer_Greys_09")
    FigdCmap      =  Config.Default(section, "FigdCmap"     , "brewer_Spectral_11")
    FigrCmap      =  Config.Default(section, "FigrCmap"     , "brewer_Spectral_11")
    VarStashCodes =  Config.Default(section, "VarStashCodes", "required"       , asList = True)
    
    VarNames_default = jobs if (len(jobs) > 1 and len(VarStashCodes) == 1) else VarStashCodes
	
    VarNames      =  Config.Default(section, "VarNames"     , VarNames_default    , asList = True)
    plotNames     =  Config.Default(section, "plotNames"    , None                , asList = True)
    VarScaling    =  Config.Default(section, "VarScaling"   , 1.0  , "float"   )
    VarLbelv      =  Config.Default(section, "VarLbelv"     , None,  "int"     )
    VarLevels     =  Config.Default(section, "VarLevels"    , None,  "float"   )
    VardLevels    =  Config.Default(section, "VardLevels"   , None,  "float"   )
    VarrLevels    =  Config.Default(section, "VarrLevels"   , VardLevels,  "float"   )
    VarPlotN      =  Config.Default(section, "VarPlotN"     , None,  "int"        )
    VarCmap       =  Config.Default(section, "VarCmap"      , [FigCmap]           , asList = True)
    VardCmap      =  Config.Default(section, "VardCmap"     , [FigdCmap]          , asList = True)
    VarrCmap      =  Config.Default(section, "VarrCmap"     , [FigrCmap]           , asList = True)
    Total         =  Config.Default(section, "Total"        , False, "boolean" )
    TotalOnly     =  Config.Default(section, "TotalOnly"    , False, "boolean" )
    Stream        =  Config.Default(section, "Stream"                          )
    FigTS         =  Config.Default(section, "FigTS"        , True , "boolean" )
    FigTSMean     =  Config.Default(section, "FigTSMean"    , True , "boolean" )
    FigTSUnits    =  Config.Default(section, "FigTSUnits")
    Ratio         =  Config.Default(section, "FigRatio"     , False, "boolean" )
    Diff          =  Config.Default(section, "FigDiff"      , True if len(jobs) == 2 and not Ratio else False, "boolean")
    DiffN         =  Config.Default(section, "FigVarNDiff"  , None,  "int"     )
    FigChange     =  Config.Default(section, "FigChange"    , False, "boolean" )
    FigAccumulate =  Config.Default(section, "FigAccumulate", False, "boolean" )
    
    Change        =  Config.Default(section, "VarChange"    , [FigChange], "boolean" )
    Accumulate    =  Config.Default(section, "VarAccumulate", [FigAccumulate], "boolean" )
    
    def lenNone(x): return(0 if x is None else len(x))
    
    if len(jobs) > 1 and (lenNone(VarStashCodes) > 1 or lenNone(VarLbelv) > 1):
        opr = []
        for job, datD in zip(jobs, datDirs):
            datDirt = datD if Stream is None else datD + Stream + '/'
            FigNamei = fdir + '/' +  job + '-' + FigName
            files = sort(listdir_path(datDirt))

            print section

            opri = open_plot_return(files, VarStashCodes, VarLbelv, VarPlotN, VarNames, plotNames,
                                    FigLon, FigLat, FigUnits,
                               diff = Diff, ratio = Ratio,
                               total = Total, totalOnly = TotalOnly,
                               scale = VarScaling,
                               change = Change, accumulate = Accumulate)
            
            if Ratio and (lenNone(VarStashCodes) == 2 or lenNone(VarLbelv) == 2):
                levels = [VarLevels, VarLevels, VarrLevels]
                cmap1  = VarCmap[0]  if type(VarCmap)  is list else  VarCmap
                cmap2  = VarrCmap[0] if type(VarrCmap) is list else  VarrCmap
                cmap   = [cmap1  , cmap1  , cmap2  ]
            else:
                levels = VarLevels
                cmap   = VarCmap
            opri.plot_cubes(FigNamei, FigTitle + ' ' + job, FigTS, FigTSMean, FigTSUnits,
                            running_mean, levels, cmap)
            opr.append(opri)
        
        opr[0].diff(opr[1], DiffN, jobs)

        cmaps = VardCmap[:]
        levels = [VardLevels]

        if DiffN is None:
            FigTitle += ' differnce'
        else:
            for _ in range(2):
                cmaps.insert(0, VarCmap[0])
                levels.insert(0, VarLevels)
        if len(levels) == 1 and type(levels[0]) is list: levels = levels[0]
        ## needs new Levels and Cmap for diff.
        FigName = fdir + '/' + 'diff_' + jobs[1] + '-' + jobs[0] + FigName
        
        opr[0].plot_cubes(FigName, FigTitle, FigTS, FigTSMean, FigTSUnits, running_mean, levels, cmaps)
      
         
    else:
        ## find files
        files = []
        for datD in datDirs:
	    datDirt = datD if Stream is None else datD + Stream + '/'        
	    files.append(sort(listdir_path(datDirt)))
        
        FigName = fdir + '/' + FigName
        if len(jobs) > 1 and len(VarNames) == 1: VarNames = [VarNames[0] + '-' + i for i in jobs]

        opr = open_plot_return(files, VarStashCodes, VarLbelv, VarPlotN, VarNames, plotNames,
                               FigLon, FigLat, FigUnits,
                               diff = Diff, total = Total, totalOnly = TotalOnly,
                               scale = VarScaling,
                               change = Change, accumulate = Accumulate)
        
        if len(jobs) == 2 and Diff:
            VarLevels = [VarLevels, VarLevels, VardLevels]
            if len(VarCmap) == 1: VarCmap   = [VarCmap[0]  , VarCmap[0]  , VardCmap[0]  ]

    
        opr.plot_cubes(FigName, FigTitle, FigTS, FigTSMean,
                       running_mean = running_mean,
                       levels = VarLevels, cmap = VarCmap)
    
    fdirNew         = Config.Default(section, "figsDir"     , fdir0)

    if fdirNew != fdir0:
        fdir0 = fdirNew
        fdirNew = fdirSub + '/' + fdirNew
        if fdir[-1]=='/': fdir = fdir[:-1]
        os.system('convert $(ls -dr figs/' + fdir + '/*) figs/' + fdir + '-' + fdirSub + '.pdf')
        fdir = fdirNew
        os.system('rm -r figs/' + fdir + '/*')
        
if fdir[-1]=='/': fdir = fdir[:-1]
os.system('convert $(ls -dr figs/' + fdir + '/*) figs/' + fdir + '-' + fdirSub + '.pdf')
