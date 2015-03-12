#!/bin/bash                                          
                                                     
function command(){                                  
     echo ">>>" $@                                   
     eval $@                                         
}

workDir=$PWD  
                                                                       
logDir=${workDir}"/BATCHJOBS/MC_v4h0/"
command "mkdir -p $logDir"

castorDirIn="/store/group/phys_heavyions/dileptons/MC2013/5TeV/NonPromptJpsi/"
castorDirOut="/store/group/phys_heavyions/dileptons/MC2013/5TeV/NonPromptJpsi/Skims/"
command "cmsMkdir $castorDirOut"


j=0
jobNb=""

#for file in `nsls $castorDirIn`
#for i in `seq 0 99`

#declare -a missingRuns=(0)
#for i in `echo ${missingRuns[@]}`
for fileList in `ls nonpromptJpsi_??`
do
#    fileList="upsilon1s_"$i
    echo $fileList;
    # file="MC_PromptNonPromptJpsi_FEVTDEBUGHLT_"${i}".root"
    jobNb=${j};
    let j=${j}+1;
    name="onia2MuMuPAT_MC_${jobNb}"
    outfilename="${name}.root"


#Start to write the script
    cat > job_Onia2MuMu_MCSkim_${jobNb}.sh << EOF
#!/bin/bash

function command(){                                  
     echo ">>>" \$@                                   
     eval \$@                                         
}

cd ${CMSSW_BASE}/src
eval \`scramv1 runtime -sh\`
cd -
cp ${workDir}/onia2MuMuPAT_pAMC_cfg.py tmp.py
cp ${workDir}/${fileList} .
echo "before running cmsRun"
ls -l

command "cmsRun tmp.py inputFiles_clear inputFiles_load=${fileList} print 2>&1 | tee -a $logDir${name}.log"
echo "after running cmsRun"
ls -l

command "cmsStage onia2MuMuPAT_MC.root ${castorDirOut}${outfilename}"
command "gzip -f $logDir${name}.log"         
rm -f tmp.py
rm -f ${fileList}

EOF

    chmod 755 job_Onia2MuMu_MCSkim_${jobNb}.sh
    
    bsub -q 2nd -J $name ${workDir}/job_Onia2MuMu_MCSkim_${jobNb}.sh

done
