#!/usr/bin/env python

import sys, utils
from utils import saveAllCanvases

# make plots of quantities related to the signal fits
# (to check the quality of the fits)

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

assert len(ARGV) == 1

inputFname = ARGV.pop(0)

import ROOT; gcs = []

fin = ROOT.TFile(inputFname)
assert fin.IsOpen(), "could not open input workspace file " + inputFname

ws = fin.Get(wsname)

assert ws != None, "could not find workspace '%s' in file '%s'" % (wsname, inputFname)

# reconstructed mass variable
recoMassVar = utils.getObj(ws, massVarName)

mhypVar = utils.getObj(ws, massHypName)

#----------
# get the list of all categories
#----------
allCats   = utils.getCatEntries(utils.getObj(ws, 'allCategories'))
allMasses = [ int(x) for x in utils.getCatEntries(utils.getObj(ws, 'allSigMasses')) ]
allProcs  = utils.getCatEntries(utils.getObj(ws, 'allSigProcesses'))

for cat in allCats:
    for proc in allProcs:

        # produce one frame with all the mass hypotheses
        # for the comparison of signal fits to signal MC
        frame = recoMassVar.frame()
        frame.SetTitle("%s %s" % (cat, proc))
        gcs.append(ROOT.TCanvas())

        for mass in allMasses:

            # get the signal MC dataset
            # e.g. sig_Hem_unbinned_ggh_115_cat7
            dataset = utils.getObj(ws, "sig_Hem_unbinned_%s_%d_%s" % (proc, mass, cat))

            # get the signal pdf
            # e.g. sigpdf_vbf_115_cat8
            pdf = utils.getObj(ws, "sigpdf_%s_%d_%s" % (proc, mass, cat))

            # add to the plot
            dataset.plotOn(frame,
                           # ROOT.RooFit.Range(110,160)
                           )
            pdf.plotOn(frame,
                       # ROOT.RooFit.Range(110,160)
                       )

        # end of loop over masses
        frame.Draw()

    # end of loop over processes
# end of loop over categories

saveAllCanvases()
    
print "saveAllCanvases()"
