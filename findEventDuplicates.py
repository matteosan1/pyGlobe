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

    for index in range(tree.GetEntries()):
        tree.GetEntry(index)

        if not data.has_key(tree.itype):
            data[tree.itype] = collections.Counter()

        key = (tree.run, tree.lumis, tree.event)

        if data[tree.itype][key] != 0:
            print "run=",tree.run,"lumi=",tree.lumis,"event=",tree.event,"found more than once for itype",tree.itype
            unique = False

        data[tree.itype][key] += 1


    if unique:
        print "all events in file",fname,"are unique"

    ROOT.gROOT.cd()
    fin.Close()

