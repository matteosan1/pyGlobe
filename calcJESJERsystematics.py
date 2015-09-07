#!/usr/bin/env python

# calculates the impact of shifting the jet energy scale
import sys
import utils
from pprint import pprint

#----------------------------------------------------------------------
wsname = "CMS_emu_workspace"

# determine the systematics at one mass point only
mass = 125

#----------------------------------------------------------------------

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------

from optparse import OptionParser
parser = OptionParser("""

  usage: %prog [options] nominal_workspace_file workspace_file_up workspace_file_down

  calculates relative deviations due to JES and JER shifts
"""
)

parser.add_option("--format",
                  type = "choice",
                  choices = [ "text", "csv", "python", "csv-numevents" ],
                  default = "text",
                  help="output format in which the results should be printed",
                  )

(options, ARGV) = parser.parse_args()

fnameNominal, fnameUp, fnameDown = ARGV
#----------------------------------------



# get the number of signal events

# first index is the JES shift ('nom', 'up', 'down')
# second index is the category
# third index is the signal process
# value is the number of expected signal events

numSigEvents = {}

allCats = None
allProcs = None

# allCats = [ 'cat0' ]
# allProcs = [ 'ggh' ]

for fname, typename in  ((fnameNominal, "nom"),
                         (fnameUp, "up"),
                         (fnameDown, "down")):
    import ROOT
    fin = ROOT.TFile(fname)
    assert fin.IsOpen(), "could not open file " + fname

    ws = fin.Get(wsname)
    assert ws != None, "could not find workspace " + wsname

    # get list of categories from the first file
    if allCats == None:
        allCats   = utils.getCatEntries(utils.getObj(ws, 'allCategories'))
        allProcs  = utils.getCatEntries(utils.getObj(ws, 'allSigProcesses'))

    for cat in allCats:
        for proc in allProcs:

            # e.g. sig_Hem_unbinned_vbf_120_cat3
            name = "_".join([
                "sig",
                "Hem",
                "unbinned",
                proc,
                str(mass),
                cat
                ])

            # binned dataset
            # e.g. sig_Hem_vbf_115_cat10
            name = "_".join([
                "sig",
                "Hem",
                proc,
                str(mass),
                cat
                ])

            # get the signal MC dataset
            ds = utils.getObj(ws, name)

            numSigEvents.setdefault(typename, {}).setdefault(cat,{})[proc] = ds.sumEntries()

        # end of loop over signal processes
    # end of loop over categories
# end of loop over files

#----------------------------------------

# from pprint import pprint
# pprint(numSigEvents)

# first index is category
# second index is signal process
relDeviations = {}

for proc in allProcs:
    for cat in allCats:

        nom = numSigEvents['nom'][cat][proc]
        up = numSigEvents['up'][cat][proc]
        down = numSigEvents['down'][cat][proc]

        # check that up and down are on opposite sides of nominal

        if not ((up >= nom and nom >= down) or (up <= nom and nom <= down)):
            print >> sys.stderr, "WARNING: up/down are NOT on opposite sides of nominal for",cat,proc,": up=",up,"nom=",nom,"down=",down

        # take (up - down) / (2 * nominal)
        rel = (up - down) / (2.0 * nom)

        relDeviations.setdefault(cat,{})[proc] = rel


if options.format == 'csv':
    # print in CSV format
    print ",".join([ "%s" % cat for cat in allCats])
    for proc in allProcs:
        parts = [ proc ] + [ "%f" % relDeviations[cat][proc] for cat in allCats ]

        print ",".join(parts)
    
    
elif options.format == 'text':
    print "   "," ".join([ " %5s" % cat for cat in allCats])
    for proc in allProcs:
        parts = [ "%+5.2f%%" % (relDeviations[cat][proc] * 100) for cat in allCats ]

        print "%-3s" % proc," ".join(parts)

    print
elif options.format == 'python':
    # this is for using it in python files read when
    # generating the combine datacards
    pprint(relDeviations)

elif options.format == "csv-numevents":
    # print the absolute number of signal events in CSV format
    
    print ",".join([ "proc", "shift", "" ] + [ "%s" % cat for cat in allCats])
    for proc in allProcs:
        for shift in [ "nom", "up", "down"]:
            parts = [ proc, shift, "" ] + [ "%f" % numSigEvents[shift][cat][proc] for cat in allCats ]

            print ",".join(parts)

        print
        print
        print

else:
    raise Exception("internal error")
        
