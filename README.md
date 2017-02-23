# UKESM_LandSurface_plotting

## Download

    git clone https://github.com/douglask3/UKESM_LandSurface_plotting.git
    cd UKESM_LandSurface_plotting

## Use

Setup up one of the .ini files. There's a few ini templates in the repo you can adapt depending on what you want to do:

1. **monitor_carbon.ini** Plots different carbon pools and/or fluxes into different plots (cVeg => vegPool;  NPP  , fVegSoil, fDeforestToProduct_Fast, fDeforestToProduct_Medium, fDeforestToProduct_Slow, fAnthDisturb, othersVegAtm => VegFLux etc) for suite u-aj053, garbbing data from apm and api output streams.
1. **monitor_vegfrac.ini** Plots a map for each vegetated tile fraction area, and a TS of global change of each tile type, for suite u-aj062.
1. **compare_albedo.ini** Compares 3 different outputs (tempurature, VIS albedo scaling and NIR albedo scaling) for two suites (u-aj523, u-aj526). This will plot a map for each suite, a difference map of u-aj526 - u-aj523, and a global time series of each 3 map (with the exception of tempurature, where the time series has been turned off).
1. **monitor_albedo.ini** Compares albedo plotting on individua tiles for VIS and NIR on two different suites (u-aj523 and u-aj526). This will produce 3 plots per variable (6 in total): one tile maps and time series for u-aj523; one for u-aj526; and difference maps/time series for u-aj526 - u-aj523.

Plus some more to explore.

### Config file fields

[FileInfo] contains fields taht apply to all plotting sections. Any other namelists listed after contains fields for each individual plot.

    [FileInfo]   ## Required namelist
    dir: path/to/mod/outputs/ ## Options. Where to store or (if outputs are already stored locally) find model outputs. Defaults to 'data/'
    job: u-xx123 ## i.e, u-ah410. Required if grabbing data of mass OR dir is not supplied
    stream: xxx # i.e, api. Required if grabbing data of mass OR dir is not supplied. Multipled can be listed.
    running_mean: False # Optional, default is False

    [SectionTemplate]   ## Requires at least one extra namelist. Can be multiple
    FigName: xxxx ## Optional. filename of figures produced. Default set to namelist title
    FigTitle: xxx_xxx_xxx ## Optional figure title. Default is blank
    FigUnits: g m-2 ## units of variables plotted in figure. UM output units as default
    FigCmap: brewer_GnBu_09 ## Optional colourmap of maps. Default of brewer_GnBu_09
    VarStashCodes: m01sxxiyyy, m01sxxiyyy, m01sxxiyy ## Required. Stash codes of variables for plotting
    VarNames: aaa, bbb, ccc ## Optional, but should be same length as VarStashCodes if provided. Variable names for plot labelling. Default to UM output varname.
    VarScaling: x, y, z  ## Optional. Scaling applied to variable before plotting. Default to 1.
    
Plus some more that I shall add to the readme soon.
    
### Run
Simply use the command:

    python process.py <<filename.ini>>
    
where filename.ini is config filename.

Plots will be distributed into various directories within 'figs/'
