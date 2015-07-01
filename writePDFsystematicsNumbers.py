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

# whether or not to normalize the relative deviations
# such that the total number of expected
# events stays the same. This should be done if one
# includes pdf uncertainties on the cross sections
# in addition in combine, otherwise the
# pdf (normalization) uncertainty is double counted
averageDeviations = True


pdfMembers = [
    ('CT10',            53),
    ('MSTW2008nlo68cl', 41),
    ('NNPDF10_100',    101),
    ]

pdfsWithUpDown = ('CT10', 'MSTW2008nlo68cl')

numPDFs = sum([ line[1] for line in pdfMembers ])
numPDFfamilies = len(pdfMembers)

allCats  = None
allProcs = None

# allCats = [ 'cat0' ]
# allProcs = [ 'ggh' ]

#----------------------------------------------------------------------

def getSumOfWeightsGlobeTuples(proc):
    filePattern = "/home/users/aholz/hadoop/2013-07-hemu/00-crab-globe/sig-with-pdfweights/" + proc + "/125.0/*.root"

    raise Exception("MUST REVIEW THIS")

    import ROOT
    chain = ROOT.TChain("event")
    chain.Add(filePattern)
    
    # get sum of event weights

    retval = [ 0. ] * numPDFs

    numEvents = chain.GetEntries()
    for i in range(numEvents):
        chain.GetEntry(i)

        # get event weight for each pdf
        for j in range(numPDFs):
            weight = chain.event.weight * chain.event.pdf_weights[j] / chain.event.pdf_weights[0]

            retval[j] += weight

    return retval

#----------------------------------------------------------------------

def getSumOfWeightsWorkspace(fname):

    retval = {}

    import ROOT
    fin = ROOT.TFile(fname)
    assert fin.IsOpen(), "could not open file " + fname

    ws = fin.Get(wsname)
    assert ws != None, "could not find workspace " + wsname

    # get list of categories from the first file

    global allCats, allProcs

    if allCats == None:
        allCats   = utils.getCatEntries(utils.getObj(ws, 'allCategories'))

    if allProcs == None:
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

            retval.setdefault(cat,{})[proc] = ds.sumEntries()

        # end of loop over signal processes
    # end of loop over categories
    
    return retval

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------

if False:
    print getSumOfWeightsGlobeTuples('ggh')
    sys.exit(1)


ARGV = sys.argv[1:]

workspaceDir, = ARGV
#----------------------------------------

# expanded pdf information
pdfInfo = []
# theSum = 0

for pdfFamilyIndex, line in enumerate(pdfMembers):
    for i in range(line[1]):
        pdfInfo.append([ line[0], i, pdfFamilyIndex])

    # theSum += line[1]
    

numSigEventsAfterSelection = {}

# find the workspace files
import glob
for fname in glob.glob(workspaceDir + "/workspace-*.root"):

    basename = os.path.basename(fname)
    print basename
    mo = re.match("workspace-(\d+).root$", basename)
    assert mo

    pdfIndex = int(mo.group(1), 10)

    numSigEventsAfterSelection[pdfIndex] = getSumOfWeightsWorkspace(fname)

# end of loop over files

# pprint(numSigEventsAfterSelection)

#----------
# write this to a spreadsheet
#----------
import openpyxl

wb = openpyxl.Workbook()
ws = wb.active

allCats = list(numSigEventsAfterSelection[0].keys())
allCats.sort(key = lambda cat: int(re.match('cat(\d+)$', cat).group(1)))

allProcs = [ 'ggh', 'vbf' ]

numCats = len(allCats)

ws.cell(column = 1, row = 1, value = 'global pdfIndex')
ws.cell(column = 2, row = 1, value = 'pdf family')
ws.cell(column = 3, row = 1, value = 'in-family index')

for procIndex, proc in enumerate(allProcs):

    row = 1
    ws.cell(
        row = row + (4 + numPDFs) * procIndex,
        column = 5,
        value = proc)

    for catIndex, cat in enumerate(allCats):
        # row = 2 + (4 + numPDFs) * procIndex
        row = 2 + (4 + numPDFs + 3 * numPDFfamilies) * procIndex

        # normal observable
        ws.cell(
            row = row,
            column = 5 + catIndex,
            value = cat)

        # delta+ / delta- columns
        col = 5 + numCats + 1 + 2 * catIndex

        ws.cell(
            row = row,
            column = col,
            value = cat)

        for deltaIndex, deltaName in enumerate(['+', '-']):
            ws.cell(
                row = row + 1,
                column = col + deltaIndex,
                value = 'delta' + deltaName)


