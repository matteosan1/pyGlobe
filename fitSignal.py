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

        # fitted values for this category and signal process
        # first index is the Gaussian component number
        # second index is the mass point index
        sigmaValues = []
        dmuValues = []

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
            # fix the fitted parameters and read the fitted values
            #----------

            sigmaVars = getGaussianVars(ws, "sigma", proc, mass, cat)
            dmuVars   = getGaussianVars(ws, "dmu", proc, mass, cat)

            numGaussians = len(sigmaVars)
            assert numGaussians == len(dmuVars)

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
