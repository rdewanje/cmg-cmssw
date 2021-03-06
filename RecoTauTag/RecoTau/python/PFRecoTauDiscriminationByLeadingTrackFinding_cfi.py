import FWCore.ParameterSet.Config as cms
from RecoTauTag.RecoTau.TauDiscriminatorTools import noPrediscriminants

pfRecoTauDiscriminationByLeadingTrackFinding = cms.EDProducer("PFRecoTauDiscriminationByLeadingObjectPtCut",
    # Tau collection to discriminate
    PFTauProducer = cms.InputTag('pfRecoTauProducer'),

    # Only look for charged PFCandidates
    UseOnlyChargedHadrons = cms.bool(True),            

    # no pre-reqs for this cut
    Prediscriminants = noPrediscriminants,

    # Any *existing* charged PFCandidate will meet this requirement - so it is 
    # a test for existence, not pt
    MinPtLeadingObject = cms.double(0.0)
)

