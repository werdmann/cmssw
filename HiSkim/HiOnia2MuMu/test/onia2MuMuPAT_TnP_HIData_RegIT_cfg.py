# for the list of used tags please see:
# https://twiki.cern.ch/twiki/bin/view/CMS/Onia2MuMuSamples

import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

# set up process
process = cms.Process("Onia2MuMuPAT")

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

# setup any defaults you want
options.inputFiles = 'file:/tmp/tdahms/6AEAB3A5-1A21-E211-A508-D4AE5264CC75.root'
options.secondaryInputFiles = 'file:/tmp/tdahms/3E3B3DED-0910-E111-84E0-003048F117F6.root'
options.outputFile = 'tnp_regit.root'

options.maxEvents = -1 # -1 means all events

# get and parse the command line arguments
options.parseArguments()

process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load("Configuration.StandardSequences.ReconstructionHeavyIons_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = 'GR_P_V27A::All'    # prompt 

# event plane stuff
process.load("RecoHI.HiEvtPlaneAlgos.HiEvtPlane_cfi")
process.load("RecoHI.HiEvtPlaneAlgos.hievtplaneflatproducer_cfi")
process.load('RecoHI.HiCentralityAlgos.CentralityBin_cfi')

process.HeavyIonGlobalParameters = cms.PSet(
    centralityVariable = cms.string("HFtowers"),
    nonDefaultGlauberModel = cms.string(""),
    centralitySrc = cms.InputTag("hiCentrality")
    )

# BSC or HF coincidence (masked unprescaled L1 bits)
process.load('L1Trigger.Skimmer.l1Filter_cfi')
process.bscOrHfCoinc = process.l1Filter.clone(
    algorithms = cms.vstring('L1_HcalHfCoincPmORBscMinBiasThresh1_BptxAND_instance1', 'L1_NotBsc2_BscMinBiasOR', 'L1_HcalHfCoincidencePm')
    )

# HLT dimuon trigger
import HLTrigger.HLTfilters.hltHighLevel_cfi
process.hltOniaHI = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.hltOniaHI.HLTPaths = ["HLT_HIL1DoubleMu0_HighQ_v*",
                              "HLT_HIL2Mu3_NHitQ_v*",
                              "HLT_HIL2Mu7_v*","HLT_HIL2Mu15_v*",
                              "HLT_HIL2DoubleMu0_NHitQ_v*",
                              "HLT_HIL2DoubleMu3_v*",
                              "HLT_HIL3Mu3_v*",
                              "HLT_HIL3DoubleMuOpen_v*","HLT_HIL3DoubleMuOpen_Mgt2_OS_NoCowboy_v*"
                              ]
process.hltOniaHI.throw = False
process.hltOniaHI.andOr = True
process.hltOniaHI.TriggerResultsTag = cms.InputTag("TriggerResults","","HLT")


from HiSkim.HiOnia2MuMu.onia2MuMuPAT_cff import *
onia2MuMuPAT(process, GlobalTag=process.GlobalTag.globaltag, MC=False, HLT="HLT", Filter=True)

process.onia2MuMuPatGlbGlb.dimuonSelection  = cms.string("mass > 0")
process.onia2MuMuPatGlbGlb.addMuonlessPrimaryVertex = False
process.onia2MuMuPatGlbGlb.resolvePileUpAmbiguity = False

process.source.fileNames = cms.untracked.vstring(
    options.inputFiles
    )

process.source.secondaryFileNames = cms.untracked.vstring(
    options.secondaryInputFiles
    )

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )
process.outTnP.fileName = cms.untracked.string( options.outputFile )

# add event plane flattening
process.load("CondCore.DBCommon.CondDBCommon_cfi");
process.CondDBCommon.connect = "sqlite_file:flatparms_PbPb_2011.db"
process.PoolDBESSource2 = cms.ESSource("PoolDBESSource",
                                      process.CondDBCommon,
                                      toGet = cms.VPSet(cms.PSet(record = cms.string('HeavyIonRPRcd'),
                                                                 tag = cms.string('flatParamtest')
                                                                 )
                                                        )
                                      )

# add event plane information
process.ProdEvtPlane = cms.Path(process.centralityBin * process.hiEvtPlane * process.hiEvtPlaneFlat)

process.e = cms.EndPath(process.outTnP)

process.patMuonSequence = cms.Sequence(
    process.bscOrHfCoinc *
#    process.hltOniaHI *
    process.collisionEventSelection *
    process.patMuonsWithTriggerSequence
    )

process.schedule = cms.Schedule(process.ProdEvtPlane,
                                process.TagAndProbeTrig,
                                process.TagAndProbeSta, 
                                process.TagAndProbeMuID,
                                process.e)

# RegIT: replace everywhere the names of the new muon collections 
from PhysicsTools.PatAlgos.tools.helpers import massSearchReplaceAnyInputTag
massSearchReplaceAnyInputTag(process.Onia2MuMuPAT, 'muons','remuons')
massSearchReplaceAnyInputTag(process.Onia2MuMuPAT, 'globalMuons','reglobalMuons')
