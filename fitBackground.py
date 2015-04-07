#!/usr/bin/env python

import sys, re, math

import utils

gcs = []

#----------------------------------------------------------------------

wsname = "CMS_emu_workspace"

# name of reconstructed mass variable
massVarName = "CMS_emu_mass"

# name of Higgs mass hypothesis variable (created by this script)
massHypName = "MH"


#----------------------------------------------------------------------

def makeBernstein(recoMassVar, prefix, order):
    # corresponds to getBernstein(..) in PdfModelBuilder.cc

    coeffList = ROOT.RooArgList()
    
    for i in range(order):
        name = "%s_p%d" % (prefix ,i)

        if i < 3:
            # param = new RooRealVar(name.c_str(),name.c_str(),10., 0.,50.);
            # param = ROOT.RooRealVar(name, name, 5., 0.,20.)
            param1 = ROOT.RooRealVar(name + "_sqrt", name + "_sqrt", math.sqrt(5.), - math.sqrt(20.), + math.sqrt(20.))
        else:
            # param = new RooRealVar(name.c_str(),name.c_str(),10., 0.,50.);
            # param = ROOT.RooRealVar(name, name, 5., 0.,20.)
            param1 = ROOT.RooRealVar(name + "_sqrt", name + "_sqrt", math.sqrt(5.), - math.sqrt(20.), + math.sqrt(20.))

        gcs.append(param1)

        param = ROOT.RooFormulaVar(name, name, "@0 * @0", ROOT.RooArgList(param1))

        gcs.append(param)
        coeffList.add(param)

    # end of loop over orders

    return ROOT.RooBernstein(prefix, prefix, recoMassVar, coeffList)

#----------------------------------------------------------------------

def makeExponential(recoMassVar, prefix, order):
    # corresponds to getExponentialSingle(..) in PdfModelBuilder.cc

    if order % 2==0:
        raise Exception("only an odd number of parameters is allowed for exponential functions")

    nfracs = (order - 1) / 2
    nexps = order - nfracs

    assert nfracs == nexps-1
    
    fracs = ROOT.RooArgList()
    exps  = ROOT.RooArgList()

    # generate the parameters
    for i in range(1, nfracs + 1):
        name =  "%s_f%d" % (prefix, i)
        param = ROOT.RooRealVar(name, name,
                                0.9 - float(i-1)*1./nfracs,
                                0.0001, 0.9999)
        fracs.add(param)
        gcs.append(param)

    for i in range(1, nexps + 1):

        name  = "%s_p%d" % (prefix, i)
        ename = "%s_e%d" % (prefix, i)
        param = ROOT.RooRealVar(name, name,
                                max(-2. , -0.04 * (i+1) ),
                                -2.,0.); gcs.append(param)

        func = ROOT.RooExponential(ename, ename, recoMassVar, param); gcs.append(func)
        
        exps.add(func);

    # build the sum of exponentials
    return ROOT.RooAddPdf(prefix, prefix, exps, fracs, True)

#----------------------------------------------------------------------

def makePowerLaw(recoMassVar, prefix, order):
    # corresponds to getPowerLawSingle(..) in PdfModelBuilder.cc

    if order % 2==0:
        raise Exception("only an odd number of parameters is allowed for poewr law functions")

    nfracs = (order - 1) / 2
    npows  = order - nfracs
    assert nfracs == npows - 1
    
    fracs = ROOT.RooArgList()
    pows  = ROOT.RooArgList()

    for i in range(1, nfracs + 1):
        name =  "%s_f%d" % (prefix,i);
        param = ROOT.RooRealVar(name, name,
                                0.9 - float(i-1) * 1./ nfracs,
                                0.,1.); gcs.append(param)
        fracs.add(param)

    # RooPower is a CMSSW class, not in RooFit
    ROOT.gSystem.Load("$CMSSW_BASE/lib/$SCRAM_ARCH/libHiggsAnalysisCombinedLimit.so")
    
    for i in range(1, npows + 1):

        name  = "%s_p%d" % (prefix, i)
        ename = "%s_e%d" % (prefix, i)

        param = ROOT.RooRealVar(name, name,
                                max(-10., -1.0*(i+1) ), # initial value
                                # may work better but does it affect
                                # the generation of toys ?
                                # TMath::Max(-10.,-0.1*(i+1)), // initial value

                                -10.,0. # range
                                ); gcs.append(param)

        func = ROOT.RooPower(ename, ename, recoMassVar, param)
        gcs.append(func)
        pows.add(func);


    return ROOT.RooAddPdf(prefix, prefix, pows, fracs, True)

