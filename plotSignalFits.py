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

def plotInterpolatedPdf(ws, mhypVar, recoMassVar, cat, proc):

    numPoints = 21

    import numpy
    massValues = numpy.linspace(mhypVar.getMin(),
                                mhypVar.getMax(),

                                numPoints) 

    suffix = "_".join([
        proc,
        cat,
        ])
    pdfname = "sigpdf_" + suffix

    pdf = utils.getObj(ws,pdfname)

    normFunc = utils.getObj(ws,pdfname + "_norm")

    # build an extended pdf

    extPdf = ROOT.RooExtendPdf("ext_" + pdfname,
                               "ext_" + pdfname,
                               pdf,
                               normFunc)

    frame = recoMassVar.frame(); gcs.append(frame)
    frame.SetTitle("interpolated signal pdf %s %s" % (cat, proc))
    gcs.append(ROOT.TCanvas())

    for massValue in massValues:
        mhypVar.setVal(massValue)

        extPdf.plotOn(frame, ROOT.RooFit.Normalization(normFunc.getVal(),
                                                       ROOT.RooAbsReal.NumEvent))


    frame.Draw()

    

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
from optparse import OptionParser
parser = OptionParser("""

  usage: %prog [options] input_file

  produces control plots for signal model building
"""
)

parser.add_option("--simultaneous",
                  default = False,
                  action = "store_true",
                  help="look for simultaneous fit objects instead of standard ones",
                  )

parser.add_option("--cat",
                  dest = "cats",
                  type = str,
                  default = None,
                  help="comma separated list of category names (default is to use all found in the workspace)",
                  )

parser.add_option("--proc",
                  dest = "procs",
                  type = str,
                  default = None,
                  help="comma separated list of process names (default is to use all found in the workspace)",
                  )

(options, ARGV) = parser.parse_args()

if options.cats != None:
    options.cats = options.cats.split(',')

if options.procs != None:
    options.procs = options.procs.split(',')

#----------------------------------------

assert len(ARGV) == 1

inputFname = ARGV.pop(0)

#----------------------------------------


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
if options.cats == None:
    allCats   = utils.getCatEntries(utils.getObj(ws, 'allCategories'))
else:
    allCats = options.cats

allMasses = [ int(x) for x in utils.getCatEntries(utils.getObj(ws, 'allSigMasses')) ]

if options.procs == None:
    allProcs  = utils.getCatEntries(utils.getObj(ws, 'allSigProcesses'))
else:
    allProcs = options.procs

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
        plotInterpolatedPdf(ws, mhypVar, recoMassVar, cat, proc)
        

    # end of loop over processes
# end of loop over categories

saveAllCanvases()
    
print "saveAllCanvases()"
