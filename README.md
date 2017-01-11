# UKESM_LandSurface_plotting

## Download

    git clone 
    cd UKESM_LandSurface_plotting

## Use

### Config file

An example:

    [FileInfo]   ## Required section
    dir: path/to/mod/outputs/ ## If outputs are store locally
    job: xx123 ## i.e, ah410 - required if grabbing data of mass AND dir is not supplied
    stream: xxx # i.e, api - required if grabbing data of mass AND dir is not supplied
    running_mean: False # Optional, default is false

    [SectionTemplate]   ## Requires at least one. Can be multiple
    FigName: xxxx ## Required. filename of figure
    FigTitle: xxx xxx xxx ## Optional figure title. Default is blank
    FigUnits: g m-2 ## units of variables plotted in figure. ESM output units as default
    FigCmap: brewer_GnBu_09 ## Optional colourmap of maps
    VarStashCodes: m01sxxiyyy, m01sxxiyyy, m01sxxiyy ## Required. Stash codes of variables for plotting
    VarNames: aaa, bbb, ccc ## Optional, but should be same length as VarStashCodes if provided. Variable names for plot labelling. Default to ESM output
    VarScaling: x, y, z  ## Scaling required for calculating total.
    
### Run

    python process.py <filename>
    
where filename is config filename.
