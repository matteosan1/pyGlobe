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

(options, ARGV) = parser.parse_args()

if options.cats != None:
    options.cats = options.cats.split(',')

if options.procs != None:
    options.procs = options.procs.split(',')

### if not options.simultaneous and options.signalScaling != 1:
###     print >> "--scale is currently only supported with --simultaneous"
###     sys.exit(1)

#----------------------------------------

assert len(ARGV) == 1

inputFname = ARGV.pop(0)

#----------------------------------------


import ROOT 
ROOT.gROOT.SetBatch(True)

# must load this library to have RooPower (otherwise we get a SIGSEGV)
ROOT.gSystem.Load("$CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisCombinedLimit.so")

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

allMasses = [ int(x) for x in utils.getCatEntries(utils.getObj(ws, 'allSigMasses')) ]

if options.procs == None:
    allProcs  = utils.getCatEntries(utils.getObj(ws, 'allSigProcesses'))
else:
    allProcs = options.procs

#----------

# table with number of signal events expected and number of MC
# events with links to plots

header = [ "proc","","mass","" ] + allCats

print ",".join(header)

#----------
# background
#----------
line = [ "bkg", "", "", ""]
for cat in allCats:
    dataset = utils.getObj(ws, "bkg_%s" % cat)
    line.append(dataset.sumEntries())    
print ",".join([str(x) for x in line ])
#----------
# signal at different masses and production mechanisms
#----------

for proc in allProcs:
    for mass in allMasses:

        line = [ "sig", proc, mass, "" ]

        for cat in allCats:

            dataset = utils.getObj(ws, "sig_Hem_unbinned_%s_%d_%s" % (proc, mass, cat))

            #----------
            # number of expected events
            #----------

            line.append(dataset.sumEntries() * options.signalScaling)

        # end of loop over categories

        print ",".join([str(x) for x in line ])

    # end of loop over masses

# end of loop over processes
