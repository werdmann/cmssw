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
#process.GlobalTag.globaltag = 'GR_P_V27A::All'
process.GlobalTag.globaltag = 'STARTHI44_V7::All'

# produce missing l1extraParticles
process.load('Configuration.StandardSequences.L1Reco_cff')
process.L1Reco_step = cms.Path(process.l1extraParticles)

from CmsHi.Analysis2010.CommonFunctions_cff import *
overrideCentrality(process)

process.HeavyIonGlobalParameters = cms.PSet(
    centralityVariable = cms.string("HFtowers"),
    nonDefaultGlauberModel = cms.string("Hydjet_Bass"),
    centralitySrc = cms.InputTag("hiCentrality")
    )

addRPFlat(process)


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
process.hltOniaHI.HLTPaths = ["HLT_HIL1DoubleMu0_HighQ_v1",
                              "HLT_HIL2Mu3_NHitQ_v1",
                              "HLT_HIL2Mu7_v1","HLT_HIL2Mu15_v1",
                              "HLT_HIL2DoubleMu0_NHitQ_v1",
                              "HLT_HIL2DoubleMu3_v1",
                              "HLT_HIL3Mu3_v1",
                              "HLT_HIL3DoubleMuOpen_v1","HLT_HIL3DoubleMuOpen_Mgt2_OS_NoCowboy_v1"
                              ]
process.hltOniaHI.throw = False
process.hltOniaHI.andOr = True

from HiSkim.HiOnia2MuMu.onia2MuMuPAT_cff import *

onia2MuMuPAT(process, GlobalTag=process.GlobalTag.globaltag, MC=True, HLT="HLT", Filter=False)

process.onia2MuMuPatGlbGlb.addMuonlessPrimaryVertex = False
process.onia2MuMuPatGlbGlb.resolvePileUpAmbiguity = False

process.source.fileNames = cms.untracked.vstring(
    '/store/relval/CMSSW_4_4_0/RelValHydjetQ_MinBias_2760GeV/GEN-SIM-RECO/STARTHI44_V4-v2/0045/1A99CD27-1BE6-E011-BC81-001A92971B72.root'
    #'/store/hidata/HIRun2011/HIDiMuon/RECO/PromptReco-v1/000/181/611/2E9B5D80-0110-E111-9CEE-003048F117F6.root'
    #'/store/hidata/HIRun2011/HIDiMuon/RECO/PromptReco-v1/000/181/604/6224AF39-D50F-E111-89BE-003048D2BBF0.root'
    )

# filter on lumisections
#from HiSkim.HiOnia2MuMu.goodLumiSectionListHI_cfi import *
#process.source.lumisToProcess = goodLumisToProcess

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.outOnia2MuMu.fileName = cms.untracked.string( 'onia2MuMuPAT_MC.root' )
process.outTnP.fileName = cms.untracked.string( 'tnp_MC.root' )

# add event plane information
process.load("RecoHI.HiEvtPlaneAlgos.HiEvtPlane_cfi")
process.ProdEvtPlane = cms.Path(process.centralityBin*process.hiEvtPlane)

process.outOnia2MuMu.outputCommands.extend(cms.untracked.vstring('keep *_hiEvtPlaneFlat_*_*'))
process.outOnia2MuMu.outputCommands.extend(cms.untracked.vstring('keep *_generator_*_*'))

process.outTnP.outputCommands.extend(cms.untracked.vstring('keep *_hiEvtPlaneFlat_*_*'))
process.outTnP.outputCommands.extend(cms.untracked.vstring('keep *_generator_*_*'))

process.e = cms.EndPath(process.outOnia2MuMu)# + process.outTnP)


process.patMuonSequence = cms.Sequence(
    #process.bscOrHfCoinc *
    process.hltOniaHI *
    process.collisionEventSelection *
    process.centralityBin *
    process.hiEvtPlaneFlat *
    process.genMuons *
    process.patMuonsWithTriggerSequence
    )

process.schedule = cms.Schedule(process.L1Reco_step,process.ProdEvtPlane,process.Onia2MuMuPAT,
                                #process.TagAndProbeSta, process.TagAndProbeMuID, process.TagAndProbeTrig,
                                process.e)


