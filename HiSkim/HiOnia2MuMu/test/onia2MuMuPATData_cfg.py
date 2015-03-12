# for the list of used tags please see:
# https://twiki.cern.ch/twiki/bin/view/CMS/Onia2MuMuSamples

import FWCore.ParameterSet.Config as cms

process = cms.Process("Onia2MuMuPAT")

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = 'GR_P_V14::All'

from HeavyFlavorAnalysis.Onia2MuMu.onia2MuMuPAT_cff import *


import HLTrigger.HLTfilters.hltHighLevel_cfi
process.hltOniaHI = HLTrigger.HLTfilters.hltHighLevel_cfi.hltHighLevel.clone()
process.hltOniaHI.HLTPaths = ["HLT_DoubleMu3_v3","HLT_L1DoubleMu0_v1","HLT_L2DoubleMu0_v2",
                              "HLT_Mu0_v3","HLT_Mu3_v3","HLT_Mu5_v3"]

onia2MuMuPAT(process, GlobalTag=process.GlobalTag.globaltag, MC=False, HLT="HLT", Filter=True)

process.source.fileNames = cms.untracked.vstring(
    'rfio:/castor/cern.ch/cms/store/data/Run2011A/AllPhysics2760/AOD/PromptReco-v2/000/161/474/FC4C13B1-975A-E011-93F8-0030487C608C.root'
)

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

