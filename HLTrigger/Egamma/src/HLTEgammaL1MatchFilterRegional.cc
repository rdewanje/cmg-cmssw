/** \class HLTEgammaL1MatchFilterRegional
 *
 * $Id: HLTEgammaL1MatchFilterRegional.cc,v 1.12 2012/01/22 23:42:50 fwyzard Exp $
 *
 *  \author Monica Vazquez Acosta (CERN)
 *
 */

#include "HLTrigger/Egamma/interface/HLTEgammaL1MatchFilterRegional.h"

//#include "DataFormats/L1GlobalTrigger/interface/L1GlobalTriggerReadoutSetupFwd.h"

#include "DataFormats/Common/interface/Handle.h"

#include "DataFormats/HLTReco/interface/TriggerFilterObjectWithRefs.h"

#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "DataFormats/RecoCandidate/interface/RecoEcalCandidate.h"
#include "DataFormats/RecoCandidate/interface/RecoEcalCandidateFwd.h"



#include "CondFormats/L1TObjects/interface/L1CaloGeometry.h"
#include "CondFormats/DataRecord/interface/L1CaloGeometryRecord.h"

#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/EventSetup.h"

#define TWOPI 6.283185308
//
// constructors and destructor
//
HLTEgammaL1MatchFilterRegional::HLTEgammaL1MatchFilterRegional(const edm::ParameterSet& iConfig) : HLTFilter(iConfig) 
{
   candIsolatedTag_ = iConfig.getParameter< edm::InputTag > ("candIsolatedTag");
   l1IsolatedTag_ = iConfig.getParameter< edm::InputTag > ("l1IsolatedTag");
   candNonIsolatedTag_ = iConfig.getParameter< edm::InputTag > ("candNonIsolatedTag");
   l1NonIsolatedTag_ = iConfig.getParameter< edm::InputTag > ("l1NonIsolatedTag");
   L1SeedFilterTag_ = iConfig.getParameter< edm::InputTag > ("L1SeedFilterTag");
   ncandcut_  = iConfig.getParameter<int> ("ncandcut");
   doIsolated_   = iConfig.getParameter<bool>("doIsolated");


   region_eta_size_      = iConfig.getParameter<double> ("region_eta_size");
   region_eta_size_ecap_ = iConfig.getParameter<double> ("region_eta_size_ecap");
   region_phi_size_      = iConfig.getParameter<double> ("region_phi_size");
   barrel_end_           = iConfig.getParameter<double> ("barrel_end");   
   endcap_end_           = iConfig.getParameter<double> ("endcap_end");   
}

HLTEgammaL1MatchFilterRegional::~HLTEgammaL1MatchFilterRegional(){}


