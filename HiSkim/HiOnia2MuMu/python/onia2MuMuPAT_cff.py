import FWCore.ParameterSet.Config as cms

from PhysicsTools.PatAlgos.tools.helpers import *

def onia2MuMuPAT(process, GlobalTag, MC=False, HLT='HLT', Filter=True):
    # Setup the process
    process.options = cms.untracked.PSet(
        wantSummary = cms.untracked.bool(True),
        # fileMode = cms.untracked.string('MERGE'),
    )
    process.load("FWCore.MessageService.MessageLogger_cfi")
    process.MessageLogger.cerr.FwkReport.reportEvery = 100
    process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
    process.load("Configuration.StandardSequences.Reconstruction_cff")
    process.load("Configuration.StandardSequences.MagneticField_cff")
    process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
    process.GlobalTag.globaltag = GlobalTag

    # Drop the DQM stuff on input
    process.source = cms.Source("PoolSource",
        inputCommands = cms.untracked.vstring("keep *", "drop *_MEtoEDMConverter_*_*"),
        fileNames = cms.untracked.vstring()
    )

    # Scraping filter
    process.scrapingFilter = cms.EDFilter("FilterOutScraping",
        applyfilter = cms.untracked.bool(True),
        debugOn = cms.untracked.bool(False),
        numtrack = cms.untracked.uint32(10),
        thresh = cms.untracked.double(0.25)
    )

    IN_ACCEPTANCE = '((abs(eta) <= 1.3 && pt > 3.3) || (1.3 < abs(eta) <= 2.2 && p > 2.9) || (2.2 < abs(eta) <= 2.4 && pt > 0.8))'

    # Merge muons, calomuons in a single collection for T&P
    process.mergedMuons = cms.EDProducer("CaloMuonMerger",
        muons     = cms.InputTag("muons"), 
        muonsCut = cms.string(""),
        mergeCaloMuons = cms.bool(True),  ### NEEDED TO RUN ON AOD
        caloMuons = cms.InputTag("calomuons"),
        caloMuonsCut = cms.string(IN_ACCEPTANCE),
        minCaloCompatibility = cms.double(0.6),
        mergeTracks = cms.bool(False),
        tracks = cms.InputTag("generalTracks"),
	tracksCut = cms.string(IN_ACCEPTANCE),
    )


    # Prune generated particles to muons and their parents
    process.genMuons = cms.EDProducer("GenParticlePruner",
        src = cms.InputTag("genParticles"),
        select = cms.vstring(
            "drop  *  ",                     # this is the default
            "++keep abs(pdgId) = 13",        # keep muons and their parents
            "drop pdgId == 21 && status = 2" # remove intermediate qcd spam carrying no flavour info
        )
    )

    # Make PAT Muons
    process.load("MuonAnalysis.MuonAssociators.patMuonsWithTrigger_cff")
    from MuonAnalysis.MuonAssociators.patMuonsWithTrigger_cff import addMCinfo, changeRecoMuonInput, useL1MatchingWindowForSinglets, changeTriggerProcessName, switchOffAmbiguityResolution
    # with some customization
    if MC:
        addMCinfo(process)
        # since we match inner tracks, keep the matching tight and make it one-to-one
        process.muonMatch.maxDeltaR = 0.05
        process.muonMatch.resolveByMatchQuality = True
        process.muonMatch.matched = "genMuons"
    changeTriggerProcessName(process, HLT)
    switchOffAmbiguityResolution(process) # Switch off ambiguity resolution: allow multiple reco muons to match to the same trigger muon
    #useL1MatchingWindowForSinglets(process)

    process.muonL1Info.maxDeltaR = 0.3
    process.muonL1Info.fallbackToME1 = True
    process.muonMatchHLTL1.maxDeltaR = 0.3
    process.muonMatchHLTL1.fallbackToME1 = True
    process.muonMatchHLTL2.maxDeltaR = 0.3
    process.muonMatchHLTL2.maxDPtRel = 10.0
    process.muonMatchHLTL3.maxDeltaR = 0.1
    process.muonMatchHLTL3.maxDPtRel = 10.0
    process.muonMatchHLTCtfTrack.maxDeltaR = 0.1
    process.muonMatchHLTCtfTrack.maxDPtRel = 10.0
    process.muonMatchHLTTrackMu.maxDeltaR = 0.1
    process.muonMatchHLTTrackMu.maxDPtRel = 10.0


    # Make a sequence
    process.patMuonSequence = cms.Sequence(
        process.hltOniaHI *
        process.PAcollisionEventSelection *
        process.genMuons *
        process.patMuonsWithTriggerSequence
    )
    if not MC:
        process.patMuonSequence.remove(process.genMuons)
      
    # Make dimuon candidates
    process.onia2MuMuPatTrkTrk = cms.EDProducer('HiOnia2MuMuPAT',
        muons = cms.InputTag("patMuonsWithTrigger"),
        beamSpotTag = cms.InputTag("offlineBeamSpot"),
        primaryVertexTag = cms.InputTag("offlinePrimaryVertices"),
        # At least one muon must pass this selection
        higherPuritySelection = cms.string("(isGlobalMuon || isTrackerMuon || (innerTrack.isNonnull && genParticleRef(0).isNonnull)) && abs(innerTrack.dxy)<4 && abs(innerTrack.dz)<35"),
        # BOTH muons must pass this selection
        lowerPuritySelection  = cms.string("(isGlobalMuon || isTrackerMuon || (innerTrack.isNonnull && genParticleRef(0).isNonnull)) && abs(innerTrack.dxy)<4 && abs(innerTrack.dz)<35"),
        dimuonSelection  = cms.string(""), ## The dimuon must pass this selection before vertexing
        addCommonVertex = cms.bool(True), ## Embed the full reco::Vertex out of the common vertex fit
        addMuonlessPrimaryVertex = cms.bool(True), ## Embed the primary vertex re-made from all the tracks except the two muons
        addMCTruth = cms.bool(MC),      ## Add the common MC mother of the two muons, if any
        resolvePileUpAmbiguity = cms.bool(True)   ## Order PVs by their vicinity to the J/psi vertex, not by sumPt                            
    )

    # check if there is at least one (inclusive) tracker+tracker di-muon
    process.onia2MuMuPatTrkTrkFilter = cms.EDFilter("CandViewCountFilter",
        src = cms.InputTag('onia2MuMuPatTrkTrk'),
        minNumber = cms.uint32(1),
    )

    # the onia2MuMu path
    process.Onia2MuMuPAT = cms.Path(
        process.patMuonSequence *
        process.onia2MuMuPatTrkTrk *
        process.onia2MuMuPatTrkTrkFilter
    )

    # Make Tag and Probe pairs for efficiency measurements
    TRACK_CUTS = "(track.hitPattern.trackerLayersWithMeasurement > 5 && track.normalizedChi2 < 1.8 && track.hitPattern.pixelLayersWithMeasurement > 1 && abs(dB) < 3 && abs(track.dz) < 15)"
    GLB_CUTS = "(isTrackerMuon && muonID('TrackerMuonArbitrated') && muonID('TMOneStationTight'))"
    QUALITY_CUTS =  "(" + GLB_CUTS + ' && ' + TRACK_CUTS + ")"

    process.tagMuonsSglTrg = cms.EDFilter("PATMuonSelector",
                                       src = cms.InputTag("patMuonsWithTrigger"),
                                       cut = cms.string(QUALITY_CUTS + ' && ' + IN_ACCEPTANCE + " && (!triggerObjectMatchesByPath('HLT_PAMu3_v*').empty() || !triggerObjectMatchesByPath('HLT_PAMu7_v*').empty() || !triggerObjectMatchesByPath('HLT_PAMu12_v*').empty())")
                                       )

    process.tagMuonsDblTrg = cms.EDFilter("PATMuonSelector",
                                       src = cms.InputTag("patMuonsWithTrigger"),
                                       cut = cms.string(QUALITY_CUTS + ' && ' + IN_ACCEPTANCE + " && !triggerObjectMatchesByPath('HLT_PAL1DoubleMuOpen_v*').empty()")
                                       )

    # produce patMuons that use the STA momentum information
    process.patMuonsWithTriggerSta = cms.EDProducer("RedefineMuonP4FromTrackPAT",
                                                    src   = cms.InputTag("patMuonsWithTrigger"),
                                                    track = cms.string("outer")
                                                    )

    # must be STA, so we can measure inner tracking efficiency
    process.probeMuonsSta = cms.EDFilter("PATMuonSelector",
                                         src = cms.InputTag("patMuonsWithTriggerSta"),
                                         cut = cms.string("outerTrack.isNonnull")
                                         )

    process.tpPairsSta = cms.EDProducer("CandViewShallowCloneCombiner",
                                        cut = cms.string('2.0 < mass < 5.0'),
                                        decay = cms.string('tagMuonsDblTrg@+ probeMuonsSta@-')
                                        )

    # must be a GLB to measure trigger efficiency
    process.probeMuons = cms.EDFilter("PATMuonSelector",
                                      src = cms.InputTag("patMuonsWithTrigger"),
                                      cut = cms.string(QUALITY_CUTS + ' && ' + IN_ACCEPTANCE)
                                      )

    process.tpPairsTrig = cms.EDProducer("CandViewShallowCloneCombiner",
                                     cut = cms.string('2.6 < mass < 4.0'),
                                     decay = cms.string('tagMuonsSglTrg@+ probeMuons@-')
                                     )

    # must be tracker muon, so we can measure the muon reco efficiency
    # since we're using tracker muons this year, we should use calo muons as probes here
    process.probeMuonsTrk = cms.EDFilter("PATMuonSelector",
                                         src = cms.InputTag("patMuonsWithTrigger"),
                                         #cut = cms.string("isCaloMuon && " + TRACK_CUTS)
                                         cut = cms.string("caloCompatibility>0.6 && innerTrack.isNonnull && " + TRACK_CUTS)
                                         )

    process.tpPairsTracks = cms.EDProducer("CandViewShallowCloneCombiner",
                                           cut = cms.string('2.6 < mass < 4.0'),
                                           decay = cms.string('tagMuonsDblTrg@+ probeMuonsTrk@-')
                                           )

    # check if there is at least one Tag and Probe pair
    process.tpPairsStaFilter = cms.EDFilter("CandViewCountFilter",
                                            src = cms.InputTag('tpPairsSta'),
                                            minNumber = cms.uint32(1),
                                            )

    process.tpPairsTrigFilter = cms.EDFilter("CandViewCountFilter",
                                             src = cms.InputTag('tpPairsTrig'),
                                             minNumber = cms.uint32(1),
                                             )

    process.tpPairsTracksFilter = cms.EDFilter("CandViewCountFilter",
                                               src = cms.InputTag('tpPairsTracks'),
                                               minNumber = cms.uint32(1),
                                               )
    
    # the Tag and Probe path
    process.tnpSta = cms.Sequence(
        process.probeMuonsSta *
        process.tpPairsSta *
        process.tpPairsStaFilter
        )

    process.tnpTrig = cms.Sequence(
        process.probeMuons *
        process.tpPairsTrig *
        process.tpPairsTrigFilter
        )

    process.tnpMuID = cms.Sequence(
        process.probeMuonsTrk *
        process.tpPairsTracks *
        process.tpPairsTracksFilter
        )

    # inner track reco efficiency
    process.TagAndProbeSta = cms.Path(
        process.patMuonSequence *
        process.tagMuonsDblTrg *
        process.patMuonsWithTriggerSta *
        process.tnpSta
    )

    # muon reco and ID efficiency
    process.TagAndProbeMuID = cms.Path(
        process.patMuonSequence *
        process.tagMuonsDblTrg *
        process.tnpMuID
    )

    # muon trigger efficiency
    process.TagAndProbeTrig = cms.Path(
        process.patMuonSequence *
        process.tagMuonsSglTrg *
        process.tnpTrig
    )
    
    if MC:
        process.tagMuonsDblTrgMCMatch = process.muonMatch.clone(src = "tagMuonsDblTrg")
        process.tagMuonsSglTrgMCMatch = process.muonMatch.clone(src = "tagMuonsSglTrg")
        process.probeMuonsStaMCMatch = process.tagMuonsDblTrgMCMatch.clone(src = "probeMuonsSta") # inner tracking eff
        process.probeMuonsTrkMCMatch = process.tagMuonsDblTrgMCMatch.clone(src = "probeMuonsTrk") # Muon reco and ID eff
        process.probeMuonsMCMatch = process.tagMuonsSglTrgMCMatch.clone(src = "probeMuons") # muon trigger eff
        process.TagAndProbeSta.replace(process.tpPairsSta, process.tagMuonsDblTrgMCMatch * process.probeMuonsStaMCMatch * process.tpPairsSta)
        process.TagAndProbeMuID.replace(process.tpPairsTracks, process.tagMuonsDblTrgMCMatch * process.probeMuonsTrkMCMatch * process.tpPairsTracks)
        process.TagAndProbeTrig.replace(process.tpPairsTrig, process.tagMuonsSglTrgMCMatch * process.probeMuonsMCMatch * process.tpPairsTrig)
    
    # output
    process.load('Configuration.EventContent.EventContent_cff')
    
    process.outOnia2MuMu = cms.OutputModule("PoolOutputModule",
        fileName = cms.untracked.string('onia2MuMuPAT.root'),
        outputCommands =  cms.untracked.vstring('drop *'),
                                                
        SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('Onia2MuMuPAT') ) if Filter else cms.untracked.PSet()
    )

    process.outOnia2MuMu.outputCommands.extend(cms.untracked.vstring(
        'keep *_mergedtruth_*_*',                              # tracking particles and tracking vertices for hit by hit matching
        'keep *_genParticles_*_*',                             # generated particles
        'keep *_genMuons_*_Onia2MuMuPAT',                      # generated muons and parents
        'keep patMuons_patMuonsWithTrigger_*_Onia2MuMuPAT',    # All PAT muons including matches to triggers
        'keep patCompositeCandidates_*__Onia2MuMuPAT',         # PAT di-muons
        'keep *_offlinePrimaryVertices_*_*',                   # Primary vertices: you want these to compute impact parameters
        'keep *_offlineBeamSpot_*_*',                          # Beam spot: you want this for the same reason                                   
        'keep edmTriggerResults_TriggerResults_*_*',           # HLT info, per path (cheap)
        'keep l1extraL1MuonParticles_hltL1extraParticles_*_*', # L1 info (cheap)
        'keep l1extraL1MuonParticles_l1extraParticles_*_*',    # L1 info (cheap)
        'keep *_offlinePrimaryVertices_*_*',
        'keep *_pACentrality_*_*',
        'keep *_generalTracks_*_*',
        'keep *_standAloneMuons_*_*')
                            ),

    process.outTnP = cms.OutputModule("PoolOutputModule",
        fileName = cms.untracked.string('tnp.root'),
        outputCommands = cms.untracked.vstring('drop *',
            'keep *_genParticles_*_*',                             # generated particles
            'keep *_genMuons_*_Onia2MuMuPAT',                      # generated muons and parents
            'keep *_tagMuonsDblTrgMCMatch__Onia2MuMuPAT',                # tagMuons MC matches for efficiency
            'keep *_tagMuonsSglTrgMCMatch__Onia2MuMuPAT',                # tagMuons MC matches for efficiency
            'keep *_probeMuonsMCMatch__Onia2MuMuPAT',              # probeMuons MC matches for efficiency
            'keep patMuons_patMuonsWithTriggerSta__Onia2MuMuPAT',    # All PAT muons including matches to triggers
            'keep patMuons_tagMuonsDblTrg__Onia2MuMuPAT',                # tagMuons for efficiency
            'keep patMuons_tagMuonsSglTrg__Onia2MuMuPAT',                # tagMuons for efficiency
            'keep patMuons_probeMuonsSta__Onia2MuMuPAT',           # probeMuons for efficiency
            'keep patMuons_probeMuonsTrk__Onia2MuMuPAT',                    # probeTracks for efficiency
            'keep patMuons_probeMuons__Onia2MuMuPAT',              # probeMuons for efficiency
            'keep *_probeMuonsStaMCMatch__Onia2MuMuPAT',              # probeMuons MC matches for efficiency
            'keep *_probeMuonsTrkMCMatch__Onia2MuMuPAT',              # probeTacks MC matches for efficiency
            'keep recoCompositeCandidates_tpPairsSta__Onia2MuMuPAT',        # RECO di-muons, tpPairs for tracking efficiency
            'keep recoCompositeCandidates_tpPairsTracks__Onia2MuMuPAT',        # RECO di-muons, tpPairs for muon ID and reco efficiency
            'keep recoCompositeCandidates_tpPairsTrig__Onia2MuMuPAT',        # RECO di-muons, tpPairs for trigger efficiency
            'keep *_offlinePrimaryVertices_*_*',                   # Primary vertices: you want these to compute impact parameters
            'keep *_offlineBeamSpot_*_*',                          # Beam spot: you want this for the same reason   
            'keep edmTriggerResults_TriggerResults_*_*',           # HLT info, per path (cheap)
            'keep l1extraL1MuonParticles_hltL1extraParticles_*_*', # L1 info (cheap)
            'keep l1extraL1MuonParticles_l1extraParticles_*_*',    # L1 info (cheap)
            'keep *_pACentrality_*_*',
            'keep *_generalTracks_*_*',
            'keep *_standAloneMuons_*_*'                           # standAloneMuon track collection, to be on the safe side
        ),
        SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('TagAndProbeSta','TagAndProbeMuID','TagAndProbeTrig') ) if Filter else cms.untracked.PSet()
    )

    process.e = cms.EndPath(process.outOnia2MuMu + process.outTnP)

