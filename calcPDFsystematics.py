#!/usr/bin/env python

# calculates the impact of varying the PDFs for the signal
import sys, re, os
import utils
from pprint import pprint
import math

#----------------------------------------------------------------------
wsname = "CMS_emu_workspace"

# determine the systematics at one mass point only
mass = 125

#----------------------------------------------------------------------

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------

ARGV = sys.argv[1:]

workspaceDir, = ARGV

# maps from 'suffix' to actual file
fileMap = {}

# find the workspace files
import glob
for fname in glob.glob(workspaceDir + "/workspace-*.root"):

    basename = os.path.basename(fname)
    print basename
    mo = re.match("workspace-(central|up\d+|down\d+)\.root$", basename)
    if not mo:
        continue

    suffix = mo.group(1)
    fileMap[suffix] = fname

# get the number of signal events

# first index is the PDF shift (e.g. 'nominal', 'down01' etc.)
# second index is the category
# third index is the signal process
# value is the number of expected signal events

numSigEvents = {}

allCats = None
allProcs = None

# allCats = [ 'cat0' ]
# allProcs = [ 'ggh' ]

for typename, fname in fileMap.items():
    import ROOT
    fin = ROOT.TFile(fname)
    assert fin.IsOpen(), "could not open file " + fname

    ws = fin.Get(wsname)
    assert ws != None, "could not find workspace " + wsname

    # get list of categories from the first file
    if allCats == None:
        allCats   = utils.getCatEntries(utils.getObj(ws, 'allCategories'))
        allProcs  = utils.getCatEntries(utils.getObj(ws, 'allSigProcesses'))

    for cat in allCats:
        for proc in allProcs:

            # e.g. sig_Hem_unbinned_vbf_120_cat3
            name = "_".join([
                "sig",
                "Hem",
                "unbinned",
                proc,
                str(mass),
                cat
                ])

            # binned dataset
            # e.g. sig_Hem_vbf_115_cat10
            name = "_".join([
                "sig",
                "Hem",
                proc,
                str(mass),
                cat
                ])

            # get the signal MC dataset
            ds = utils.getObj(ws, name)

            numSigEvents.setdefault(typename, {}).setdefault(cat,{})[proc] = ds.sumEntries()

        # end of loop over signal processes
    # end of loop over categories
# end of loop over files

#----------------------------------------

# pprint(numSigEvents); sys.exit(1)

pdfs = numSigEvents.keys()
pdfs.remove('central')
pdfs.sort()

# assert len(pdfs) == 2

pdfNums = set()
for pdf in pdfs:
    mo = re.match("(up|down)(\d+)$", pdf)
    assert mo
    # we keep this as an integer on purpose
    pdfNums.add(mo.group(2))


pdfNums = sorted(pdfNums)
print "found",pdfNums,"pdf directions"

# first index is category
# second index is signal process
# third index is the pdf number
relDeviations = {}

for proc in allProcs:
    for cat in allCats:

        nom = numSigEvents['central'][cat][proc]

        sumSqRel = 0

        for pdfNum in pdfNums:
            up = numSigEvents['up' + pdfNum][cat][proc]
            down = numSigEvents['down' + pdfNum][cat][proc]

            # check that up and down are on opposite sides of nominal

            if not ((up >= nom and nom >= down) or (up <= nom and nom <= down)):
                print "WARNING: up/down are NOT on opposite sides of nominal for",cat,proc,": up=",up,"nom=",nom,"down=",down

                # take the maximum deviation as uncertainty, with the sign determined by the larger deviation
                relup = (up - nom) / nom
                reldown = (nom - down) / nom

                if abs(relup) > abs(reldown):
                    rel = relup
                else:
                    rel = reldown
            else:
                # deviations are on both sides
                # take (up - down) / (2 * nominal)
                rel = (up - down) / (2.0 * nom)

            sumSqRel += rel * rel

            relDeviations.setdefault(cat,{}).setdefault(proc,{})[pdfNum] = rel

        # end of loop over pdf numbers

pprint(relDeviations);# sys.exit(1)


print "         "," ".join([ " %5s" % cat for cat in allCats])
for proc in allProcs:
    print "%-3s" % proc

    sums = [ 0] * len(allCats)

    for pdfNum in pdfNums:
        parts = [ "%+5.1f%%" % (relDeviations[cat][proc][pdfNum] * 100) for cat in allCats ]

        sums = [ x + relDeviations[cat][proc][pdfNum]**2 for cat,x in zip(allCats,sums) ]

        print "       %02s" % pdfNum," ".join(parts)

    # print the quadratic sum:
    sums = [ math.sqrt(x) for x in sums ]
    
    parts = [ "%5.1f%%" % (x * 100) for x in sums ]
    
    print "      %03s" % "sum"," ".join(parts)        
