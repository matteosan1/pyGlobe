#!/usr/bin/env python

import sys

# checks for duplicate (run,lumis,event) numbers
# for any itype
# (if there are no such duplicates, we can uniquely
# identify events using these variables)

ARGV = sys.argv[1:]

treename = "opttree"

for fname in ARGV:

    import ROOT

    fin = ROOT.TFile(fname)
    assert fin.IsOpen(), "could not open file " + fname

    tree = fin.Get(treename)

    assert tree != None, "could not find tree " + treename + " in file " + fname


    tree.SetBranchStatus("*",0)
    tree.SetBranchStatus("run",1)
    tree.SetBranchStatus("lumis",1)
    tree.SetBranchStatus("event",1)
    tree.SetBranchStatus("itype",1)

    # first index is itype
    # then we count tuples of (run,lumisection, event)
    data = {}

    import collections

    unique = True

    # allKeys = {}

    for index in range(tree.GetEntries()):
        tree.GetEntry(index)

        run, lumis, event, itype = tree.run, tree.lumis, int(tree.event + 0.5), tree.itype

        if not data.has_key(itype):
            data[itype] = collections.Counter()

        key = (run, lumis, event)

        if data[itype][key] != 0:
            print "run=",run,"lumi=",lumis,"event=",event,"found more than once for itype",itype
            unique = False

        data[itype][key] += 1
        # allKeys.setdefault(itype,[]).append(key)

    if unique:
        print "all events in file",fname,"are unique"


        # cross checking
        # for thisAllKeys in allKeys.values():
        #    assert len(thisAllKeys) == len(set(thisAllKeys))

    ROOT.gROOT.cd()
    fin.Close()

