#!/usr/bin/env python

import sys, utils, itertools
from utils import saveAllCanvases
gcs = []

# make plots of quantities related to the signal fits
# (to check the quality of the fits)

#----------------------------------------------------------------------

wsname = "CMS_emu_workspace"

# name of reconstructed mass variable
massVarName = "CMS_emu_mass"

# name of Higgs mass hypothesis variable (created by this script)
massHypName = "MH"

#----------------------------------------------------------------------

def plotSignalFitsVsMC(ws, recoMassVar, cat, proc):

    # produce one frame with all the mass hypotheses
    # for the comparison of signal fits to signal MC
    frame = recoMassVar.frame()
    frame.SetTitle("signal fit vs. MC %s %s" % (cat, proc))
    gcs.append(frame)
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

#----------------------------------------------------------------------

def plotParameterEvolution(ws, mhypVar, cat, proc):

    for varname in ("sigma", "dmu", "frac"):

        # plot all functions of the same type on the same
        # frame (useful e.g. to make sure that the sigma
        # parameters do not cross)
        frame = mhypVar.frame(); gcs.append(frame)
        frame.SetTitle("%s %s %s" % (varname, cat, proc))
        gcs.append(ROOT.TCanvas())
        
        for gaussIndex in itertools.count():
            funcname = utils.makeGaussianVarname("interp_" + varname,
                                                 proc,
                                                 None, # mhyp
                                                 cat,
                                                 gaussIndex
                                                 )

            func = ws.obj(funcname)

            print "ZZ",funcname,func

            # check if this object is present in the workspace
            # if not, stop the loop
            if func == None:
                break

            func.plotOn(frame)

        # end of loop over Gaussian components
        frame.Draw()

    # end of loop over variables

    #----------
    # plot evolution of the normalization variable
    # (which does NOT have Gaussian components)
    #----------

    # signal normalization function
    suffix = "_".join([
        proc,
        cat,
        ])
    pdfname = "sigpdf_" + suffix
    funcname = pdfname + "_norm"

    func = utils.getObj(ws,funcname)

    frame = mhypVar.frame(); gcs.append(frame)
    frame.SetTitle("signal normalization %s %s" % (cat, proc))
    gcs.append(ROOT.TCanvas())

    func.plotOn(frame)
    frame.Draw()
    

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
ARGV = sys.argv[1:]

assert len(ARGV) == 1

inputFname = ARGV.pop(0)

import ROOT 

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

        #----------
        # plot signal fit vs. MC sample (signal)
        #----------
        plotSignalFitsVsMC(ws, recoMassVar, cat, proc)

        #----------
        # draw evolution of interpolated parameters vs. mass hypothesis
        #----------
        plotParameterEvolution(ws, mhypVar, cat, proc)

        #----------
        # plot the interpolated signal PDFs at more values of mhyp
        #----------

        


        

    # end of loop over processes
# end of loop over categories

saveAllCanvases()
    
print "saveAllCanvases()"
