# for the list of used tags please see:
# https://twiki.cern.ch/twiki/bin/view/CMS/Onia2MuMuSamples

import FWCore.ParameterSet.Config as cms

# set up process
process = cms.Process("Onia2MuMuPAT")

process.load('Configuration.StandardSequences.GeometryExtended_cff')
process.load("Configuration.StandardSequences.Reconstruction_cff")
process.load("Configuration.StandardSequences.ReconstructionHeavyIons_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")

process.load("RecoHI.HiEvtPlaneAlgos.HiEvtPlane_cfi")
process.load("RecoHI.HiEvtPlaneAlgos.hievtplaneflatproducer_cfi")
process.load('RecoHI.HiCentralityAlgos.CentralityBin_cfi')

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
#process.GlobalTag.globaltag = 'GR_R_44_V10::All'
process.GlobalTag.globaltag = 'GR_P_V27A::All'

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
    

# Common offline event selection
process.load("HeavyIonsAnalysis.Configuration.collisionEventSelection_cff")

# HLT dimuon trigger
import HLTrigger.HLTfilters.hltHighLevel_cfi
process.hltOniaHI = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.hltOniaHI.HLTPaths = ["HLT_HIL1DoubleMu0_HighQ_v2",
                              "HLT_HIL2Mu3_NHitQ_v2",
                              "HLT_HIL2Mu7_v2","HLT_HIL2Mu15_v2",
                              "HLT_HIL2DoubleMu0_NHitQ_v2",
                              "HLT_HIL2DoubleMu3_v2",
                              "HLT_HIL3Mu3_v2",
                              "HLT_HIL3DoubleMuOpen_v2","HLT_HIL3DoubleMuOpen_Mgt2_OS_NoCowboy_v2"
                              ]
process.hltOniaHI.throw = False
process.hltOniaHI.andOr = True

process.hltWmunuHI = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.hltWmunuHI.HLTPaths = ["HLT_HIL2Mu3_NHitQ_v2","HLT_HIL2Mu7_v2","HLT_HIL2Mu15_v2"]
process.hltWmunuHI.throw = False
process.hltWmunuHI.andOr = True

from HiSkim.HiOnia2MuMu.onia2MuMuPAT_cff import *

onia2MuMuPAT(process, GlobalTag=process.GlobalTag.globaltag, MC=False, HLT="HLT", Filter=True)

process.onia2MuMuPatGlbGlb.addMuonlessPrimaryVertex = False
process.onia2MuMuPatGlbGlb.resolvePileUpAmbiguity = False

process.source.fileNames = cms.untracked.vstring(
    '/store/hidata/HIRun2011/HIDiMuon/RECO/PromptReco-v1/000/181/611/2E9B5D80-0110-E111-9CEE-003048F117F6.root'
    #'/store/hidata/HIRun2011/HIDiMuon/RECO/PromptReco-v1/000/181/604/6224AF39-D50F-E111-89BE-003048D2BBF0.root'
    )

# filter on lumisections
#from HiSkim.HiOnia2MuMu.goodLumiSectionListHI_cfi import *
#process.source.lumisToProcess = goodLumisToProcess

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.outOnia2MuMu.fileName = cms.untracked.string( 'onia2MuMuPAT.root' )

# add event plane information
process.load("RecoHI.HiEvtPlaneAlgos.HiEvtPlane_cfi")
process.ProdEvtPlane = cms.Path(process.centralityBin*process.hiEvtPlane)


# add event plane flattening
process.load("CondCore.DBCommon.CondDBCommon_cfi");
process.CondDBCommon.connect = "sqlite_file:flatparms.db"
process.PoolDBESSource2 = cms.ESSource("PoolDBESSource",
                                       process.CondDBCommon,
                                       toGet = cms.VPSet(cms.PSet(record = cms.string('HeavyIonRPRcd'),
                                                                  tag = cms.string('flatParamtest')
                                                                  )
                                                         )
                                       )



process.outOnia2MuMu.outputCommands.extend(cms.untracked.vstring('keep *_hiEvtPlaneFlat_*_*'))

process.e = cms.EndPath(process.outOnia2MuMu)

process.patMuonSequence = cms.Sequence(
    process.bscOrHfCoinc *
    process.hltOniaHI *
    process.collisionEventSelection *
    process.centralityBin *
    process.hiEvtPlaneFlat *
    process.patMuonsWithTriggerSequence
    )

process.schedule = cms.Schedule(process.ProdEvtPlane,process.Onia2MuMuPAT,process.e)


