import ConfigParser
import json

from libs.open_plot_return import *


def ConfigGetList(type = '', *arg):
    var = Config.get(*arg)
    var = [e.strip() for e in var.split(',')]

    ## replace with something shorter and cleverer
    if (type == 'float'): var = [float(i) for i in var]

    if (len(var) == 1):
        return var[0]
    else:
        return var

Config = ConfigParser.ConfigParser()
Config.read("look_at_carbon.ini")

dir          = Config.get("FileInfo", "dir"         )
running_mean = Config.get("FileInfo", "running_mean")
files        = sort(listdir_path(dir))

opr          = open_plot_return(files, running_mean = running_mean)

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


