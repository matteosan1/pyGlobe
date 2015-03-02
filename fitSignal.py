#!/usr/bin/env python

import sys

import utils

#----------------------------------------------------------------------

wsname = "CMS_emu_workspace"

# name of reconstructed mass variable
massVarName = "CMS_emu_mass"

# name of Higgs mass hypothesis variable (created by this script)
massHypName = "MH"


# number of Gaussian components to fit an individual cat/proc/mass point
numGaussians = 2

#----------------------------------------------------------------------

def makeSignalPdfsForFit(ws, catname, proc, recoMassVar, signalMasses):
    # produces sum of Gaussian PDFs for fitting (i.e. without interpolation, independent
    # at each mass point)

    # assume we have all signal processes at all signal mass points

    # signalMasses is assumed to be ordered
    for massIndex, mhyp in enumerate(signalMasses):
        suffix = "_".join([
            proc,
            str(mhyp),
            catname,
            ])

        # create the delta mu and sigma vars
        dmuvars = [ ROOT.RooRealVar(utils.makeGaussianVarname("dmu", proc, mhyp, catname, gaussIndex),
                                    "delta mu",
                                    gaussIndex,
                                    -1.5,
                                    +1.5)
                    for gaussIndex in range(numGaussians)]
        sigmavars = [ ROOT.RooRealVar(utils.makeGaussianVarname("sigma", proc, mhyp, catname, gaussIndex),
                                    "sigma",
                                    1 + gaussIndex,
                                    0.01,
                                    10)
                    for gaussIndex in range(numGaussians)]

        fractionvars = [ ROOT.RooRealVar(utils.makeGaussianVarname("frac", proc, mhyp, catname, gaussIndex),
                                         "fraction variable for Gaussian sum",
                                         0.5,
                                         0,
                                         1)
                         for gaussIndex in range(numGaussians - 1)]

        pdf = utils.makeSumOfGaussians("sigpdf_" + suffix,
                                       recoMassVar,
                                       mhyp,
                                       dmuvars,
                                       sigmavars,
                                       fractionvars)

        # import into workspace
        if ws != None:
            getattr(ws, 'import')(pdf, ROOT.RooFit.RecycleConflictNodes())
    # end of loop over masses

#----------------------------------------------------------------------

def getGaussianVars(ws, varname, proc, mass, catname):
    # searches parameter variables of the Gaussians
    # in the workspace
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

