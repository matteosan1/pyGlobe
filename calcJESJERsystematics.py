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

ARGV = sys.argv[1:]

fnameNominal, fnameUp, fnameDown = ARGV

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
            print "WARNING: up/down are NOT on opposite sides of nominal for",cat,proc,": up=",up,"nom=",nom,"down=",down

        # take (up - down) / (2 * nominal)
        rel = (up - down) / (2.0 * nom)

        relDeviations.setdefault(cat,{})[proc] = rel


print "   "," ".join([ " %5s" % cat for cat in allCats])
for proc in allProcs:
    parts = [ "%5.1f%%" % (relDeviations[cat][proc] * 100) for cat in allCats ]

    print "%-3s" % proc," ".join(parts)

print
pprint(relDeviations)
    
        