for procIndex, proc in enumerate(allProcs):

    # names of cells over which the maximum should be taken
    # (per category)
    #
    # first index is category name
    cellsForMax = {}

    for pdfIndex in sorted(numSigEventsAfterSelection):

        pdfFamily = pdfInfo[pdfIndex][0]
        inFamilyIndex = pdfInfo[pdfIndex][1]
        pdfFamilyIndex = pdfInfo[pdfIndex][2]

        row = 4 + pdfIndex + (4 + numPDFs + 3 * numPDFfamilies) * procIndex + 3 * pdfFamilyIndex

        ws.cell(column = 1, row = row, value = pdfIndex)

        if inFamilyIndex == 0:
            nominalPdfRow = row

        ws.cell(column = 2, row = row, value = pdfFamily)
        ws.cell(column = 3, row = row, value = inFamilyIndex)

        for catIndex, cat in enumerate(allCats):
            ws.cell(
                column = 5 + catIndex,
                row = row,
                value = numSigEventsAfterSelection[pdfIndex][cat][proc])

        #----------
        # delta columns
        #----------
        
        # find the number of pdfs in this family
        familySize = [ line[1] for line in pdfMembers if line[0] == pdfFamily]
        assert len(familySize) == 1
        familySize = familySize[0]

        #----------
        
        if pdfFamily in pdfsWithUpDown:
            if inFamilyIndex == 0:

                # add the sqrt(sumsq(..)) cells
                for catIndex, cat in enumerate(allCats):
                    col = 5 + numCats + 1 + 2 * catIndex

                    origCol = openpyxl.cell.get_column_letter(5 + catIndex)

                    for plusMinusIndex in range(2):
                        colName = openpyxl.cell.get_column_letter(col + plusMinusIndex)

                        cell = ws.cell(row = row + familySize + 1,
                                       column = col + plusMinusIndex,
                                       value = '=SQRT(SUMSQ(%s%d:%s%d)) / %s%d' % (colName, row,
                                                                                   colName, row + familySize - 1,
                                                                                   origCol, row)
                                       )

                        cell.number_format = '0.00%'

                        cellsForMax.setdefault(cat,[]).append(cell)

                        ## cell = ws.cell(row = row + familySize + 1,
                        ##                column = col + plusMinusIndex,
                        ##                value = '=SQRT(SUMSQ(%s%d:%s%d))' % (colName, row,
                        ##                                                            colName, row + familySize - 1,
                        ##                                                            )
                        ##                )

            if inFamilyIndex > 0 and inFamilyIndex % 2 == 0:

                for catIndex, cat in enumerate(allCats):

                    col = 5 + numCats + 1 + 2 * catIndex

                    origCol = openpyxl.cell.get_column_letter(5 + catIndex)

                    ws.cell(
                        column = col,
                        row = row,
                        value = '=MAX(%s%d - %s$%d, %s%d - %s$%d, 0)' % (origCol, row - 1,
                                                                         origCol, nominalPdfRow,
                                                                         origCol, row,
                                                                         origCol, nominalPdfRow)
                        )

                    

                    ws.cell(
                        column = col + 1,
                        row = row,
                        value = '=MAX(%s$%d - %s%d, %s$%d - %s%d, 0)' % (origCol, nominalPdfRow,
                                                                         origCol, row - 1,
                                                                         origCol, nominalPdfRow,
                                                                         origCol, row)
                        )

        else:
            # this is NOT a PDF with up/down
            # we take the rms
            # also add a row with the average of our observable
            # (as opposed of the observable of the average)

            if inFamilyIndex == 0:

                # add the stdev(..) cells
                for catIndex, cat in enumerate(allCats):
                    col = 5 + numCats + 1 + 2 * catIndex

                    colName = openpyxl.cell.get_column_letter(5 + catIndex)

                    # the range over which we take the average and stddev.
                    rangeDesc = "%s%d:%s%d" % (colName, row + 1, # do not include nominal row
                                               colName, row + familySize - 1)

                    cell = ws.cell(row = row + familySize + 1,
                            column = col,
                            value = '=STDEV(%s) / AVERAGE(%s)'  % (rangeDesc, rangeDesc)
                            )

                    cell.number_format = '0.00%'
                    cellsForMax.setdefault(cat,[]).append(cell)

            else:
                pass
                # for catIndex, cat in enumerate(allCats):
                # 
                #     col = 5 + numCats + 1 + 2 * catIndex
                # 
                #     origCol = openpyxl.cell.get_column_letter(5 + catIndex)
                # 
                #     ws.cell(
                #         column = col,
                #         row = row,
                #         value = '=(%s%d - %s$%d, %s%d - %s$%d, 0)' % (origCol, row - 1,
                #                                                          origCol, nominalPdfRow,
                #                                                          origCol, row,
                #                                                          origCol, nominalPdfRow)
                #         )
                
    # end of loop over PDFs

    # put the cells for the maximum over all PDF families

    # row = 4 + (4 + numPDFs + 3 * numPDFfamilies) * len(allProcs)
    row = 4 + numPDFs + (4 + numPDFs + 3 * numPDFfamilies) * procIndex + 3 * (numPDFfamilies - 1) + 2

    ws.cell(row = row,
            column = 3,
            value = "max over all PDF families")

    for catIndex, cat in enumerate(allCats):
        column = 5 + catIndex

        cellNames = [ cell.coordinate for cell in cellsForMax[cat] ]

        cell = ws.cell(row = row,
                       column = column,
                       value = "=MAX(%s)" % ",".join(cellNames)
                       )

        cell.number_format = '0.00%'

