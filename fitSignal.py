#!/usr/bin/env python

import sys

import utils

#----------------------------------------------------------------------

inputFname = "workspace.root"

outputFname = "workspace-sigfit.root"

wsname = "CMS_emu_workspace"

massVarName = "CMS_emu_mass"

#----------------------------------------------------------------------

def saveAllCanvases(suffix = "png"):
    import ROOT

    canvases = ROOT.gROOT.GetListOfCanvases()
    num = canvases.GetSize()

    for i in range(num):
        canv = canvases.At(i)
        canv.SaveAs("plot-%02d.%s" % (i, suffix))

#----------------------------------------------------------------------

def getGaussianVars(ws, varname, proc, mass, catname):
    import itertools

    retval = []

    for gaussIndex in itertools.count():
        name = utils.makeGaussianVarname(varname,
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

def getFitParam(fitparams, paramName, proc, mass, catname, defaultValue):
    if fitparams == None:
        return defaultValue

    if not fitparams.has_key(catname):
        return defaultValue

    tmp = fitparams[catname]

    if not tmp.has_key(proc):
        return defaultValue

    tmp = tmp[proc]

    if not tmp.has_key(mass):
        return defaultValue

    tmp = tmp[mass]


    return tmp.get(paramName, defaultValue)


#----------------------------------------------------------------------

def setVariableRange(fitparams,
                     paramPrefix,
                     var,
                     proc,
                     mass,
                     cat
                     ):
    # sets the range and initial value of a RooRealVar from the values
    # specified in the parameters

    # get the parameters

    minVal     = getFitParam(fitparams, paramPrefix + "_min", proc, mass, cat, None)
    maxVal     = getFitParam(fitparams, paramPrefix + "_max", proc, mass, cat, None)
    initialVal = getFitParam(fitparams, paramPrefix + "_initial", proc, mass, cat, None)

    print "PPP",var.GetName(),minVal,maxVal,initialVal

    if minVal != None and maxVal != None:
        # set the range
        var.setRange(minVal,maxVal)
    elif minVal != None:
        var.setMin(minVal)
    elif maxVal != None:
        var.setMax(maxVal)

    if initialVal != None:
        var.setVal(initialVal)

    # if maxVal != None:
    #     var.Print()
    #     sys.exit(1)

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
# script for fitting the signal models

ARGV = sys.argv[1:]

if ARGV:
    # assume this is the name of a fit parameter settings file in python format
    import imp
    configFname = ARGV.pop(0)
    parametersModule = imp.load_source('parameters', configFname)

    fitparams = parametersModule.params
else:
    fitparams = {}


import ROOT; gcs = []
ROOT.gROOT.SetBatch(1)


fin = ROOT.TFile(inputFname)
assert fin.IsOpen(), "could not open input workspace file " + inputFname

ws = fin.Get(wsname)

assert ws != None, "could not find workspace '%s' in file '%s'" % (wsname, inputFname)

massVar = utils.getObj(ws, massVarName)

# get the list of all categories
allCats   = utils.getCatEntries(utils.getObj(ws, 'allCategories'))
allMasses = [ int(x) for x in utils.getCatEntries(utils.getObj(ws, 'allSigMasses')) ]
allProcs  = utils.getCatEntries(utils.getObj(ws, 'allSigProcesses'))

for cat in allCats:
    for proc in allProcs:

        # produce one frame with all the mass hypotheses
        frame = massVar.frame(110,160)
        frame.SetTitle("%s %s" % (cat, proc))
        gcs.append(ROOT.TCanvas())

        # fitted values for this category and signal process
        # first index is the Gaussian component number
        # second index is the mass point index
        sigmaValues = []
        dmuValues = []

        for mass in allMasses:

            # get the signal MC dataset
            # e.g. sig_Hem_unbinned_ggh_115_cat7
            dataset = utils.getObj(ws, "sig_Hem_unbinned_%s_%d_%s" % (proc, mass, cat))
            
            # get the signal pdf
            # e.g. sigpdf_vbf_115_cat8
            pdf = utils.getObj(ws, "sigpdf_%s_%d_%s" % (proc, mass, cat))

            #----------
            # adjust fit parameters if specified
            #----------

            sigmaVars = getGaussianVars(ws, "sigma", proc, mass, cat)
            dmuVars   = getGaussianVars(ws, "dmu", proc, mass, cat)

            numGaussians = len(sigmaVars)
            assert numGaussians == len(dmuVars)

            for varname, vars in (("sigma", sigmaVars),
                                  ("dmu",   dmuVars)):
                for gaussianIndex in range(numGaussians):

                    # set the variable range and initial value of this variable
                    setVariableRange(fitparams,
                                     varname + "%d" % gaussianIndex,
                                     vars[gaussianIndex],
                                     proc,
                                     mass,
                                     cat)
                # end of loop over Gaussian components
            # end of loop over variables

            #----------
            # perform the fit
            #----------

            pdf.fitTo(dataset,
                      ROOT.RooFit.Minimizer("Minuit2"),
                      ROOT.RooFit.Range(mass + getFitParam(fitparams, "fitRangeLeft",  proc, mass, cat, - 5),
                                        mass + getFitParam(fitparams, "fitRangeRight", proc, mass, cat, +5)),
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
            # normalization object
            #----------

            sumWeights = dataset.sumEntries()
            normVar = ROOT.RooRealVar(pdf.GetName() + "_norm",
                                      pdf.GetName() + "_norm",
                                      sumWeights,
                                      0,
                                      sumWeights); gcs.append(normVar)
            normVar.setConstant(True)
                                      
            getattr(ws, 'import')(normVar)

            #----------
            # fix the fitted parameters and read the fitted values
            #----------

            # TODO: sort the Gaussian components, e.g. according to the width

            for vars, values in ((sigmaVars, sigmaValues),
                                 (dmuVars, dmuValues)):

                if len(values) == 0:
                    values.extend([[ ] for i in range(numGaussians) ] )

                for gaussIndex, var in enumerate(vars):
                    var.setConstant(True)
                    values[gaussIndex].append(var.getVal())

            #----------


        # end of loop over masses
        frame.Draw()

        #----------
        # produce the interpolating objects
        #----------
        for varname, values in (("sigma", sigmaValues),
                              ("dmu", dmuValues)):

            for gaussIndex in range(len(values)):
                funcname = utils.makeGaussianVarname("interp_" + varname,
                                          proc,
                                          None, # mhyp
                                          cat,
                                          gaussIndex
                                          )

                print "ZZ",values[gaussIndex]
                func = utils.makePiecewiseLinearFunction(funcname,
                                                         massVar,
                                                         allMasses,
                                                         values[gaussIndex])

                # import this function into the workspace
                getattr(ws, 'import')(func, ROOT.RooFit.RecycleConflictNodes())
            # end of loop over Gaussian components

        # end of loop over variables

        # TODO: build the interpolated signal PDF


    # end of loop over signal processes

# end of loop over categories
                             
# write the fitted workspace out
ws.writeToFile(outputFname)

print "saveAllCanvases()"
