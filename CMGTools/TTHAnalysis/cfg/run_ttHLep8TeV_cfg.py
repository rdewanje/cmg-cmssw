import copy
import os 
import CMGTools.RootTools.fwlite.Config as cfg
from CMGTools.RootTools.fwlite.Config import printComps
from CMGTools.RootTools.RootTools import *

PDFWeights = []
#PDFWeights = [ ("CT10",53), ("MSTW2008lo68cl",41), ("NNPDF21_100",101) ]
#PDFWeights = [ ("cteq61",41) ]

# this analyzer finds the initial events before the skim
skimAnalyzer = cfg.Analyzer(
    'skimAnalyzerCount'
    )

eventSelector = cfg.Analyzer(
    'EventSelector',
    toSelect = [
    # here put the event numbers (actual event numbers from CMSSW)
    ]
    )
    
jsonAna = cfg.Analyzer(
    'JSONAnalyzer',
    )

triggerAna = cfg.Analyzer(
    #'TriggerAnalyzer',
    'triggerBitFilter',
    )


# this analyzer is just there to select a list of good primary vertices.
ttHVertexAna = cfg.Analyzer(
    'VertexAnalyzer',
    goodVertices = 'offlinePrimaryVertices',
    vertexWeight = None,
    fixedWeight = 1,
    verbose = False
    )


# this analyzer actually does the pile-up reweighting.
pileUpAna = cfg.Analyzer(
    "PileUpAnalyzer",
    # build unweighted pu distribution using number of pile up interactions if False
    # otherwise, use fill the distribution using number of true interactions
    true = True,
    makeHists=False
    )


# Gen Info Analyzer
ttHGenAna = cfg.Analyzer(
    'ttHGenLevelAnalyzer',
    filterHiggsDecays = [0, 15, 23, 24],
    verbose = False,
    PDFWeights = [ pdf for pdf,num in PDFWeights ]
    )

susyScanAna = cfg.Analyzer(
    'susyParameterScanAnalyzer',
    )

# Lepton Analyzer
ttHLepAna = cfg.Analyzer(
    'ttHLepAnalyzerBase',
    rhoMuon= 'kt6PFJetsCentralNeutral',
    rhoElectron = 'kt6PFJets',
    muons='cmgMuonSel',
    electrons='cmgElectronSel',
    photons='cmgPhotonSel',
    isolationCut=0.4, 
    sip3dCut=10,
    sip3dCutVeryLoose=100,
    minGoodLeptons=2,
    minInclusiveLeptons=2,
    doSSLeptons=False,
    doMuScleFitCorrections=False,
    doRochesterCorrections=True,
    doElectronScaleCorrections=False,
    doRecomputeSIP3D=True,
    doSegmentBasedMuonCleaning=True,
    doEleMuCrossCleaning=True,
    )


# Lepton MC Matching (must happen earlier to allow for MVA corrections)
ttHLepMCAna = cfg.Analyzer(
    'ttHLepMCMatchAnalyzer',
    )


# Tau Analyzer
ttHTauAna = cfg.Analyzer(
    'ttHTauAnalyzer',
    ptMin = 20,
    vetoLeptons = True,
    leptonVetoDR = 0.5,
    tauID = "byMediumIsolationMVA2",
    tauLooseID = "decayModeFinding",
)

# Tau MC Matching
ttHTauMCAna = cfg.Analyzer(
    'ttHTauMCMatchAnalyzer',
)


# Jets Analyzer 
ttHJetAna = cfg.Analyzer(
    'ttHJetAnalyzer',
    jetCol = 'cmgPFJetSelCHS',
    jetCol4MVA = 'cmgPFJetSel',
    jetPt = 25.,
    jetEta = 4.7,
    jetEtaCentral = 2.4,
    relaxJetId = False,  
    doPuId = True,
    recalibrateJets = False,
    shiftJEC = 0, # set to +1 or -1 to get +/-1 sigma shifts
    cleanJetsFromTaus = False,
    )


## MET Analyzer
#ttHMETAna = cfg.Analyzer(
#    'ttHMETAnalyzer',
#    )

# Jet MC Match Analyzer
ttHJetMCAna = cfg.Analyzer(
    'ttHJetMCMatchAnalyzer',
    smearJets = True,
    shiftJER = 0, # set to +1 or -1 to get +/-1 sigma shifts
    )

# Event Analyzer
ttHEventAna = cfg.Analyzer(
    'ttHLepEventAnalyzer',
    maxLeps = 4, ## leptons to use
    verbose = False,
    minJets25 = 0,
    )

from CMGTools.TTHAnalysis.samples.samples_8TeV import triggers_mumu, triggers_ee, triggers_mue
# Tree Producer
treeProducer = cfg.Analyzer(
    'ttHLepTreeProducerBase',
    doLooseLeptons = False,
    doInclusiveLeptons = False,
    doTaus = False,
    doJetsFailId = False,
    PDFWeights = PDFWeights,
    triggerBits = {
            'DoubleMu' : triggers_mumu,
            'DoubleEl' : [ t for t in triggers_ee if "Ele15_Ele8_Ele5" not in t ],
            'TripleEl' : [ t for t in triggers_ee if "Ele15_Ele8_Ele5"     in t ],
            'MuEG'     : [ t for t in triggers_mue if "Mu" in t and "Ele" in t ]
        }
    )


