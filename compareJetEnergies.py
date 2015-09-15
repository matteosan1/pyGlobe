#!/usr/bin/env python

import sys
gcs = []

# makes some comparison plots for jet energies and MET before/after shifting them

#----------------------------------------------------------------------

def readROOTtree(tree, itype, eventKeys, expressions, cutexpr = None):
    # eventKeys should be a list of (run, lumisection, event)
    # we will return the values in the same order
    
    retval = [ [ None ] * len(eventKeys) for expression in expressions ]

    # build a reverse index
    eventKeysMap = {}
    for i, key in enumerate(eventKeys):
        assert not eventKeysMap.has_key(key)
        eventKeysMap[key] = i

    print "requested events:",len(eventKeysMap)
    numEventsFound = 0

    numEventsSelected = 0

    # loop over the entries
    for i in range(tree.GetEntries()):
        tree.GetEntry(i)

        # check if this event was requested
        if tree.itype  != itype:
            continue

        thisEventKey = (tree.run, tree.lumis, int(tree.event + 0.5))
        try:

            position = eventKeysMap.get(thisEventKey, None)
            if position == None:
                # not requested
                continue

            numEventsFound += 1

            # check if the event passes the cut or not
            if cutexpr != None and not eval(cutexpr):
                continue

            numEventsSelected += 1

            # store variables
            for expressionIndex, expression in enumerate(expressions):
                retval[expressionIndex][position] = eval("tree." + expression)
        except Exception, ex:
            print >> sys.stderr, "caught exception for run/lumisection/event",thisEventKey
            raise

    # check that we've found all events
    assert numEventsFound == len(eventKeysMap)

    print "selected %d out of %d events" % (numEventsSelected, numEventsFound)
    

    return retval

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------

from optparse import OptionParser
parser = OptionParser("""

  usage: %prog [options] before.csv after.csv

  plots category migration when changing from before.csv to after.csv

"""
)

parser.add_option("-o",
                  dest = "outputFile",
                  type = str,
                  default = None,
                  help="file names where the save the plot to, supports {..} templates",
                  )

parser.add_option("--cats",
                  dest = "categories",
                  type = str,
                  default = None,
                  help="comma separated list of category numbers (default is to run over all categories)",
                  )

parser.add_option("--mode",
                  type = str,
                  default = None,
                  help="mode name (e.g. JES or JER) for plot title",
                  )

(options, ARGV) = parser.parse_args()

if options.categories != None:
    options.categories = [ int(x) for x in options.categories.split(",") ]

#----------------------------------------

itype, csvFile, rootFileNominal, rootFileShifted = ARGV
itype = int(itype)

import plotEventMigrations

# get list of events to plot (and their categories)
csvData = plotEventMigrations.readFile(csvFile)

csvData = csvData[itype]


if options.categories == None:
    allCats = sorted(set( [ line['cat'] for line in csvData.values() ]))
else:
    allCats = options.categories


#----------
# open the ROOT files
#----------
trees = []

allFnames = [ rootFileNominal, rootFileShifted ]

for fname in allFnames:
    import ROOT

    fin = ROOT.TFile(fname); gcs.append(fin)
    assert fin.IsOpen()

    tree = fin.Get("opttree")
    assert tree != None

    trees.append(tree)

#----------
# read jet energies from the trees
#----------
catToNumJets = {
    0: 0,
    1: 1,
    2: 2,
    3: 0,
    4: 1,
    5: 2,
    6: 0,
    7: 1,
    8: 2,
    9: 2,
    10: 2,
    }

for cat in allCats:

    maxNumJets = catToNumJets[cat]

    if maxNumJets == 0:
        continue

    # find events for this category
    eventKeys = [ key for key, line in csvData.items() if line['cat'] == cat ]

    # produce an ntuple with the before/after energies
    ntuple = ROOT.TNtuple("ntuple","ntuple","before:after"); gcs.append(ntuple)

    # for categories with more than one jet,
    # fill all jets into the same ntuple
    for jetIndex in range(maxNumJets):
        expressions = [ "jetet[%d]" % jetIndex ]

        print "cat=",cat,"expressions=",expressions
        
        eventDatas = []
        for tree, fname in zip(trees, allFnames):
            print "reading tree from file",fname

            print "fname=",fname
            eventDatas.append(readROOTtree(tree, itype, eventKeys, expressions,
                                           cutexpr = "tree.njets20 > %d" % jetIndex
                                           ))

        assert len(eventDatas[0][0]) == len(eventDatas[1][0])

        for before, after in zip(eventDatas[0][0], eventDatas[1][0]):
            if before != None and after != None:
                ntuple.Fill(before,after)
            else:
                # print "UUU before=",before,"after=",after
                pass

    # end of loop over jet indices
    
    # make plots
    gcs.append(ROOT.TCanvas())

    ntuple.SetMarkerStyle(20)
    ntuple.Draw("(after - before) * 100.0 / before:before")

    htemp = ntuple.GetHistogram()

    htemp.SetXTitle("Jet ET [GeV]")
    htemp.SetYTitle("(modified - unmodified)/unmodified [%]")

    titleParts = [
        plotEventMigrations.itypeToProcName.get(itype,"(unknown process)"),
        "cat%d" % cat
        ]

    if options.mode != None:
        titleParts.append(options.mode)

    title = " ".join(titleParts)

    htemp.SetTitle(title)

    ROOT.gPad.SetGrid()

    if options.outputFile != None:
        shortProcName = plotEventMigrations.itypeToShortProcName[itype] 

        ROOT.gPad.SaveAs(options.outputFile.format(cat = cat,
                                                   itype = itype,
                                                       proc = shortProcName))
        