def doFitsClassic(ws, mhypVar, recoMassVar, cat, proc, allMasses, massScaleNuisance, resolutionNuisance):
    # classic fitting of signal MC

    # fitted values for this category and signal process
    # first index is the Gaussian component number
    # second index is the mass point index
    sigmaValues = []
    dmuValues = []
    fracValues = []
    normValues = []

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
        dmuVars   = getGaussianVars(ws, "dmu",   proc, mass, cat)
        fracVars  = getGaussianVars(ws, "frac",  proc, mass, cat)

        numGaussians = len(sigmaVars)

        assert numGaussians == len(dmuVars)
        assert numGaussians == len(fracVars) + 1

        for varname, vars in (("sigma", sigmaVars),
                              ("dmu",   dmuVars),
                              ):
            for gaussianIndex in range(len(vars)):

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

                  # take MC statistics error, not error on number of events...
                  ROOT.RooFit.SumW2Error(False),

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

        normValues.append(sumWeights)

        #----------
        # sort the Gaussian components according to the width
        #----------

        indices = sorted(range(numGaussians), key = lambda index: sigmaVars[index].getVal() )

        # instead of reordering the objects, we re-assign the values
        utils.reassignValues(indices, sigmaVars)
        utils.reassignValues(indices, dmuVars)

        # note that for the fractions (which are continued fractions),
        # we must expand them, sort and then collapse again
        # (the values will be different !)

        expandedFracValues = utils.expandContinuedFraction([ x.getVal() for x in fracVars])
        expandedFracValues = utils.reorder(indices, expandedFracValues)
        unexpandedFracValues = utils.collapseContinuedFraction(expandedFracValues)
        for value, var in zip(unexpandedFracValues, fracVars):
            var.setVal(value)

        #----------
        # fix the fitted parameters and read the fitted values
        #----------

        for vars, values in ((sigmaVars, sigmaValues),
                             (dmuVars, dmuValues),
                             (fracVars, fracValues),
                             ):

            if len(values) == 0:
                values.extend([[ ] for i in range(len(vars)) ] )

            # freeze the fitted variables at the fit final values
            # and add the values to a list for interpolation
            for gaussIndex, var in enumerate(vars):
                var.setConstant(True)
                values[gaussIndex].append(var.getVal())

        #----------


    # end of loop over masses

    #----------
    # produce the interpolating objects
    #----------
    interpDmuFuncs = []
    interpSigmaFuncs = []
    interpFracFuncs = []

    for varname, values, interpFuncs in (("sigma", sigmaValues, interpSigmaFuncs),
                                         ("dmu", dmuValues, interpDmuFuncs),
                                         ("frac", fracValues, interpFracFuncs)):

        for gaussIndex in range(len(values)):
            funcname = utils.makeGaussianVarname(varname + "func",
                                      proc,
                                      None, # mhyp
                                      cat,
                                      gaussIndex
                                      )

            func = utils.makePiecewiseLinearFunction(funcname,
                                                     mhypVar,
                                                     allMasses,
                                                     values[gaussIndex])

            # import this function into the workspace
            getattr(ws, 'import')(func, ROOT.RooFit.RecycleConflictNodes())

            interpFuncs.append(func)

        # end of loop over Gaussian components

    # end of loop over variables

    #----------
    # build the interpolated signal PDF
    #----------

    # example name: sigpdf_vbf_cat6

    suffix = "_".join([
        proc,
        # str(mhyp), # not used here
        cat,
        ])

    pdfname = "sigpdf_" + suffix
    pdf = utils.makeSumOfGaussians(pdfname,
                                   recoMassVar,       # reconstructed mass
                                   mhypVar,       # Higgs mass hypothesis
                                   interpDmuFuncs,
                                   interpSigmaFuncs,
                                   interpFracFuncs,
                                   massScaleNuisance = massScaleNuisance,
                                   resolutionNuisance = resolutionNuisance,
                                   ); gcs.append(pdf)

    # import this function into the workspace
    getattr(ws, 'import')(pdf, ROOT.RooFit.RecycleConflictNodes())

    #----------
    # build the interpolated normalization function
    #----------
    normfunc = utils.makePiecewiseLinearFunction(pdfname + "_norm",
                                                 mhypVar,
                                                 allMasses,
                                                 normValues); gcs.append(normfunc)

    # import this function into the workspace
    getattr(ws, 'import')(normfunc, ROOT.RooFit.RecycleConflictNodes())


#----------------------------------------------------------------------

def makeBernsteinFormula(degree, formulaName, addMassToFormulaName, xmin, xmax, ymin, ymax, massHypVar, coeffsDict, setCoeffsConstant):
    # if coeffsDict is not None, parameters are first searched for there (by name)
    # and if not existing, created parameters will be added there 
    #
    # addMassToFormulaName is normally set to True during the fitting
    # (the mass is NOT added to the coefficients of the function which
    #  are common across all mass hyptheses) and set to False
    #  when producing the final function 

    parts = []

    args = ROOT.RooArgList()

    args.add(massHypVar)

    import scipy.misc

    inverseRange = 1 / float(xmax - xmin)

    coeffList = []
    
    for i in range(degree + 1):
        # see http://en.wikipedia.org/wiki/Bernstein_polynomial#Definition

        name = formulaName + "_c%d" % i

        if coeffsDict != None and coeffsDict.has_key(name):
            # re-use existing parameter
            coeff = coeffsDict[name]
        else:
            # create a coefficient
            coeff = ROOT.RooRealVar(name,
                                    name,
                                    0.5 * (ymax + ymin),
                                    ymin,
                                    ymax); gcs.append(coeff)

            if coeffsDict != None:
                coeffsDict[name] = coeff

        if setCoeffsConstant:
            coeff.setConstant(True)
            
        args.add(coeff)

        combFactor = scipy.misc.comb(degree, i)

        argIndex = i+1
        icomplement = degree - i

        parts.append("@{argIndex} * {combFactor} * pow({inverseRange} * (@0 - {xmin}),{i}) * pow({inverseRange} * ({xmax} - @0), {icomplement})".format(**locals()))

    formula = " + ".join(parts)

    if addMassToFormulaName:
        formulaName += "_m%d" % int(massHypVar.getVal() + 0.5)

    return ROOT.RooFormulaVar(formulaName,
                              formulaName,
                              formula,
                              args)


