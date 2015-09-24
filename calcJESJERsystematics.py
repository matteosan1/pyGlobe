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

def addUncert(expectedNumEvents, numMCentries):
    import uncertainties
    import math

    # TODO: add protection against zero events
    return uncertainties.ufloat(expectedNumEvents,
                                expectedNumEvents / math.sqrt(numMCentries))

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
                  choices = [ "text", "csv", "python", "csv-numevents", "csv-numentries" ],
                  default = "text",
                  help="output format in which the results should be printed",
                  )

parser.add_option("--uncert",
                  default = False,
                  action = "store_true",
                  help="also print uncertainties, derived from MC statistics assuming equally weighted events and using the Gaussian sqrt{N} approximation. Works only if the uncertainties python package is installed. Implies --unbinned.",
                  )

parser.add_option("--abs",
                  default = False,
                  action = "store_true",
                  help="print the deviation in terms of absolute number of events (for the default output format)",
                  )

parser.add_option("--unbinned",
                  default = False,
                  action = "store_true",
                  help="use the unbinned datasets instead of the binned ones (e.g. useful with --format csv-numentries which otherwise just returns the number of bins)",
                  )

(options, ARGV) = parser.parse_args()

fnameNominal, fnameUp, fnameDown = ARGV

if options.uncert:
    options.unbinned = True

#----------------------------------------



# get the number of signal events

# first index is the JES shift ('nom', 'up', 'down')
# second index is the category
# third index is the signal process
# value is the number of expected signal events

numSigEvents = {} # number of expected events
numSigEntries = {} # number of MC events (for checks)

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
            if options.unbinned:
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

            # get the signal MC dataset
            ds = utils.getObj(ws, name)

            numSigEvents.setdefault(typename, {}).setdefault(cat,{})[proc] = ds.sumEntries()
            numSigEntries.setdefault(typename, {}).setdefault(cat,{})[proc] = ds.numEntries()

        # end of loop over signal processes
    # end of loop over categories
# end of loop over files

#----------------------------------------

# from pprint import pprint
# pprint(numSigEvents)

# first index is category
# second index is signal process
relDeviations = {}
absDeviations = {}

for proc in allProcs:
    for cat in allCats:

        nom  = numSigEvents['nom'][cat][proc]
        up   = numSigEvents['up'][cat][proc]
        down = numSigEvents['down'][cat][proc]

        # check that up and down are on opposite sides of nominal

        if not ((up >= nom and nom >= down) or (up <= nom and nom <= down)):
            print >> sys.stderr, "WARNING: up/down are NOT on opposite sides of nominal for",cat,proc,": up=",up,"nom=",nom,"down=",down

        #----------
        # add uncertainties based on limited MC statistics
        # if requested
        #----------
        if options.uncert:
            nom  = addUncert(nom,  numSigEntries['nom'][cat][proc])
            up   = addUncert(up,   numSigEntries['up'][cat][proc])
            down = addUncert(down, numSigEntries['down'][cat][proc])
        #----------

        # take (up - down) / (2 * nominal)
        rel = (up - down) / (2.0 * nom)

        relDeviations.setdefault(cat,{})[proc] = rel

        # also calculate the (symmetrized) absolute uncertainty
        absDeviations.setdefault(cat,{})[proc] = (up - down) / 2.0

if options.format == 'csv':
    # print in CSV format
    print ",".join([ "%s" % cat for cat in allCats])
    for proc in allProcs:
        parts = [ proc ] + [ "%f" % relDeviations[cat][proc] for cat in allCats ]

        print ",".join(parts)
    
    
elif options.format == 'text':
    if options.abs:
        deviations = absDeviations
    else:
        deviations = relDeviations

    if options.uncert:
        if options.abs:
            fmt = " %17s"
        else:
            fmt = " %14s"
    else:
        if options.abs:
            fmt = " %7s"
        else:
            fmt = " %5s"

    print "    |"," | ".join([ fmt % cat for cat in allCats])
    for proc in allProcs:

        if options.uncert:
            if options.abs:
                fmt = "%+8.1f+/-%7.1f"
            else:
                fmt = "%+6.2f+/-%5.2f%%"

            parts = [ fmt % (deviations[cat][proc].n * 100, deviations[cat][proc].std_dev * 100) for cat in allCats ]

        else:
            if options.abs:
                fmt = "%+8.1f"
            else:
                fmt = "%+6.2f%%"
            parts = [ fmt % (deviations[cat][proc] * 100) for cat in allCats ]

        print "%-3s |" % proc," | ".join(parts)

    print
elif options.format == 'python':
    # this is for using it in python files read when
    # generating the combine datacards

    if options.abs:
        pprint(absDeviations)
    else:
        pprint(relDeviations)

elif options.format in ("csv-numevents", "csv-numentries"):
    # print the absolute number of signal events in CSV format
    if options.format == "csv-numevents":
        theData = numSigEvents
        theFormat = "%f"
    elif options.format == 'csv-numentries':
        theData = numSigEntries
        theFormat = "%d"
    else:
        raise Exception("internal error")
    
    print ",".join([ "proc", "shift", "" ] + [ "%s" % cat for cat in allCats])
    for proc in allProcs:
        for shift in [ "nom", "up", "down"]:
            parts = [ proc, shift, "" ] + [ theFormat % theData[shift][cat][proc] for cat in allCats ]

            print ",".join(parts)

        print
        print
        print

else:
    raise Exception("internal error")
        
