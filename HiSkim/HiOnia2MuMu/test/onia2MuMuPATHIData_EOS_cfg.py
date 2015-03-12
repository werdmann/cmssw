# for the list of used tags please see:
# https://twiki.cern.ch/twiki/bin/view/CMS/Onia2MuMuSamples

import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

# set up process
process = cms.Process("Onia2MuMuPAT")

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

# setup any defaults you want
options.inputFiles = '/store/hidata/HIRun2010/HIAllPhysics/RECO/SDmaker_3SD_1CS_PDHIAllPhysicsZSv2_SD_MuHI-v1/0054/FED0C648-DE4C-E011-A1EE-003048F1BF7A.root'

options.maxEvents = -1 # -1 means all events

# get and parse the command line arguments
options.parseArguments()

process.load('Configuration.StandardSequences.GeometryExtended_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = 'GR_R_39X_V6B::All'

# produce missing l1extraParticles
process.load('Configuration.StandardSequences.L1Reco_cff')
process.L1Reco_step = cms.Path(process.l1extraParticles)

from CmsHi.Analysis2010.CommonFunctions_cff import *
overrideCentrality(process)

process.HeavyIonGlobalParameters = cms.PSet(
    centralityVariable = cms.string("HFhits"),
    nonDefaultGlauberModel = cms.string(""),
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
                                             histFileName = cms.string("MinBiasCentralityEarly_Histo.root")
                                             )

process.MinBiasCounter = cms.EDAnalyzer('MinBiasCounter',
                                        TriggerResultsLabel = cms.InputTag("TriggerResults","","HLT"),
                                        triggerName = cms.vstring("HLT_HIMinBiasHfOrBSC"),
                                        histFileName = cms.string("MinBiasCentrality_Histo.root")
                                        )

process.DoubleMuOpenCounter = cms.EDAnalyzer('MinBiasCounter',
                                             TriggerResultsLabel = cms.InputTag("TriggerResults","","HLT"),
                                             triggerName = cms.vstring("HLT_HIL1DoubleMuOpen"),
                                             # triggerName = cms.vstring("HLT_HIL1DoubleMuOpen_Core"),
                                             histFileName = cms.string("DoubleMuOpenCentrality_Histo.root")
                                             )

process.MinBiasEarlyPath = cms.Path(process.hltMinBiasHFOrBSCEarly *
                                    process.collisionEventSelection *
                                    process.MinBiasCounterEarly
                                    )

process.MinBiasPath = cms.Path(process.hltMinBiasHFOrBSC *
                               process.collisionEventSelection *
                               process.MinBiasCounter
                               )

from HiSkim.HiOnia2MuMu.onia2MuMuPAT_cff import *

onia2MuMuPAT(process, GlobalTag=process.GlobalTag.globaltag, MC=False, HLT="HLT", Filter=True)

process.onia2MuMuPatGlbGlb.addMuonlessPrimaryVertex = False
process.onia2MuMuPatGlbGlb.resolvePileUpAmbiguity = False

process.source.fileNames = cms.untracked.vstring(
    options.inputFiles
    #'/store/hidata/HIRun2010/HIAllPhysics/RECO/SDmaker_3SD_1CS_PDHIAllPhysicsZSv2_SD_MuHI-v1/0054/FED0C648-DE4C-E011-A1EE-003048F1BF7A.root'
    )

# filter on lumisections
from HiSkim.HiOnia2MuMu.goodLumiSectionListHI_cfi import *
process.source.lumisToProcess = goodLumisToProcess

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )
process.outOnia2MuMu.fileName = cms.untracked.string( 'onia2MuMuPAT.root' )

process.schedule = cms.Schedule(process.L1Reco_step, process.MinBiasEarlyPath, process.MinBiasPath, process.Onia2MuMuPAT, process.TagAndProbeSta, process.TagAndProbeMuID, process.TagAndProbeTrig, process.e)