// ------------ method called to produce the data  ------------
//configuration:
//doIsolated=true, only isolated superclusters are allowed to match isolated L1 seeds
//doIsolated=false, isolated superclusters are allowed to match either iso or non iso L1 seeds, non isolated superclusters are allowed only to match non-iso seeds. If no collection name is given for non-isolated superclusters, assumes the the isolated collection contains all (both iso + non iso) seeded superclusters.
bool
HLTEgammaL1MatchFilterRegional::hltFilter(edm::Event& iEvent, const edm::EventSetup& iSetup, trigger::TriggerFilterObjectWithRefs & filterproduct)
{
  // std::cout <<"runnr "<<iEvent.id().run()<<" event "<<iEvent.id().event()<<std::endl;
  using namespace trigger;
  using namespace l1extra;

  if (saveTags()) {
    filterproduct.addCollectionTag(l1IsolatedTag_);
    if (not doIsolated_)
      filterproduct.addCollectionTag(l1NonIsolatedTag_);
  }

  edm::Ref<reco::RecoEcalCandidateCollection> ref;

  // Get the CaloGeometry
  edm::ESHandle<L1CaloGeometry> l1CaloGeom ;
  iSetup.get<L1CaloGeometryRecord>().get(l1CaloGeom) ;


  // look at all candidates,  check cuts and add to filter object
  int n(0);

  // Get the recoEcalCandidates
  edm::Handle<reco::RecoEcalCandidateCollection> recoIsolecalcands;
  iEvent.getByLabel(candIsolatedTag_,recoIsolecalcands);


  edm::Handle<trigger::TriggerFilterObjectWithRefs> L1SeedOutput;

  iEvent.getByLabel (L1SeedFilterTag_,L1SeedOutput);

  std::vector<l1extra::L1EmParticleRef > l1EGIso;       
  L1SeedOutput->getObjects(TriggerL1IsoEG, l1EGIso);
  
  std::vector<l1extra::L1EmParticleRef > l1EGNonIso;       
  L1SeedOutput->getObjects(TriggerL1NoIsoEG, l1EGNonIso);

  
  for (reco::RecoEcalCandidateCollection::const_iterator recoecalcand= recoIsolecalcands->begin(); recoecalcand!=recoIsolecalcands->end(); recoecalcand++) {

  
    if(fabs(recoecalcand->eta()) < endcap_end_){
      //SC should be inside the ECAL fiducial volume

      bool matchedSCIso = matchedToL1Cand(l1EGIso,recoecalcand->eta(),recoecalcand->phi());

      //now due to SC cleaning given preference to isolated candiates, 
      //if there is an isolated and nonisolated L1 cand in the same eta/phi bin
      //the corresponding SC will be only in the isolated SC collection
      //so if we are !doIsolated_, we need to run over the nonisol L1 collection as well 
      bool matchedSCNonIso=false;
      if(!doIsolated_){
	matchedSCNonIso =  matchedToL1Cand(l1EGNonIso,recoecalcand->eta(),recoecalcand->phi());
      }
       

      if(matchedSCIso || matchedSCNonIso) {
	n++;

	ref = edm::Ref<reco::RecoEcalCandidateCollection>(recoIsolecalcands, distance(recoIsolecalcands->begin(),recoecalcand) );       
	filterproduct.addObject(TriggerCluster, ref);
      }//end  matched check

    }//end endcap fiduical check
    
  }//end loop over all isolated RecoEcalCandidates
  
  //if doIsolated_ is false now run over the nonisolated superclusters and non isolated L1 seeds 
  //however in the case we have a single collection of superclusters containing both iso L1 and non iso L1 seeded superclusters,
  //we specific doIsolated=false to match to isolated superclusters to non isolated seeds in the above loop
  //however we do not have a non isolated collection of superclusters so we have to protect against that
  if(!doIsolated_ && !candNonIsolatedTag_.label().empty()) {
  
    edm::Handle<reco::RecoEcalCandidateCollection> recoNonIsolecalcands;
    iEvent.getByLabel(candNonIsolatedTag_,recoNonIsolecalcands);
    
    for (reco::RecoEcalCandidateCollection::const_iterator recoecalcand= recoNonIsolecalcands->begin(); recoecalcand!=recoNonIsolecalcands->end(); recoecalcand++) {
      if(fabs(recoecalcand->eta()) < endcap_end_){
	bool matchedSCNonIso =  matchedToL1Cand(l1EGNonIso,recoecalcand->eta(),recoecalcand->phi());
	
	if(matchedSCNonIso) {
	  n++;
	  ref = edm::Ref<reco::RecoEcalCandidateCollection>(recoNonIsolecalcands, distance(recoNonIsolecalcands->begin(),recoecalcand) );       
	  filterproduct.addObject(TriggerCluster, ref);
	}//end  matched check
	
      }//end endcap fiduical check
      
    }//end loop over all isolated RecoEcalCandidates
  }//end doIsolatedCheck
  

  // filter decision
  bool accept(n>=ncandcut_);
  
  return accept;
}


bool 
HLTEgammaL1MatchFilterRegional::matchedToL1Cand(const std::vector<l1extra::L1EmParticleRef >& l1Cands,const float scEta,const float scPhi) 
{
  for (unsigned int i=0; i<l1Cands.size(); i++) {
    //ORCA matching method
    double etaBinLow  = 0.;
    double etaBinHigh = 0.;	
    if(fabs(scEta) < barrel_end_){
      etaBinLow = l1Cands[i]->eta() - region_eta_size_/2.;
      etaBinHigh = etaBinLow + region_eta_size_;
    }
    else{
      etaBinLow = l1Cands[i]->eta() - region_eta_size_ecap_/2.;
      etaBinHigh = etaBinLow + region_eta_size_ecap_;
    }
    
    float deltaphi=fabs(scPhi -l1Cands[i]->phi());
    if(deltaphi>TWOPI) deltaphi-=TWOPI;
    if(deltaphi>TWOPI/2.) deltaphi=TWOPI-deltaphi;
    
    if(scEta < etaBinHigh && scEta > etaBinLow && deltaphi <region_phi_size_/2. )  {
      return true;
    }
  }
  return false;
}