#----------------------------------------------------------------------

def makeGaussianSum(mhypVar, recoMassVar, massForName, xmin, xmax, coeffsDict, finalName = None,
                    massScaleNuisance = None, resolutionNuisance = None, setCoeffsConstant = False):
    # produces a sum of Gaussians (for the simultaneous case, similar to utils.makeSumOfGaussians(..) )
    # 
    # param massForName is the mass to be used in the name of the final
    # addPdf (this can be set to None to build the final PDF or a
    # given mass for the fitting stage)

    addMassToFormulaName = (massForName != None)

    #----------
    # build the expressions for the base polynomials (Bernstein polynimials) for the parameter
    # evolutions
    #
    # we plug in the mass values explicitly during the fit to create a separate PDF for
    # each mass hypothesis
    #----------

    # degree of polynomial for interpolation across mass hypotheses
    polynomialDegree = 2

    fractionsForGaussian = ROOT.RooArgList()
    gaussianPdfs = ROOT.RooArgList()

    for gaussIndex in range(numGaussians):

        # build the Gaussian from the mu and sigma functions
        # we build one 'function' (with the mass argument fixed)
        # for each mass point

        #----------
        # deltaMu
        #----------

        name = utils.makeGaussianVarname("dmufunc",
                                         proc,
                                         None, # no mass, use common coefficients 
                                         cat,
                                         gaussIndex)

        dmuFunc = makeBernsteinFormula(polynomialDegree,
                                       name,
                                       addMassToFormulaName,
                                       xmin, xmax,
                                       -10,10, # y range
                                       mhypVar, coeffsDict, setCoeffsConstant); gcs.append(dmuFunc)

        #----------
        # build mu from delta mu
        #----------
        name = utils.makeGaussianVarname("mufunc",
                                         proc,
                                         None, # no mass, use common coefficients 
                                         cat,
                                         gaussIndex)

        if massScaleNuisance != None:
            formula = "(@0 + @1) * @2"
            args = ROOT.RooArgList(mhypVar, dmuFunc, massScaleNuisance)
        else:
            # no mass scale nuisance specified
            formula = "@0 + @1"
            args = ROOT.RooArgList(mhypVar, dmuFunc)

        muFunc = ROOT.RooFormulaVar(name, name,
                                    formula,
                                    args); gcs.append(muFunc)

        #----------
        # sigma
        #----------
        name = utils.makeGaussianVarname("sigmafunc",
                                         proc,
                                         None, # no mass, use common coefficients 
                                         cat,
                                         gaussIndex)


        sigmaFunc = makeBernsteinFormula(polynomialDegree,
                                         name,
                                         addMassToFormulaName,
                                         xmin, xmax,
                                         0,10, # y range
                                         mhypVar, coeffsDict, setCoeffsConstant); gcs.append(sigmaFunc)

        if resolutionNuisance != None:
            sigmaFunc = ROOT.RooFormulaVar("nuisancedSigmaFunc" + name[9:],
                                           "nuisancedSigmaFunc" + name[9:],
                                           "@0 * @1",
                                           ROOT.RooArgList(sigmaFunc, resolutionNuisance)); gcs.append(sigmaFunc)
        

        #----------                                            
        # build the Gaussian
        #----------
        name = utils.makeGaussianVarname("gauss",
                                         proc,
                                         None, # no mass, use common coefficients 
                                         cat,
                                         gaussIndex)

        gaussian = ROOT.RooGaussian(name, name,
                                    recoMassVar,
                                    muFunc,
                                    sigmaFunc); gcs.append(gaussian)
        gaussianPdfs.add(gaussian)

        #----------
        # create a weighting coefficient
        #----------
        if gaussIndex > 0:

            name = utils.makeGaussianVarname("fracfunc",
                                             proc,
                                             None, # no mass, use common coefficients 
                                             cat,
                                             gaussIndex - 1)

            fracFunc = makeBernsteinFormula(polynomialDegree,
                                            name,
                                            addMassToFormulaName,
                                            xmin, xmax,
                                            0,1, # y range
                                            mhypVar, coeffsDict, setCoeffsConstant); gcs.append(fracFunc)

            fractionsForGaussian.add(fracFunc)

    # end of loop over Gaussians

    #----------
    # build the RooAddPdf
    #----------
    if finalName == None:
        finalName = utils.makeGaussianVarname("addpdf",
                                         proc,
                                         massForName,
                                         cat,
                                         None)

    addPdf = ROOT.RooAddPdf(finalName, finalName,
                            gaussianPdfs,
                            fractionsForGaussian); gcs.append(addPdf)


    return addPdf


