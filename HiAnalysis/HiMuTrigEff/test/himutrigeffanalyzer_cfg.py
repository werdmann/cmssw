import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

process = cms.Process("HIMuTrigEffAna")

# setup 'analysis'  options
options = VarParsing.VarParsing ('analysis')

# setup any defaults you want
options.outputFile = "MuTrigEff_Histos.root"
options.inputFiles = 'rfio:/castor/cern.ch/cms/store/user/tdahms/HeavyIons/Zmumu/Data/v1/PatGoodRecoMuonSkims/Runs_150844-152638/patGoodRecoMuon_Skim_10_1_fvd.root'
options.maxEvents = -1 # -1 means all events

# get and parse the command line arguments
options.parseArguments()

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.destinations = ['cout', 'cerr']
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.GlobalTag.globaltag = 'GR10_P_V12::All'

from CmsHi.Analysis2010.CommonFunctions_cff import *
overrideCentrality(process)

process.HeavyIonGlobalParameters = cms.PSet(
    centralityVariable = cms.string("HFhits"),
    nonDefaultGlauberModel = cms.string(""),
    centralitySrc = cms.InputTag("hiCentrality")
    )

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(options.maxEvents) )

process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        options.inputFiles
    )
)
'''
import os,commands
# get a list of files from a specified directory
mydir = "/castor/cern.ch/cms/store/caf/user/tdahms/HeavyIons/Onia/Data2010/v1/Skims/Prompt/150844-152638/"

cmd  = 'nsls %s/ ' % (mydir)
mylist = ["rfio:%s/%s" % (mydir,j) for j in commands.getoutput(cmd).split('\n')]

# add a specified number of files from mydir to the list of fileNames
start=0
nfiles=50
for i in range(start,start+nfiles):
     process.source.fileNames.append('%s' % (mylist[i]))
#     print "process.source.fileNames.append(%s" % (mylist[i])")"
print "Number of files to process is %s" % (len(process.source.fileNames))
'''

process.mutrigeff = cms.EDAnalyzer('HiMuTrigEffAnalyzer',
                                   srcMuon = cms.InputTag("patMuonsWithTrigger"),
                                   primaryVertexTag = cms.InputTag("hiSelectedVertex"),
                                   maxAbsZ = cms.double(24.0),
                                   histFileName = cms.string(options.outputFile),		
                                   trigFilterName = cms.string("hltHIL2Mu3L2Filtered")
                                   #trigFilterName = cms.string("hltHIL2DoubleMu3L2Filtered")
)


process.p = cms.Path(process.mutrigeff)