#-------- SAMPLES

from CMGTools.TTHAnalysis.samples.samples_8TeV import * 

for mc in mcSamples+fastSimSamples:
    mc.triggers = triggersMC_mue
#selectedComponents=mcSamples
#selectedComponents=[TTH,DYJetsM10,DYJetsM50,TTLep]
#selectedComponents=[DY1JetsM50,DY2JetsM50,DY3JetsM50,DY4JetsM50,W2Jets,WGToLNuG,WJets_HT250To300,WJets_HT300To400,WJets_HT400ToInf]
#selectedComponents=[W1Jets,W2Jets,WGToLNuG]

for data in dataSamplesE:
    data.triggers = triggers_ee
for data in dataSamplesMu:
    data.triggers = triggers_mumu
    data.vetoTriggers = triggers_ee
for data in dataSamplesMuE:
    data.triggers = triggers_mue
    data.vetoTriggers=triggers_ee+triggers_mumu

selectedComponents=mcSamples+dataSamplesMu+dataSamplesE+dataSamplesMuE



#-------- SEQUENCE

sequence = cfg.Sequence([
    skimAnalyzer,
    #eventSelector,
    jsonAna,
    triggerAna,
    pileUpAna,
    ttHGenAna,
    #susyScanAna, #not working on V5_10_0 samples
    ttHVertexAna,
    ttHLepAna,
    ttHLepMCAna,
    ttHTauAna,
    ttHTauMCAna,
    ttHJetAna,
    #ttHMETAna,
    ttHJetMCAna,
    ttHEventAna,
    treeProducer,
    ])




#-------- HOW TO RUN
test = 1
if test==1:
    # test a single component, using a single thread.
    # necessary to debug the code, until it doesn't crash anymore
    comp = TTH
    #comp = DoubleMuD
    comp.files = comp.files[:1]
    selectedComponents = [comp]
    comp.splitFactor = 1
    ## search for memory leaks
    #import ROOT;
    #hook = ROOT.SetupIgProfDumpHook()
    #hook.start()
elif test==2:    
    # test all components (1 thread per component).
    # important to make sure that your code runs on any kind of component
    for comp in selectedComponents:
        comp.splitFactor = 1
        comp.files = comp.files[:3]
elif test==3:
    # test two components, using many threads, to check if variables are ok
    #comp = DoubleElectronC
    #comp.files = comp.files[:20]
    #comp.splitFactor = 5
    #selectedComponents = [comp]
    comp = DYJetsM50
    comp.files = comp.files[:20]
    comp.splitFactor = 5
    selectedComponents = [comp]
elif test==4:
    # MC sync sample
    comp = TTH
    comp.files = [ 'root://pcmssd12//data/gpetrucc/8TeV/ttH/cmgTuple_full.TTH_Inclusive_M-125_8TeV_pythia6_PU_S10_START53_V7A-v1_F8454517-F509-E211-BAB4-003048D47792.root' ]
    selectedComponents = [comp]
    comp.splitFactor = 1
    comp.triggers = [] #triggersMC_mue #[t for t in triggersMC_mue if "Ele15_Ele8_Ele5" not in t ]
    ttHLepAna.doRochesterCorrections = False
    ttHLepAna.doElectronScaleCorrections = False
    ttHLepAna.minGoodLeptons = 2
    #treeProducer.doJetsFailId = True
    #ttHJetAna.jetCol = 'cmgPFJetSel'
elif test==6:
    # Ad-hoc Data sample
    comp = DoubleMuD
    comp.name = 'DoubleMuAll'
    comp.json = None
    comp.triggers = [] 
    comp.files = [ '/afs/cern.ch/user/g/gpetrucc/ttH/CMGTools/CMSSW_5_3_5/src/CMGTools/TTHAnalysis/../Common/prod/2lss_mumu_tight/patAOD-DoubleMu-all.root' ]
    #comp.name = 'MuEGAll'
    #comp.files = [ '/afs/cern.ch/user/g/gpetrucc/ttH/CMGTools/CMSSW_5_3_5/src/CMGTools/Common/prod/2lss_em_tight/patAOD-2lss_em-all.root' ]
    selectedComponents = [comp]
    comp.splitFactor = 1
elif test==7:    
    for comp in selectedComponents:
        comp.splitFactor = comp.splitFactor / 40
        comp.files = [ f for (i,f) in enumerate(comp.files) if i % 20 == 19 ]
 
     

# creation of the processing configuration.
# we define here on which components to run, and
# what is the sequence of analyzers to run on each event. 
config = cfg.Config( components = selectedComponents,
                     sequence = sequence )

printComps(config.components, True)
