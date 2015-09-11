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

ARGV = sys.argv[1:]

itype, csvFile, rootFileNominal, rootFileShifted = ARGV
itype = int(itype)

import plotEventMigrations

# get list of events to plot (and their categories)
csvData = plotEventMigrations.readFile(csvFile)

csvData = csvData[itype]

allCats = sorted(set( [ line['cat'] for line in csvData.values() ]))


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

        # produce an ntuple with the before/after energies
        ntuple = ROOT.TNtuple("ntuple","ntuple","before:after"); gcs.append(ntuple)

        assert len(eventDatas[0][0]) == len(eventDatas[1][0])

        for before, after in zip(eventDatas[0][0], eventDatas[1][0]):
            if before != None and after != None:
                ntuple.Fill(before,after)
            else:
                # print "UUU before=",before,"after=",after
                pass

        # make plots
        gcs.append(ROOT.TCanvas())
        
        ntuple.SetMarkerStyle(20)
        ntuple.Draw("(after - before) / before:before")
        
        


