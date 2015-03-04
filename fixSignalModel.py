#!/usr/bin/env python

import sys, utils

# add some customization for the signal model
#
# for ggh cat9, take the shapes from cat10 ggh but the normalization
# from cat9 ggh

#----------------------------------------------------------------------
wsname = "CMS_emu_workspace"

# name of reconstructed mass variable
massVarName = "CMS_emu_mass"

# name of Higgs mass hypothesis variable (created by this script)
massHypName = "MH"


#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
ARGV = sys.argv[1:]

inputFname, outputFname = ARGV

import ROOT; gcs = []
ROOT.gROOT.SetBatch(1)


fin = ROOT.TFile(inputFname)
assert fin.IsOpen(), "could not open input workspace file " + inputFname

ws = fin.Get(wsname)

assert ws != None, "could not find workspace '%s' in file '%s'" % (wsname, inputFname)
#----------

# rather than cloning the pdf we just copy the parameters over
# (so that the parameters are not shared)

origPdf = utils.getObj(ws, "sigpdf_ggh_cat9")

# loop over leaf nodes

for leaf in utils.getLeafNodes(origPdf):

    name = leaf.GetName()

    if not 'ggh_cat9' in name:
        continue

    # print leaf

    # copy the corresponding value from cat10 ggh
    srcObj = utils.getObj(ws, name.replace('cat9','cat10'))

    # copy the range and value
    leaf.setRange(srcObj.getMin(), srcObj.getMax())
    leaf.setVal(srcObj.getVal())

#----------
# write the fitted workspace out
#----------
ws.writeToFile(outputFname)

