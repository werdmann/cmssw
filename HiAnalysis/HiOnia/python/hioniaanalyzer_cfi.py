import FWCore.ParameterSet.Config as cms

hionia = cms.EDAnalyzer('HiOniaAnalyzer',
                        src = cms.InputTag("onia2MuMuPatTrkTrk"),
                        srcTracks = cms.InputTag("srcTracks"),
                        genParticles = cms.InputTag("genMuons"),
                        primaryVertexTag = cms.InputTag("hiSelectedVertex"),
                        triggerResultsLabel = cms.InputTag("TriggerResults"),
                        srcCentrality = cms.InputTag("hiCentrality"),

                        #-- Reco Details
                        useBeamSpot = cms.bool(False),
                        useRapidity = cms.bool(True),
                        
                        #--
                        maxAbsZ = cms.double(24.0),
                        
                        pTBinRanges = cms.vdouble(0.5, 3.0, 6.0, 8.0, 10.0, 15.0, 35.0),
                        etaBinRanges = cms.vdouble(0.0, 2.5),
                        
                        onlyTheBest = cms.bool(False),		
                        applyCuts = cms.bool(True),			
                        storeEfficiency = cms.bool(False),
                        
                        removeSignalEvents = cms.untracked.bool(False),
                        removeTrueMuons = cms.untracked.bool(False),
                        storeSameSign = cms.untracked.bool(False),
                        
                        muonLessPV = cms.bool(True),
                        
                        #-- Gen Details
                        oniaPDG = cms.int32(443),
                        isHI = cms.untracked.bool(True),
                        isPA = cms.untracked.bool(False),
                        isMC = cms.untracked.bool(False),
                        isPromptMC = cms.untracked.bool(False),

                        #-- Histogram configuration
                        combineCategories = cms.bool(False),
                        fillRooDataSet = cms.bool(False),
                        fillTree = cms.bool(True),
                        fillHistos = cms.bool(True),
                        minimumFlag = cms.bool(True),
                        fillSingleMuons = cms.bool(True),
                        fillRecoTracks = cms.bool(False),
                        histFileName = cms.string("Jpsi_Histos.root"),		
                        dataSetName = cms.string("Jpsi_DataSet.root"),
                        
                        #--
                        dblTriggerPathNames    = cms.vstring(),
                        dblTriggerFilterNames = cms.vstring(),
                        sglTriggerPathNames    = cms.vstring(),
                        sglTriggerFilterNames = cms.vstring()
                        )
