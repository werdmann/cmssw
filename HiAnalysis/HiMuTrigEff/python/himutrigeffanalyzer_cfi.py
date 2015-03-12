import FWCore.ParameterSet.Config as cms

mutrigeff = cms.EDAnalyzer('HiMuTrigEffAnalyzer',
                           srcMuon = cms.InputTag("patMuonsWithTrigger"),
                           primaryVertexTag = cms.InputTag("hiSelectedVertex"),
                           maxAbsZ = cms.double(24.0),
                           histFileName = cms.string("MuTrigEff_Histos.root"), 
                           trigFilterName = cms.string("hltHIL2DoubleMu3L2Filtered")
)
