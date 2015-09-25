#!/usr/bin/env python

import sys, utils, itertools, math, array
from utils import saveAllCanvases
gcs = []

# print number of (expected) events, mostly in csv format

#----------------------------------------------------------------------

wsname = "CMS_emu_workspace"

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
from optparse import OptionParser
parser = OptionParser("""

  usage: %prog [options] input_file

  prints the number of (expected) events
"""
)

### parser.add_option("--simultaneous",
###                   default = False,
###                   action = "store_true",
###                   help="look for simultaneous fit objects instead of standard ones",
###                   )

parser.add_option("--cat",
                  dest = "cats",
                  type = str,
                  default = None,
                  help="comma separated list of category names (default is to use all found in the workspace)",
                  )

parser.add_option("--scaleSig",
                  dest = "signalScaling",
                  type = float,
                  default = 1,
                  help="factor to scale the signal with, only for the comparison with MC (useful when the signal has been scaled w.r.t the input MC events)",
                  )

parser.add_option("--proc",
                  dest = "procs",
                  type = str,
                  default = None,
                  help="comma separated list of process names (default is to use all found in the workspace)",
                  )

parser.add_option("--mass",
                  dest = "masses",
                  type = str,
                  default = None,
                  help="comma separated list of masses (default is to use all found in the workspace)",
                  )

parser.add_option("--obs",
                  default = False,
                  action = "store_true",
                  help="also print the number of observed events",
                  )

parser.add_option("--mc-events",
                  dest = "mcEvents",
                  default = False,
                  action = "store_true",
                  help="use unbinned datasets (for signal only) to print the number of MC events",
                  )

parser.add_option("--sig-reco-mass-range",
                  dest = "sigRecoMassRange",
                  default = None,
                  type = str,
                  help="only count signal events in the range minMass,maxMass of reconstructed mass",
                  )

parser.add_option("--sumcat",
                  default = False,
                  action = "store_true",
                  help="add a column with the sum over categories",
                  )


(options, ARGV) = parser.parse_args()

if options.cats != None:
    options.cats = options.cats.split(',')

if options.procs != None:
    options.procs = options.procs.split(',')

if options.masses != None:
    options.masses = [ int(x) for x in options.masses.split(',') ]

### if not options.simultaneous and options.signalScaling != 1:
###     print >> "--scale is currently only supported with --simultaneous"
###     sys.exit(1)

if options.sigRecoMassRange:
    options.sigRecoMassRange = [ float(x) for x in options.sigRecoMassRange.split(',') ]
    assert len(options.sigRecoMassRange) == 2
else:
    options.sigRecoMassRange = (None, None)

#----------------------------------------

import ROOT 
ROOT.gROOT.SetBatch(True)

# must load this library to have RooPower (otherwise we get a SIGSEGV)
ROOT.gSystem.Load("$CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisCombinedLimit.so")


for inputFname in ARGV:

    fin = ROOT.TFile(inputFname)
    assert fin.IsOpen(), "could not open input workspace file " + inputFname

    ws = fin.Get(wsname)

    assert ws != None, "could not find workspace '%s' in file '%s'" % (wsname, inputFname)

    #----------
    # get the list of all categories
    #----------
    if options.cats == None:
        allCats = utils.getCatEntries(utils.getObj(ws, 'allCategories'))
    else:
        allCats = options.cats

    if options.masses != None:
        allMasses = list(options.masses)
    else:
        allMasses = [ int(x) for x in utils.getCatEntries(utils.getObj(ws, 'allSigMasses')) ]

    if options.procs == None:
        allProcs  = utils.getCatEntries(utils.getObj(ws, 'allSigProcesses'))
    else:
        allProcs = options.procs

    #----------

    # table with number of signal events expected and number of MC
    # events with links to plots

    header = [ "proc","","mass","" ] + allCats

    if options.sumcat:
        header.append("sum")

    print ",".join(header)

    #----------
    # background
    #----------
    line = [ "bkg", "", "", ""]

    catSum = 0.

    for cat in allCats:
        dataset = utils.getObj(ws, "bkg_%s" % cat)
        line.append(dataset.sumEntries())
        catSum += line[-1]

    if options.sumcat:
        line.append(catSum)
    
    print ",".join([str(x) for x in line ])

    #----------
    # observed number of events
    #----------

    catSum = 0

    if options.obs:
        line = [ "obs", "", "", ""]

        for cat in allCats:
            dataset = utils.getObj(ws, "data_%s" % cat)
            line.append(dataset.sumEntries())    

            catSum += line[-1]

        if options.sumcat:
            line.append(catSum)

        print ",".join([str(x) for x in line ])


    #----------
    # signal at different masses and production mechanisms
    #----------

    for proc in allProcs:
        for mass in allMasses:

            line = [ "sig", proc, mass, "" ]

            catSum = 0.

            for cat in allCats:

                # e.g. sig_Hem_unbinned_vbf_120_cat3
                if options.mcEvents or options.sigRecoMassRange:
                    name = "_".join([
                        "sig",
                        "Hem",
                        "unbinned",
                        proc,
                        str(mass),
                        cat
                        ])
                else:
                    # binned dataset
                    # e.g. sig_Hem_vbf_115_cat10
                    name = "_".join([
                        "sig",
                        "Hem",
                        proc,
                        str(mass),
                        cat
                        ])

                dataset = utils.getObj(ws, name)

                #----------
                # number of expected events
                #----------

                # number of MC events or number of expected events
                value = utils.sumWeightsInMassRange(ws, dataset,
                                                    options.sigRecoMassRange[0],
                                                    options.sigRecoMassRange[1],
                                                    useWeights = not options.mcEvents
                                                    )
                
                if not options.mcEvents:
                    value *= options.signalScaling

                line.append(value)
                catSum += line[-1]

            # end of loop over categories

            if options.sumcat:
                line.append(catSum)

            print ",".join([str(x) for x in line ])

        # end of loop over masses

    # end of loop over processes

    print

    ROOT.gROOT.cd()
    fin.Close()

# end of loop over files