#----------------------------------------------------------------------

def fitNormalizations(funcName, massHypVar, masses, normValues, numMCevents):
    # this is used for fitting the normalization with a polynomial
    # (only used for simulatenous fitting)
    #
    # we take 1 / sqrt(numMCevents) as a relative error

    import array, math

    numPoints = len(masses)
    assert len(normValues) == numPoints
    assert len(numMCevents) == numPoints

    # build a TGraph which we can fit to a function
    xerrs = [ 1.0 ] * numPoints
    
    yerrs = [ normVal / math.sqrt(events) for normVal, events in zip(normValues, numMCevents) ]

    # use this instead of RooAbsReal::chi2FitTo(..)
    # as it is not clear to me how the latter e.g.
    # takes the errors on the y values...
    graph = ROOT.TGraphErrors(numPoints,
                              array.array('f', masses),
                              array.array('f', normValues),
                              array.array('f', xerrs),
                              array.array('f', yerrs),
                              )

    # for some reason, can't directly specify the formula
    # in TGraph.Fit(..), need to create a TF1 first...

    func = ROOT.TF1("normfitfunc", "[0]+x*[1]+x*x*[2]", mhypVar.getMin(), mhypVar.getMax())

    fitres = graph.Fit(func,
                       "S" # save the result
                       )

    fitres2 = fitres.Get()

    # create a RooFormulaVar with the fit result
    return ROOT.RooFormulaVar(funcName, "fitted signal normalization",
                              "%f + %f * @0 + %f * @0 * @0" % (
                                  fitres2.Parameter(0),
                                  fitres2.Parameter(1),
                                  fitres2.Parameter(2),
                                  ),
                              ROOT.RooArgList(massHypVar))
    

#----------------------------------------------------------------------

