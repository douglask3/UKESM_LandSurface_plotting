import os
jobs = ['u-bc179', 'u-bc292', 'u-bc370', 'u-bb075', 'u-az513', 'u-az515', 'u-az524', 'u-bb277', 'u-bc470', 'u-bd288', 'u-bd416', 'u-bd483']
jobs = ['u-by791', 'u-bz502', 'u-bz897', 'u-ca360', 'u-ca811', 'u-cb799']
figSubDirs = jobs

fileInfos = " \n\
subDir: LandEvaluation_UKESM1.1/ \n\
grab: True \n\
Stream: apm \n\
StartYr:1980 \n\
EndYr: 2014  \n\
MapEndYrsN: 1  \n\
namelistDoc: namelists/ \n\
namelist: monitor_carbon.ini, monitor_lai.ini\n"

def generate_namelist(job, figSubDir):
    fileInfo = "[FileInfo]\njob: " + job + "\nfigSubDir: " + figSubDir + fileInfos
    filename = 'temp/' + job + '_' + '.ini'
    
    file = open(filename, "w")
    file.write(fileInfo)
    file.close()
    command = '/usr/local/sci/bin/python2.7 process.py ' + filename
    print(command)
    os.system(command)

[generate_namelist(job, figSubDir) for job, figSubDir in zip(jobs, figSubDirs)]
