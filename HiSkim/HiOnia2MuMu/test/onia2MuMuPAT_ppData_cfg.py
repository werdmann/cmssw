# for the list of used tags please see:
# https://twiki.cern.ch/twiki/bin/view/CMS/Onia2MuMuSamples

import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

# set up process
process = cms.Process("Onia2MuMuPAT")

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

# setup any defaults you want
options.outputFile = 'onia2MuMuPAT.root'
options.inputFiles = '/store/data/Run2013A/PPMuon/RECO/PromptReco-v1/000/211/739/00000/0842C448-3A76-E211-9FF0-0025901D6272.root'
#'/store/data/Run2013A/PPMuon/RECO/PromptReco-v1/000/211/831/00000/F40F947D-1578-E211-8D75-003048D37666.root'
options.maxEvents = -1 # -1 means all events

# get and parse the command line arguments
options.parseArguments()

process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = 'GR_P_V43D::All'

# Common offline event selection
process.load("HeavyIonsAnalysis.Configuration.collisionEventSelection_cff")

# pile up rejection
process.load('Appeltel.RpPbAnalysis.PAPileUpVertexFilter_cff')

# Centrality for pPb
process.load('RecoHI.HiCentralityAlgos.HiCentrality_cfi')

# HLT dimuon trigger
import HLTrigger.HLTfilters.hltHighLevel_cfi
process.hltOniaHI = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.hltOniaHI.HLTPaths = ["HLT_PAL1DoubleMuOpen_v*",
                              "HLT_PAL1DoubleMu0_HighQ_v*",
                              "HLT_PAL2DoubleMu3_v*",
                              "HLT_PAMu3_v*",
                              "HLT_PAMu7_v*",
                              "HLT_PAMu12_v*"
                              ]
process.hltOniaHI.throw = False
process.hltOniaHI.andOr = True
process.hltOniaHI.TriggerResultsTag = cms.InputTag("TriggerResults","","HLT")


from HiSkim.HiOnia2MuMu.onia2MuMuPAT_cff import *
onia2MuMuPAT(process, GlobalTag=process.GlobalTag.globaltag, MC=False, HLT="HLT", Filter=True)

#process.onia2MuMuPatTrkTrk.addMuonlessPrimaryVertex = False
#process.onia2MuMuPatTrkTrk.resolvePileUpAmbiguity = False

# don't filter on good vertex here, do it in the skimming step on the PV closest to onia in Delta Z
process.PAcollisionEventSelection = cms.Sequence(process.hfCoincFilter *
                                                 #process.PAprimaryVertexFilter *
                                                 process.NoScraping
                                                 )

process.patMuonSequence = cms.Sequence(
    process.hltOniaHI *
    process.PAcollisionEventSelection *
    process.pileupVertexFilterCutGplus * 
    process.pACentrality_step *
    process.patMuonsWithTriggerSequence
    )

process.source.fileNames = cms.untracked.vstring(
    options.inputFiles
    )

# filter on lumisections
#import FWCore.PythonUtilities.LumiList as LumiList
#process.source.lumisToProcess = LumiList.LumiList(filename = 'Cert_211739-211831_2760GeV_PromptReco_Collisions13_JSON_MuonPhys.txt').getVLuminosityBlockRange()

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )
process.outOnia2MuMu.fileName = cms.untracked.string( options.outputFile )

# suppress harmless warnings about missing parentage info for vertex collection
#process.MessageLogger.suppressWarning = cms.untracked.vstring('onia2MuMuPatTrkTrk')

process.e = cms.EndPath(process.outOnia2MuMu)

process.schedule = cms.Schedule(process.Onia2MuMuPAT,process.e)