def doFitsSimultaneous(ws, mhypVar, recoMassVar, cat, proc, allMasses, massScaleNuisance, resolutionNuisance):
    # simultaneous fit across multiple mass hypotheses

    mhypVars = []

    # number of expected signal events
    normValues = []
    numMCevents = [] # for determining the error on the norm value

    # one 'category' per mass point for the simultaneous fit
    pdfsForSimultaneous = ROOT.RooArgList()
    catsForSimultaneous = ROOT.RooCategory("massPoint", "massPoint")

    for mass in allMasses:
        catsForSimultaneous.defineType("m%d" % mass)

    #----------
    # build a simultaneous pdf
    #----------
    name = utils.makeGaussianVarname("simultaneousPdf",
                                     proc,
                                     None, # mass
                                     cat,
                                     None # gauss index
                                     )
    simultaneousPdf = ROOT.RooSimultaneous(name, name, catsForSimultaneous)

    #----------

    # see https://root.cern.ch/phpBB3/viewtopic.php?f=15&t=16882
    # ROOT.gInterpreter.GenerateDictionary("std::pair<std::string, RooDataSet*>", "map;string;RooDataSet.h")
    # datasetsForSimultaneous = ROOT.std.map('string, RooDataSet*')(); gcs.append(datasetsForSimultaneous)

    datasetsForSimultaneous = []

    # coefficients for the interpolating functions
    coeffsDict = {}

    for mass in allMasses:
        # make fixed value mass variables

        thisMhypVar = ROOT.RooRealVar("mass_" + str(mass),
                                      "mass_" + str(mass),
                                      mass,
                                      mass,
                                      mass); gcs.append(thisMhypVar)
        thisMhypVar.setConstant(True)
        mhypVars.append(thisMhypVar)


        addPdf = makeGaussianSum(thisMhypVar, recoMassVar, mass, mhypVar.getMin(), mhypVar.getMax(), coeffsDict)

        simultaneousPdf.addPdf(addPdf, "m%d" % mass)

        #----------
        # add to the list of the datasets
        #----------
        # see https://root.cern.ch/phpBB3/viewtopic.php?f=15&t=16882
        ds = utils.getObj(ws, "sig_Hem_unbinned_%s_%d_%s" % (proc, mass, cat)); gcs.append(ds)

        normValues.append(ds.sumEntries())
        numMCevents.append(ds.numEntries())

        datasetsForSimultaneous.append(ds)

        # pair = ROOT.std.pair('string, RooDataSet*')(simultaneousCatName, ds)

        # this line causes a problem with dictionary generation
        # and an empty file name in an include statement...
        # but it still works ?!
        # beg = datasetsForSimultaneous.begin()


        # datasetsForSimultaneous.insert(beg,pair)

        
    # end of loop over masses

    #----------
    # build a simultaneous dataset
    #----------

    name = utils.makeGaussianVarname("simultaneousData",
                                     proc,
                                     None, # mass
                                     cat,
                                     None # gauss index
                                     )

    # ugly hack, works as long as ew don't have too many mass points
    # (I could not get this here to work: https://root.cern.ch/phpBB3/viewtopic.php?f=15&t=16882 )
    simultaneousDataset = eval("ROOT.RooDataSet(name, name, ROOT.RooArgSet(recoMassVar), ROOT.RooFit.Index(catsForSimultaneous),%s)" % ",".join(
        [ 'ROOT.RooFit.Import("m%d", datasetsForSimultaneous[%d])' % (mass, index) for index,mass in enumerate(allMasses) ]))

    #----------
    # perform the fit
    #----------

    simultaneousPdf.fitTo(simultaneousDataset,
                          ROOT.RooFit.Minimizer("Minuit2"),
                          # ROOT.RooFit.Range(mass + getFitParam(fitparams, "fitRangeLeft",  proc, mass, cat, - 5),
                          #mass + getFitParam(fitparams, "fitRangeRight", proc, mass, cat, +5)),

                          # take MC statistics error, not error on number of events...
                          ROOT.RooFit.SumW2Error(False),
                          )

    #----------
    # rebuild the interpolating functions
    # (this time with one single mass hypothesis variable)
    #----------


    #----------
    # rebuild one RooAddPdf with the interpolating functions
    #----------

    # example name: sigpdf_vbf_cat6
    suffix = "_".join([
        proc,
        # str(mhyp), # not used here
        cat,
        ])

    pdfname = "sigpdf_" + suffix

    # after fitting, make nuisances non-constant
    massScaleNuisance.setConstant(False)
    resolutionNuisance.setConstant(False)

    finalPdf = makeGaussianSum(mhypVar, recoMassVar, None, mhypVar.getMin(), mhypVar.getMax(), coeffsDict,
                               pdfname,

                               massScaleNuisance = massScaleNuisance,
                               resolutionNuisance = resolutionNuisance,

                               # set the coefficients of the polynomial constant now (otherwise combine will move them around..)
                               setCoeffsConstant = True,

                               ); gcs.append(finalPdf)

    # import this pdf into the workspace
    getattr(ws, 'import')(finalPdf, ROOT.RooFit.RecycleConflictNodes())

    #----------
    # build the interpolated normalization function
    #----------
    if False:
        normfunc = utils.makePiecewiseLinearFunction(pdfname + "_norm",
                                                     mhypVar,
                                                     allMasses,
                                                     normValues); gcs.append(normfunc)

    # do a fit of a polynomial to the normalization function values
    normfunc = fitNormalizations(pdfname + "_norm",
                                 mhypVar,
                                 allMasses,
                                 normValues,
                                 numMCevents); gcs.append(normfunc)
        
    # import this function into the workspace
    getattr(ws, 'import')(normfunc, ROOT.RooFit.RecycleConflictNodes())


