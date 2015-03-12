// -*- C++ -*-
//
// Package:    HiMuTrigEffAnalyzer
// Class:      HiMuTrigEffAnalyzer
// 
/**\class HiMuTrigEffAnalyzer HiMuTrigEffAnalyzer.cc HiAnalysis/HiMuTrigEffAnalyzer/plugin/HiMuTrigEffAnalyzer.cc

   Description: [one line class summary]

   Implementation:
   [Notes on implementation]
*/
//
// Original Author:  Torsten Dahms,40 4-A32,+41227671635,
//         Created:  Thu Dec  2 06:03:28 CET 2010
// $Id$
//
//


// system include files
#include <memory>
#include <iostream>
#include <string>
#include <vector>

#include "TFile.h"
#include "TH2.h"

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"

#include "RecoHI/HiCentralityAlgos/interface/CentralityProvider.h"
//
// class declaration
//

class HiMuTrigEffAnalyzer : public edm::EDAnalyzer {
public:
  explicit HiMuTrigEffAnalyzer(const edm::ParameterSet&);
  ~HiMuTrigEffAnalyzer();


private:
  virtual void beginJob() ;
  virtual void analyze(const edm::Event&, const edm::EventSetup&);
  virtual void endJob() ;

  // ----------member data ---------------------------
  // TFile
  TFile* fOut;

  // histos
  TH2F* hAllMu_pt_eta;
  TH2F* hTrigMu_pt_eta;
  TH2F* hTightMu_pt_eta;
  TH2F* hTrigTightMu_pt_eta;
  TH1F* hCent;

  // Handles
  edm::Handle<pat::MuonCollection> collMuon;

  // data members
  edm::InputTag       _patMuon;
  edm::InputTag       _thePVs;
  std::string         _histfilename;
  std::string         _trigFilterName;
  double              _maxAbsZ;

  math::XYZPoint RefVtx;

  // centrality
  CentralityProvider* centProvider = 0;
  int centBin;

  int nEvents;
};

//
// constructors and destructor
//
HiMuTrigEffAnalyzer::HiMuTrigEffAnalyzer(const edm::ParameterSet& iConfig):
  _patMuon(iConfig.getParameter<edm::InputTag>("srcMuon")),
  _thePVs(iConfig.getParameter<edm::InputTag>("primaryVertexTag")),
  _histfilename(iConfig.getParameter<std::string>("histFileName")),
  _trigFilterName(iConfig.getParameter<std::string>("trigFilterName")),
  _maxAbsZ(iConfig.getParameter<double>("maxAbsZ"))
{
  //now do what ever initialization is needed
  nEvents=0;
}


HiMuTrigEffAnalyzer::~HiMuTrigEffAnalyzer()
{
 
  // do anything here that needs to be done at desctruction time
  // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to for each event  ------------
void
HiMuTrigEffAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  nEvents++;

  edm::Handle<reco::VertexCollection> privtxs;
  iEvent.getByLabel(_thePVs, privtxs);
  reco::VertexCollection::const_iterator privtx;

  if ( privtxs->begin() != privtxs->end() ) {
    privtx=privtxs->begin();
    RefVtx = privtx->position();
  } else {
    RefVtx.SetXYZ(0.,0.,0.);
  }

  if (fabs(RefVtx.Z()) > _maxAbsZ) return;

  if(!centProvider) centProvider = new CentralityProvider(iSetup);
  centProvider->newEvent(iEvent,iSetup); // make sure you do this first in every event
  //const reco::Centrality* centrality = centProvider->raw();
  hCent->Fill(centProvider->getBin());

  iEvent.getByLabel(_patMuon,collMuon);

  if (collMuon.isValid()) {
    for(std::vector<pat::Muon>::const_iterator it=collMuon->begin();
	it!=collMuon->end();++it) {
      const pat::Muon* muon = &(*it);
      hAllMu_pt_eta->Fill(muon->eta(),muon->pt());

      reco::TrackRef iTrack = muon->innerTrack();
      reco::TrackRef gTrack = muon->globalTrack();
      bool isTightQuality = false;

      if (iTrack.isNonnull() && gTrack.isNonnull()) {
	const reco::HitPattern& p = iTrack->hitPattern();
	const reco::HitPattern& q = gTrack->hitPattern();
	isTightQuality = (muon->isGlobalMuon() &&
			  muon->isTrackerMuon() &&
			  iTrack->found() > 11 &&
			  gTrack->chi2()/gTrack->ndof() < 10.0 &&
			  q.numberOfValidMuonHits() > 0 &&
			  iTrack->chi2()/iTrack->ndof() < 4.0 &&
			  muon->muonID("TrackerMuonArbitrated") &&
			  muon->muonID("TMLastStationAngTight") &&
			  p.pixelLayersWithMeasurement() > 1 &&
			  fabs(iTrack->dxy(RefVtx)) < 0.2 &&
			  fabs(iTrack->dz(RefVtx)) < 4.0 ) ? true : false;
      }
      if (isTightQuality)
	hTightMu_pt_eta->Fill(muon->eta(),muon->pt());

      const pat::TriggerObjectStandAloneCollection muHLTMatches = muon->triggerObjectMatchesByFilter(_trigFilterName);
      if (muHLTMatches.size()>0) {
	hTrigMu_pt_eta->Fill(muon->eta(),muon->pt());
	if (isTightQuality) 
	    hTrigTightMu_pt_eta->Fill(muon->eta(),muon->pt());
      }
    }
  }
  
  return;
}


// ------------ method called once each job just before starting event loop  ------------
void 
HiMuTrigEffAnalyzer::beginJob()
{
  hAllMu_pt_eta = new TH2F("hAllMu_pt_eta","All muons p_{T} distribution;#eta (#mu);p_{T} (#mu) [GeV/c];counts",50,-2.5,2.5,120,0.0,60);
  hTrigMu_pt_eta = new TH2F("hTrigMu_pt_eta","Trigger matched muons p_{T} distribution;#eta (#mu);p_{T} (#mu) [GeV/c];counts",50,-2.5,2.5,120,0.0,60);

  hTightMu_pt_eta = new TH2F("hTightMu_pt_eta","Tight quality muons p_{T} distribution;#eta (#mu);p_{T} (#mu) [GeV/c];counts",50,-2.5,2.5,120,0.0,60);
  hTrigTightMu_pt_eta = new TH2F("hTrigTightMu_pt_eta","Trigger matched tight muons p_{T} distribution;#eta (#mu);p_{T} (#mu) [GeV/c];counts",50,-2.5,2.5,120,0.0,60);

  hAllMu_pt_eta->Sumw2();
  hTrigMu_pt_eta->Sumw2();

  hTightMu_pt_eta->Sumw2();
  hTrigTightMu_pt_eta->Sumw2();

  hCent = new TH1F("hCent","hCent;centrality bin;Number of Events",40,0,40);
  hCent->Sumw2();

  return;
}

// ------------ method called once each job just after ending the event loop  ------------
void 
HiMuTrigEffAnalyzer::endJob()
{
  std::cout << "Total number of events = " << nEvents << std::endl;

  fOut = new TFile(_histfilename.c_str(), "RECREATE");
  hAllMu_pt_eta->Write();
  hTrigMu_pt_eta->Write();
  hTightMu_pt_eta->Write();
  hTrigTightMu_pt_eta->Write();
  hCent->Write();
  fOut->Close();

  return;
}

//define this as a plug-in
DEFINE_FWK_MODULE(HiMuTrigEffAnalyzer);