#----------------------------------------------------------------------

def addBackgroundFunction(ws, recoMassVar, cat, bgfuncName, pdfName = None):

    if pdfName == None:
        # not specified, create our own
        pdfName = "_".join(
            ["bgfunc",
             bgfuncName,
             cat])

    # determine the type
    mo = re.match("(\S+)(\d+)$", bgfuncName)
    assert mo, "bad format for background name: '%s'" % bgfuncName
    name, order = mo.groups()
    order = int(order)

    # important: choose the same ranges for the parameters as we
    #            did in the bias study (see PdfModelBuilder.cc)

    if name == 'pol':
        # Bernstein polynomials
        bgfunc = makeBernstein(recoMassVar, pdfName, order)

    elif name == 'exp':
        # exponenial function
        bgfunc = makeExponential(recoMassVar, pdfName, order)

    elif name == 'pow':
        # power law
        # note that we use RooPower, a class which is
        # part of CMSSW, not RooFit
        bgfunc = makePowerLaw(recoMassVar, pdfName, order)
        
    else:
        raise Exception("unsupported background function type '%s'" % name)

    gcs.append(bgfunc)
    # do NOT import the pdf here before fitting (otherwise we'll
    # get the initial values)

    return bgfunc

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
from optparse import OptionParser
parser = OptionParser("""

  usage: %prog [options] param_file input_file output_file

  program for creating and fitting the background functions

"""
)

parser.add_option("--cat",
                  dest = "cats",
                  type = str,
                  default = None,
                  help="comma separated list of category names (default is to use all found in the workspace)",
                  )

(options, ARGV) = parser.parse_args()

if options.cats != None:
    options.cats = options.cats.split(',')

if len(ARGV) != 3:
    parser.print_help();
    sys.exit(1)

paramFname, inputFname, outputFname = ARGV

#----------------------------------------

# assume this is the name of a fit parameter settings file in python format
import imp
parametersModule = imp.load_source('parameters', paramFname)

bgfuncs = parametersModule.bgfuncs

#----------------------------------------

import ROOT; gcs = []
ROOT.gROOT.SetBatch(1)


fin = ROOT.TFile(inputFname)
assert fin.IsOpen(), "could not open input workspace file " + inputFname

ws = fin.Get(wsname)

assert ws != None, "could not find workspace '%s' in file '%s'" % (wsname, inputFname)

# reconstructed mass variable
recoMassVar = utils.getObj(ws, massVarName)


# get the list of all categories
if options.cats == None:
    allCats   = utils.getCatEntries(utils.getObj(ws, 'allCategories'))
else:
    allCats = options.cats

allMasses = [ int(x) for x in utils.getCatEntries(utils.getObj(ws, 'allSigMasses')) ]

# this can be used for combine to let the background parameters
# float while keeping other nuisances fixed
bgParamsSet = ROOT.RooArgSet(); gcs.append(bgParamsSet)


#----------
for cat in allCats:

    # create the function
    bgpdf = addBackgroundFunction(ws, recoMassVar, cat, bgfuncs[cat], "pdf_bkg_" + cat)

    pdfname = bgpdf.GetName()

    # create the normalization function
    ds = utils.getObj(ws, "data_%s" % cat)
    numEvents = ds.sumEntries()
    normFunc = ROOT.RooRealVar(pdfname + "_norm", pdfname + "_norm",
                               numEvents,
                               0,
                               10 * numEvents); gcs.append(normFunc)

    # fit to the data (does combine refit this anyway ?)
    extPdf = ROOT.RooExtendPdf(pdfname + "_ext", pdfname + "_ext",
                               bgpdf,
                               normFunc)
    extPdf.fitTo(ds,
                 ROOT.RooFit.Minimizer("Minuit2"),
                 )

    # import these AFTER fitting
    getattr(ws, 'import')(bgpdf, ROOT.RooFit.RecycleConflictNodes())
    getattr(ws, 'import')(normFunc, ROOT.RooFit.RecycleConflictNodes())

    # add the parameters of the background functions to the corresponding set
    # note that this does NOT depend on the Higgs mass hypothesis variable MH
    # but we have to exclude the reconstructed mass variable 'CMS_emu_mass'
    for leaf in utils.getLeafNodes(bgpdf):
        if leaf.GetName() == massVarName:
            continue

        bgParamsSet.add(leaf)

    # also add the normalization variable
    bgParamsSet.add(normFunc)



# end of loop over categories

# import that set of background parameters to the workspace
ws.defineSet("group_bgparams", bgParamsSet)
                             
# write the fitted workspace out
ws.writeToFile(outputFname)

