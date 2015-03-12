
import FWCore.ParameterSet.Config as cms

# set up process
process = cms.Process("MUSKIM")

process.load("Configuration.StandardSequences.Services_cff")
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.load("Configuration.StandardSequences.ReconstructionHeavyIons_cff")
process.load("Configuration.StandardSequences.GeometryDB_cff")
process.load("Configuration.StandardSequences.MagneticField_38T_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load('Configuration.EventContent.EventContentHeavyIons_cff')

process.GlobalTag.globaltag = 'GR_R_39X_V6B::All'

process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.source = cms.Source("PoolSource",
                            fileNames = cms.untracked.vstring(
        'rfio:/castor/cern.ch/cms/store/hidata/HIRun2010/HIAllPhysics/RECO/ZS-v2/0033/7E0F627F-5C43-E011-AF82-003048F1CA12.root'
        )
                            )

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

# BSC or HF coincidence (masked unprescaled L1 bits)
process.load('L1Trigger.Skimmer.l1Filter_cfi')
process.bscOrHfCoinc = process.l1Filter.clone(
    algorithms = cms.vstring('L1_BscMinBiasThreshold1', 'L1_HcalHfCoincidencePm')
    )
    
# Common offline event selection
process.load("HeavyIonsAnalysis.Configuration.collisionEventSelection_cff")

# HLT dimuon trigger
import HLTrigger.HLTfilters.hltHighLevel_cfi

process.hltMuons = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.hltMuons.HLTPaths = ["HLT_HIL1DoubleMuOpen","HLT_HIL2DoubleMu0","HLT_HIL2DoubleMu3",
                             "HLT_HIL1SingleMu3","HLT_HIL1SingleMu5","HLT_HIL1SingleMu7",
                             "HLT_HIL2Mu20","HLT_HIL2Mu3","HLT_HIL2Mu5Tight"]
process.hltMuons.throw = False
process.hltMuons.andOr = True

process.p = cms.Path(process.bscOrHfCoinc *
                     process.hltMuons)

from Configuration.EventContent.EventContentHeavyIons_cff import *

process.out = cms.OutputModule("PoolOutputModule",
                               fileName = cms.untracked.string('/tmp/tdahms/Skim_HLT_Muons_RECO_4.root'),
                               outputCommands = cms.untracked.vstring('drop *'),
                               SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') )
                               )

process.out.outputCommands.extend(RECOEventContent.outputCommands)

process.e = cms.EndPath(process.out)