# end of loop over processes

wb.save(filename = "pdf-uncert.xlsx")


#----------------------------------------

### # pprint(numSigEvents); sys.exit(1)
### 
### pdfs = numSigEvents.keys()
### pdfs.remove('central')
### pdfs.sort()
### 
### # assert len(pdfs) == 2
### 
### pdfNums = set()
### for pdf in pdfs:
###     mo = re.match("(up|down)(\d+)$", pdf)
###     assert mo
###     # we keep this as an integer on purpose
###     pdfNums.add(mo.group(2))
### 
### 
### pdfNums = sorted(pdfNums)
### print "found",pdfNums,"pdf directions"
### 
### # first index is category
### # second index is signal process
### # third index is the pdf number
### relDeviations = {}
### 
### for proc in allProcs:
### 
###     #----------
###     # calculate sum of events over all categories
###     #----------
### 
###     sumEventsUp = {}
###     sumEventsDown = {}
### 
###     for pdfNum in pdfNums:
###         sumEventsUp[pdfNum]   = sum([numSigEvents['up'   + pdfNum][cat][proc] for cat in allCats])
###         sumEventsDown[pdfNum] = sum([numSigEvents['down' + pdfNum][cat][proc] for cat in allCats])
### 
###     sumEventsCentral = sum([numSigEvents['central'][cat][proc] for cat in allCats])
### 
###     #----------
###     
###     for cat in allCats:
### 
###         nom = numSigEvents['central'][cat][proc]
### 
###         sumSqRel = 0
### 
###         for pdfNum in pdfNums:
###             up = numSigEvents['up' + pdfNum][cat][proc]
###             down = numSigEvents['down' + pdfNum][cat][proc]
### 
###             if averageDeviations:
###                 # take out any average change in normalization
###                 up   *= sumEventsCentral / float(sumEventsUp[pdfNum])
###                 down *= sumEventsCentral / float(sumEventsDown[pdfNum])
### 
###             # check that up and down are on opposite sides of nominal
### 
###             if not ((up >= nom and nom >= down) or (up <= nom and nom <= down)):
###                 print "WARNING: up/down are NOT on opposite sides of nominal for",cat,proc,": up=",up,"nom=",nom,"down=",down
### 
###                 # take the maximum deviation as uncertainty, with the sign determined by the larger deviation
###                 relup = (up - nom) / nom
###                 reldown = (nom - down) / nom
### 
###                 if abs(relup) > abs(reldown):
###                     rel = relup
###                 else:
###                     rel = reldown
###             else:
###                 # deviations are on both sides
###                 # take (up - down) / (2 * nominal)
###                 rel = (up - down) / (2.0 * nom)
### 
###             sumSqRel += rel * rel
### 
###             relDeviations.setdefault(cat,{}).setdefault(proc,{})[pdfNum] = rel
### 
###         # end of loop over pdf numbers
### 
### pprint(relDeviations);# sys.exit(1)
### 
### 
### print "         "," ".join([ " %5s" % cat for cat in allCats])
### for proc in allProcs:
###     print "%-3s" % proc
### 
###     sums = [ 0] * len(allCats)
### 
###     for pdfNum in pdfNums:
###         parts = [ "%+5.1f%%" % (relDeviations[cat][proc][pdfNum] * 100) for cat in allCats ]
### 
###         sums = [ x + relDeviations[cat][proc][pdfNum]**2 for cat,x in zip(allCats,sums) ]
### 
###         print "       %02s" % pdfNum," ".join(parts)
### 
###     # print the quadratic sum:
###     sums = [ math.sqrt(x) for x in sums ]
###     
###     parts = [ "%5.1f%%" % (x * 100) for x in sums ]
###     
###     print "      %03s" % "sum"," ".join(parts)        
