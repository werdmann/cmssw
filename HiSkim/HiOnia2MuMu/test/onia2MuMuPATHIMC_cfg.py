# for the list of used tags please see:
# https://twiki.cern.ch/twiki/bin/view/CMS/Onia2MuMuSamples

import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

# set up process
process = cms.Process("Onia2MuMuPAT")

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

# setup any defaults you want
options.outputFile = 'onia2MuMuPAT_MC.root'
#options.inputFiles = 'root://eoscms//eos/cms/store/relval/CMSSW_4_4_0/RelValHydjetQ_MinBias_2760GeV/GEN-SIM-RECO/STARTHI44_V4-v2/0045/1A99CD27-1BE6-E011-BC81-001A92971B72.root?svcClass=default'
options.maxEvents = -1 # -1 means all events

# get and parse the command line arguments
options.parseArguments()

process.load('Configuration.StandardSequences.GeometryExtended_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = 'STARTHI44_V4::All'


# produce missing l1extraParticles
process.load('Configuration.StandardSequences.L1Reco_cff')
process.L1Reco_step = cms.Path(process.l1extraParticles)

from CmsHi.Analysis2010.CommonFunctions_cff import *
overrideCentrality(process)

process.HeavyIonGlobalParameters = cms.PSet(
    centralityVariable = cms.string("HFhits"),
    nonDefaultGlauberModel = cms.string("Hydjet_Bass"), # different from data!
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
process.hltMinBiasHFOrBSCEarly.throw = False
process.hltMinBiasHFOrBSCEarly.andOr = True

process.hltMinBiasHFOrBSC = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.hltMinBiasHFOrBSC.HLTPaths = ["HLT_HIMinBiasHfOrBSC"]
process.hltMinBiasHFOrBSC.throw = False


process.hltOniaHI = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.hltOniaHI.HLTPaths = ["HLT_HIL1DoubleMuOpen_v1",
                              "HLT_HIL1DoubleMu0_HighQ_v1",
                              "HLT_HIL2Mu3_v1","HLT_HIL2Mu3_NHitQ_v1",
                              "HLT_HIL2Mu7_v1","HLT_HIL2Mu15_v1",
                              "HLT_HIL2DoubleMu0_v1","HLT_HIL2DoubleMu0_NHitQ_v1","HLT_HIL2DoubleMu0_L1HighQL2NHitQ_v1",
                              "HLT_HIL2DoubleMu3_v1",
                              "HLT_HIL3Mu3_v1",
                              "HLT_HIL3DoubleMuOpen_v1","HLT_HIL3DoubleMuOpen_Mgt2_v1","HLT_HIL3DoubleMuOpen_Mgt2_SS_v1","HLT_HIL3DoubleMuOpen_Mgt2_OS_v1","HLT_HIL3DoubleMuOpen_Mgt2_OS_NoCowboy_v1"
                              ]

process.hltOniaHI.throw = False
process.hltOniaHI.andOr = True


from HiSkim.HiOnia2MuMu.onia2MuMuPAT_cff import *

onia2MuMuPAT(process, GlobalTag=process.GlobalTag.globaltag, MC=True, HLT="HLT1", Filter=True)

process.onia2MuMuPatGlbGlb.addMuonlessPrimaryVertex = False
process.onia2MuMuPatGlbGlb.resolvePileUpAmbiguity = False

# modify stuff!
process.patMuonSequence.remove(process.bscOrHfCoinc)
#process.Onia2MuMuPAT.remove(process.hltOniaHI)
process.patMuonSequence.remove(process.collisionEventSelection)

#process.genMuons.src = "genParticles"


process.source.duplicateCheckMode = cms.untracked.string('noDuplicateCheck')
process.source.fileNames = cms.untracked.vstring(
    options.inputFiles
    )

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )

process.outOnia2MuMu.fileName = cms.untracked.string( options.outputFile )
process.outTnP.fileName = cms.untracked.string('tnp_MC.root')
#process.outSta.fileName = cms.untracked.string('tnpSta_MC.root')
#process.outMuID.fileName = cms.untracked.string('tnpMuID_MC.root')
#process.outTrig.fileName = cms.untracked.string('tnpTrig_MC.root')


# add event plane information
process.load("RecoHI.HiEvtPlaneAlgos.HiEvtPlane_cfi")
process.ProdEvtPlane = cms.Path(process.hiEvtPlane)


process.schedule = cms.Schedule(process.L1Reco_step,process.ProdEvtPlane,process.Onia2MuMuPAT,
                                process.TagAndProbeSta, process.TagAndProbeMuID, process.TagAndProbeTrig,
                                process.e)
