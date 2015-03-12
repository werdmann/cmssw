# for the list of used tags please see:
# https://twiki.cern.ch/twiki/bin/view/CMS/Onia2MuMuSamples

import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

# set up process
process = cms.Process("Onia2MuMuPAT")

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

# setup any defaults you want
options.inputFiles = 'rfio:/castor/cern.ch/cms/store/user/tdahms/HeavyIons/Onia/MC/v6/MC_NonPromptJpsi_FEVTDEBUGHLT_98.root'

options.maxEvents = -1 # -1 means all events

# get and parse the command line arguments
options.parseArguments()

process.load('Configuration.StandardSequences.GeometryExtended_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = 'START39_V7HI::All'
#process.GlobalTag.globaltag = 'START311_V1::All'

from CmsHi.Analysis2010.CommonFunctions_cff import *
overrideCentrality(process)

process.HeavyIonGlobalParameters = cms.PSet(
    centralityVariable = cms.string("HFhits"),
    nonDefaultGlauberModel = cms.string("Hydjet_Bass"),
    centralitySrc = cms.InputTag("hiCentrality")
    )

# BSC or HF coincidence (masked unprescaled L1 bits)
process.load('L1Trigger.Skimmer.l1Filter_cfi')
process.bscOrHfCoinc = process.l1Filter.clone(
    algorithms = cms.vstring('L1_BscMinBiasThreshold1', 'L1_HcalHfCoincidencePm')
    )
    

# Common offline event selection
process.load("HeavyIonsAnalysis.Configuration.collisionEventSelection_cff")

# HLT dimuon trigger
import HLTrigger.HLTfilters.hltHighLevel_cfi
# early runs (to be done)
process.hltMinBiasHFOrBSCEarly = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.hltMinBiasHFOrBSCEarly.HLTPaths = ["HLT_HIMinBiasHF","HLT_HIMinBiasBSC"]
#process.hltMinBiasHFOrBSCEarly.HLTPaths = ["HLT_HIMinBiasHF_Core","HLT_HIMinBiasBSC_Core"]
process.hltMinBiasHFOrBSCEarly.throw = False
process.hltMinBiasHFOrBSCEarly.andOr = True

process.hltMinBiasHFOrBSC = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.hltMinBiasHFOrBSC.HLTPaths = ["HLT_HIMinBiasHfOrBSC"]
#process.hltMinBiasHFOrBSC.HLTPaths = ["HLT_HIMinBiasHfOrBSC_Core"]
process.hltMinBiasHFOrBSC.throw = False


process.hltOniaHI = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.hltOniaHI.HLTPaths = ["HLT_HIL1DoubleMuOpen","HLT_HIL2DoubleMu0","HLT_HIL2DoubleMu3",
                              "HLT_HIL1SingleMu3","HLT_HIL1SingleMu5","HLT_HIL1SingleMu7",
                              "HLT_HIL2Mu20","HLT_HIL2Mu3","HLT_HIL2Mu5Tight"]

#process.hltOniaHI.HLTPaths = ["HLT_HIL1DoubleMuOpen_Core","HLT_HIL2DoubleMu0_Core","HLT_HIL2DoubleMu3_Core",
#                              "HLT_HIL1SingleMu3_Core","HLT_HIL1SingleMu5_Core","HLT_HIL1SingleMu7_Core",
#                              "HLT_HIL2Mu20_Core","HLT_HIL2Mu3_Core","HLT_HIL2Mu5Tight_Core"]
process.hltOniaHI.throw = False
process.hltOniaHI.andOr = True

process.MinBiasCounterEarly = cms.EDAnalyzer('MinBiasCounter',
                                             TriggerResultsLabel = cms.InputTag("TriggerResults","","HLT"),
                                             triggerName = cms.vstring("HLT_HIMinBiasHF","HLT_HIMinBiasBSC"),
                                             histFileName = cms.string("MinBiasCentralityEarly_MC_Histo.root")
                                             )

process.MinBiasCounter = cms.EDAnalyzer('MinBiasCounter',
                                        TriggerResultsLabel = cms.InputTag("TriggerResults","","HLT"),
                                        triggerName = cms.vstring("HLT_HIMinBiasHfOrBSC"),
                                        histFileName = cms.string("MinBiasCentrality_MC_Histo.root")
                                        )

process.DoubleMuOpenCounter = cms.EDAnalyzer('MinBiasCounter',
                                             TriggerResultsLabel = cms.InputTag("TriggerResults","","HLT"),
                                             triggerName = cms.vstring("HLT_HIL1DoubleMuOpen"),
                                             histFileName = cms.string("DoubleMuOpenCentrality_MC_Histo.root")
                                             )

#process.MinBiasEarlyPath = cms.Path(process.hltMinBiasHFOrBSCEarly *
#                                    process.collisionEventSelection *
#                                    process.MinBiasCounterEarly
#                                    )
#
#process.MinBiasPath = cms.Path(process.hltMinBiasHFOrBSC *
#                               process.collisionEventSelection *
#                               process.MinBiasCounter
#                               )

from HiSkim.HiOnia2MuMu.onia2MuMuPAT_cff import *

onia2MuMuPAT(process, GlobalTag=process.GlobalTag.globaltag, MC=True, HLT="HLT", Filter=True)

process.onia2MuMuPatGlbGlb.addMuonlessPrimaryVertex = False
process.onia2MuMuPatGlbGlb.resolvePileUpAmbiguity = False

process.muonL1Info.matched = "hltL1extraParticles"

process.Onia2MuMuPAT.remove(process.DoubleMuOpenCounter)
#process.Onia2MuMuPAT.remove(process.hltOniaHI)

process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')
process.source.fileNames = cms.untracked.vstring(
    options.inputFiles
    )

'''
import os,commands
# get a list of files from a specified directory
mydir = "/castor/cern.ch/cms/store/user/tdahms/HeavyIons/Onia/MC/v1/"

cmd  = 'nsls %s/ ' % (mydir)
mylist = ["rfio:%s/%s" % (mydir,j) for j in commands.getoutput(cmd).split('\n')]

# add a specified number of files from mydir to the list of fileNames
start=0
nfiles=94
for i in range(start,start+nfiles):
     process.source.fileNames.append('%s' % (mylist[i]))
     print "process.source.fileNames.append(%s" % (mylist[i])
print "Number of files to process is %s" % (len(process.source.fileNames))
'''

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )

process.outOnia2MuMu.fileName = cms.untracked.string( 'onia2MuMuPAT_MC.root' )
process.outSta.fileName = cms.untracked.string('tnpSta_MC.root')
process.outMuID.fileName = cms.untracked.string('tnpMuID_MC.root')
process.outTrig.fileName = cms.untracked.string('tnpTrig_MC.root')


#disable TnP path temporarily
#process.TagAndProbeSta = cms.Path()
#process.TagAndProbeMuID = cms.Path()
#process.TagAndProbeTrig = cms.Path()
#
#process.e.remove(process.outSta)
#process.e.remove(process.outMuID)
#process.e.remove(process.outTrig)
