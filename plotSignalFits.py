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

htmlOutputFname = "plots.html"

#----------------------------------------------------------------------

def canvasToDataURIString(canv):

    import tempfile
    fout = tempfile.NamedTemporaryFile(suffix = ".png")

    canv.SaveAs(fout.name)

    fin = open(fout.name)
    data = fin.read()
    fin.close()

    fout.close()

    return "data:image/png;base64," + data.encode('base64').replace('\n','')

#----------------------------------------------------------------------

def plotSignalFitsVsMC(ws, recoMassVar, cat, proc, htmlout):

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

    if htmlout != None:
        print >> htmlout, '<img src="%s" />' % canvasToDataURIString(ROOT.gPad)

#----------------------------------------------------------------------

def plotParameterEvolution(ws, mhypVar, cat, proc, minMass, maxMass, htmlout):

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

            func.plotOn(frame,
                        # commented out since some normalization
                        # seems to be applied by RooFit when giving a range
                        # (which does not make sense since this is a function,
                        # not a PDF)
                        # ROOT.RooFit.Range(minMass, maxMass)
                        )

        # end of loop over Gaussian components
        frame.Draw()

        if htmlout != None:
            print >> htmlout, '<img src="%s" />' % canvasToDataURIString(ROOT.gPad)

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

    func.plotOn(frame,
                # disabled (see above)
                # ROOT.RooFit.Range(minMass, maxMass)
                )
    frame.Draw()

    if htmlout != None:
        print >> htmlout, '<img src="%s" />' % canvasToDataURIString(ROOT.gPad)

#----------------------------------------------------------------------

def plotInterpolatedPdf(ws, mhypVar, recoMassVar, cat, proc, minMass, maxMass, htmlout):

    numPoints = 21

    import numpy
    massValues = numpy.linspace(minMass,
                                maxMass,

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

    if htmlout != None:
        print >> htmlout, '<img src="%s" />' % canvasToDataURIString(ROOT.gPad)

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------
ARGV = sys.argv[1:]

assert len(ARGV) == 1

inputFname = ARGV.pop(0)

import ROOT 
ROOT.gROOT.SetBatch(True)

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

# allCats = [ 'cat0'] ; allProcs = [ 'ggh' ]

import cStringIO as StringIO
htmlout = StringIO.StringIO()

print >> htmlout, "<html>"
print >> htmlout, "<head>"
print >> htmlout, "<title>signal model plots for %s</title>" % inputFname
print >> htmlout, "</head>"

print >> htmlout, "<body>"

print >> htmlout, "<h1>signal model plots for %s</h1><br/>" % inputFname

# table with number of signal events expected and number of MC
# events with links to plots

print >> htmlout, '<table border="1"><tbody>'

print >> htmlout, "<tr>"
print >> htmlout, "<th>category</th>"
print >> htmlout, "<th>mass</th>"

for proc in allProcs:
    print >> htmlout, "<th>expected events %s</th>" % proc
    print >> htmlout, "<th>MC events %s</th>" % proc
    print >> htmlout, "<th>plots</th>"

print >> htmlout, "</tr>"

for cat in allCats:

    for massIndex, mass in enumerate(allMasses):

        print >> htmlout,"<tr>"

        if massIndex == 0:
            print >> htmlout,'<td rowspan="%d">%s</td>' % (len(allMasses), cat)
            
        print >> htmlout,"<td>%d</td>" % mass

        for proc in allProcs:

            dataset = utils.getObj(ws, "sig_Hem_unbinned_%s_%d_%s" % (proc, mass, cat))

            #----------
            # number of expected events
            #----------

            print >> htmlout, "<td>%.1f</td>" % dataset.sumEntries()

            #----------
            # number of MC events
            #----------

            print >> htmlout, "<td>%d</td>" % dataset.numEntries()

            #----------
            # link to plots
            #----------
            if massIndex == 0:
                print >> htmlout, '<td rowspan="%d"><a href="#%s_%s">plots</a></td>' %  (len(allMasses), cat, proc)

        # end of loop over processes

        print >> htmlout,"</tr>"

    # end of loop over masses
        
print >> htmlout, "</tbody></table>"

print >> htmlout, "<hr/>"

#----------

minMassForPlots = min(allMasses)
maxMassForPlots = max(allMasses)

for cat in allCats:

    print >> htmlout, "<h2>%s</h2><br/>" % cat

    for proc in allProcs:

        # anchor
        print >> htmlout,'<a name="%s_%s" />' % (cat, proc)

        # title
        print >> htmlout,"<h3>%s / %s</h3><br/>" % (cat, proc)

        #----------
        # plot signal fit vs. MC sample (signal)
        #----------
        plotSignalFitsVsMC(ws, recoMassVar, cat, proc, htmlout)

        #----------
        # draw evolution of interpolated parameters vs. mass hypothesis
        #----------
        plotParameterEvolution(ws, mhypVar, cat, proc, minMassForPlots, maxMassForPlots, htmlout)

        #----------
        # plot the interpolated signal PDFs at more values of mhyp
        #----------
        plotInterpolatedPdf(ws, mhypVar, recoMassVar, cat, proc, minMassForPlots, maxMassForPlots, htmlout)

        print >> htmlout, "<hr/><br/>"

    # end of loop over processes
# end of loop over categories

# saveAllCanvases()
# print "saveAllCanvases()"

print >> htmlout, "</body>"
print >> htmlout, "</html>"

# write the html output
fout = open(htmlOutputFname,"w")
fout.write(htmlout.getvalue())
fout.close()

print "wrote plots to",htmlOutputFname