#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
from optparse import OptionParser
parser = OptionParser("""

  usage: %prog [options] input_file output_file

  program for fitting the signal models

"""
)

parser.add_option("--simultaneous",
                  default = False,
                  action = "store_true",
                  help="perform a simultaneous fit (across all mass hypotheses) instead of fitting per mass point",
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

parser.add_option("--param",
                  type = str,
                  default = None,
                  help="name of a python file with parameter restrictions (non-simultaneous only for the moment)",
                  )

(options, ARGV) = parser.parse_args()

if options.cats != None:
    options.cats = options.cats.split(',')

if options.procs != None:
    options.procs = options.procs.split(',')

if len(ARGV) != 2:
    parser.print_help();
    sys.exit(1)

inputFname, outputFname = ARGV

#----------------------------------------

if options.param != None:
    # assume this is the name of a fit parameter settings file in python format
    import imp
    configFname = options.param
    parametersModule = imp.load_source('parameters', configFname)

    fitparams = parametersModule.params
else:
    fitparams = {}

#----------------------------------------

import ROOT; gcs = []
ROOT.gROOT.SetBatch(1)


fin = ROOT.TFile(inputFname)
assert fin.IsOpen(), "could not open input workspace file " + inputFname

ws = fin.Get(wsname)

assert ws != None, "could not find workspace '%s' in file '%s'" % (wsname, inputFname)

# reconstructed mass variable
massVar = utils.getObj(ws, massVarName)

mhypVar = ROOT.RooRealVar(massHypName, "Higgs mass hypothesis variable",
                          massVar.getVal(),
                          massVar.getMin(),
                          massVar.getMax())


# get the list of all categories
if options.cats == None:
    allCats   = utils.getCatEntries(utils.getObj(ws, 'allCategories'))
else:
    allCats = options.cats

allMasses = [ int(x) for x in utils.getCatEntries(utils.getObj(ws, 'allSigMasses')) ]

if options.procs == None:
    allProcs  = utils.getCatEntries(utils.getObj(ws, 'allSigProcesses'))
else:
    allProcs = options.procs


# nuisance parameters
nuisanceVars = []

#----------
# mass scale nuisance parameter centered at 1 -> model this as lnN distributed nuisance
#----------
massScaleNuisance = ROOT.RooRealVar("CMS_emu_scale",
                                    "mass scale nuisance",
                                    1, 0, 2)
massScaleNuisance.setConstant(True)
nuisanceVars.append(massScaleNuisance)

#----------
# resolution nuisance
#----------
resolutionNuisance = ROOT.RooRealVar("CMS_emu_reso",
                                    "mass resolution nuisance",
                                    1, 0, 2)
resolutionNuisance.setConstant(True)
nuisanceVars.append(resolutionNuisance)

#----------
for cat in allCats:
    for proc in allProcs:

        if options.simultaneous:
            doFitsSimultaneous(ws, mhypVar, massVar, cat, proc, allMasses, massScaleNuisance, resolutionNuisance)
        else:
            # create the PDFs to be fitted first
            makeSignalPdfsForFit(ws, cat, proc, massVar, allMasses)
            doFitsClassic(ws, mhypVar, massVar, cat, proc, allMasses, massScaleNuisance, resolutionNuisance)

    # end of loop over signal processes

# end of loop over categories


# set nuisance parameters non-constant after fit
for nuisanceVar in nuisanceVars:
    nuisanceVar.setConstant(False)

                             
# write the fitted workspace out
ws.writeToFile(outputFname)

