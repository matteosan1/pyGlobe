#!/usr/bin/env python

import sys

import utils

#----------------------------------------------------------------------

inputFname = "workspace.root"

outputFname = "workspace-sigfit.root"

wsname = "CMS_emu_workspace"

massVarName = "CMS_emu_mass"

#----------------------------------------------------------------------

def getObj(ws, name):

    retval = ws.obj(name)

    if retval == None:
        print >> sys.stderr,"could not get object '%s' from workspace '%s', exiting" % (name, ws.GetName())
        sys.exit(1)

    return retval

#----------------------------------------------------------------------

def getCatEntries(catvar):
    # catvar should e.g. be a RooCategory object

    retval = []

    oldIndex = catvar.getIndex()

    for index in range(catvar.numTypes()):
        catvar.setIndex(index)
        retval.append(catvar.getLabel())

    catvar.setIndex(oldIndex)

    return retval

#----------------------------------------------------------------------

def getGaussianVars(ws, varname, proc, mass, catname):
    import itertools

    retval = []

    for gaussIndex in itertools.count():
        name = utils.makeGaussianVarname("sigma",
                                         proc,
                                         mass,
                                         catname,
                                         gaussIndex)

        obj = ws.obj(name)
        if obj == None:
            break
        
        retval.append(obj)

    return retval

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
# script for fitting the signal models

import ROOT; gcs = []

fin = ROOT.TFile(inputFname)
assert fin.IsOpen(), "could not open input workspace file " + inputFname

ws = fin.Get(wsname)

assert ws != None, "could not find workspace '%s' in file '%s'" % (wsname, inputFname)

massVar = getObj(ws, massVarName)

# get the list of all categories
allCats = getCatEntries(getObj(ws, 'allCategories'))
allMasses = [ int(x) for x in getCatEntries(getObj(ws, 'allSigMasses')) ]
allProcs = getCatEntries(getObj(ws, 'allSigProcesses'))

for cat in allCats:
    for proc in allProcs:

        # produce one frame with all the mass hypotheses
        frame = massVar.frame(110,160)
        frame.SetTitle("%s %s" % (cat, proc))
        gcs.append(ROOT.TCanvas())

        for mass in allMasses:

            # get the signal MC dataset
            # e.g. sig_Hem_unbinned_ggh_115_cat7
            dataset = getObj(ws, "sig_Hem_unbinned_%s_%d_%s" % (proc, mass, cat))
            
            # get the signal pdf
            # e.g. sigpdf_vbf_115_cat8
            pdf = getObj(ws, "sigpdf_%s_%d_%s" % (proc, mass, cat))

            pdf.fitTo(dataset,
                      ROOT.RooFit.Range(mass - 5, mass + 5),
                      )

            if True:
                # add to the plot

                dataset.plotOn(frame,
                               # ROOT.RooFit.Range(110,160)
                               )
                pdf.plotOn(frame,
                           # ROOT.RooFit.Range(110,160)
                           )


            #----------
            # fix the fitted parameters
            #----------

            sigmaVars = getGaussianVars(ws, "sigma", proc, mass, cat)
            dmuVars   = getGaussianVars(ws, "dmu", proc, mass, cat)

            for var in sigmaVars + dmuVars:
                var.setConstant(True)

            #----------

        # end of loop over masses
        frame.Draw()

    # end of loop over signal processes

# end of loop over categories
                             
# write the fitted workspace out
ws.writeToFile(outputFname)
