#!/bin/bash                                          
                                                     
function command(){                                  
     echo ">>>" $@                                   
     eval $@                                         
}

workDir=$PWD  
                                                                       
logDir=${workDir}"/BATCHJOBS/v0h0/"
command "mkdir -p $logDir"

castorDirOut="/store/caf/user/tdahms/Data2013/pPb/ExpressSkims/Runs_210498-210638/Skim/"
#command "cmsMkdir -p $castorDirOut"


j=0
jobNb=""

for fileList in `ls express_runs_210498-210638_??`
do
    echo $fileList;
    jobNb=${j};
    let j=${j}+1;
    name="onia2MuMuPAT_${jobNb}"
    outfilename="${name}.root"


#Start to write the script
    cat > job_Onia2MuMu_EOS_${jobNb}.sh << EOF
#!/bin/bash

function command(){                                  
     echo ">>>" \$@                                   
     eval \$@                                         
}


cd ${CMSSW_BASE}/src
eval \`scramv1 runtime -sh\`
cd -
cp ${workDir}/onia2MuMuPAT_pAData_cfg.py tmp.py
cp ${workDir}/${fileList} .
echo "before running cmsRun"
ls -l

command "cmsRun tmp.py inputFiles_clear inputFiles_load=${fileList} print 2>&1 | tee -a $logDir${name}.log"

echo "after running cmsRun"
ls -l

command "cmsStage onia2MuMuPAT.root ${castorDirOut}${outfilename}"
command "gzip -f $logDir${name}.log"
command "rm -f tmp.py"
command "rm -f ${fileList}"

EOF

	chmod 755 job_Onia2MuMu_EOS_${jobNb}.sh
	
	bsub -q cmscaf1nd -J $name ${workDir}/job_Onia2MuMu_EOS_${jobNb}.sh

done
