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

    # for the moment, we just take the pdf weights into account,
    # no correlation with the PU reweighting

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
            weight = chain.weight * chain.pdf_weights[j] / chain.pdf_weights[0]

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
    print getSumOfWeightsGlobeTuples('vbf')
    sys.exit(1)
else:
    # note that this is independent of (selection) categories
    sumWeightsGlobeTuples = {
        "ggh": [8940.0, 8943.884810978698, 8936.292024288045, 8954.593220015773, 8924.92045992629, 9113.264990274265, 8789.622200304719, 9010.308576524212, 8866.754612266284, 8975.67990133543, 8893.100957959225, 8940.533446594585, 8939.622884233233, 8892.815828767913, 9016.3078201992, 8907.895448598692, 8969.124499671834, 8804.293323728589, 9018.592255493855, 8888.868975301317, 8965.245432264317, 8985.12670699006, 8908.074636895766, 9053.297119203167, 8810.743222430172, 8936.299276944703, 8947.456118143748, 8957.341330116633, 8926.279924470186, 8904.740204992102, 8966.620371235364, 8979.513643512733, 8903.893581600572, 8950.330213547804, 8904.649073784145, 8953.70041221985, 8970.143280314529, 8943.928553945723, 8935.35482758048, 8951.043335216957, 8954.3080061586, 8975.065811892317, 8907.924498308785, 8954.054415081668, 8924.618491102054, 8905.542360743299, 8989.298167305393, 8982.517638792357, 8833.884406491929, 8938.819723170933, 8910.219065206968, 8977.421467674338, 8812.30525327015, 8972.114105845341, 8987.874955481213, 8959.152969245308, 8981.598437051509, 8961.568537243638, 8982.584289940974, 8956.627094822436, 8980.163527574237, 8966.726023599456, 8955.091918403865, 8996.370065103674, 8874.940612439448, 9032.4683852144, 8997.706872643676, 8937.258608579757, 8938.389476053728, 8984.43924671866, 8956.20318175159, 8965.181915328996, 8964.318847163284, 8979.279941736071, 8998.998443008415, 8921.11147658558, 8958.869430100334, 8980.005412340772, 8971.122886331374, 8971.878821780594, 8969.464777134375, 8987.497748932114, 8928.930060236704, 9053.36822082138, 8967.913101367865, 8973.78412256078, 8983.861015023786, 8965.329627888574, 8966.92559064389, 8973.995818930518, 9010.630319841206, 8894.642188943713, 8961.268262481113, 8975.122493538249, 9024.142676567253, 9318.757374274037, 8961.959542495842, 9191.60182735616, 9218.220466550916, 8957.084335431875, 9598.982175428298, 8966.302338460697, 9096.205215968792, 8956.404070247983, 8637.393838798987, 8945.17900015355, 8697.743185226844, 9069.719773331504, 8594.95927593249, 9037.735783877972, 9104.098748416478, 9007.562552848733, 9024.339597105747, 9337.226862040725, 9072.853856712567, 8947.6750126348, 9087.015716731099, 9179.806879094667, 9666.133534211705, 8961.43944207641, 8929.315381177215, 9125.401048199976, 9028.00958345184, 9250.317756192955, 9170.510629920165, 9073.271481728329, 9443.849202195272, 9207.61746400935, 8676.00779781197, 8986.07957631551, 9082.80069516253, 8914.75269238641, 9029.593347679645, 9413.687107332169, 9352.347074466285, 9007.169451416215, 9362.66185697199, 9027.556640216633, 9284.412108873317, 8833.761244108202, 9090.0952657473, 9420.293385312141, 8947.180498559763, 9193.06325646476, 9154.376263248805, 8903.61040926295, 9059.856741576396, 9128.776066653027, 9305.7804542371, 9185.546688021535, 8956.794257037829, 8765.515384241926, 8685.702963193895, 8688.252955836058, 9012.779553869743, 9091.105172504016, 9105.608816396685, 9236.123476045803, 8936.167860278088, 9105.29285276324, 9157.792154383365, 9006.112071459642, 8940.218466493741, 9083.517548192347, 8768.413969951605, 9058.30026331609, 9224.818062759921, 8828.275495865531, 8837.909594154491, 9363.614034109802, 8899.30091239345, 9115.55884507721, 8903.16280303841, 8876.218142387108, 8989.068100158825, 8206.385850249155, 8543.564271125982, 9173.956641130902, 8700.359273009313, 8726.718772705543, 8986.325299456887, 9031.284102836888, 8404.621964424574, 8660.220287705324, 9015.462724513629, 8939.940357198873, 8831.722270573859, 9314.723441462163, 9149.806375341632, 9293.768459174897, 8553.0008814063, 8816.18878642626, 9279.709190989708, 9037.972307090604, 8935.948982654001],
        'vbf': [9689.0, 9664.124548826496, 9711.396033891158, 9701.501136339632, 9675.781925047448, 9464.46694294553, 9886.091433045447, 9580.615703834434, 9778.172173550738, 9650.641053631987, 9738.705521838507, 9700.051387935619, 9682.355091362393, 9657.244326443226, 9733.69196524959, 9752.850849276632, 9628.960245001917, 9822.666199542668, 9615.474191103218, 9793.833530325377, 9636.358916767002, 9709.859360716184, 9666.763359554976, 9712.269830493218, 9683.107895459521, 9698.931061756793, 9666.007732496508, 9713.72400752326, 9668.687603338443, 9726.401625266153, 9660.101126676665, 9688.709851631314, 9688.673473889034, 9685.803606264346, 9692.178377850052, 9695.417000933983, 9696.313986191912, 9679.357133164769, 9694.342838480788, 9701.601502506433, 9691.32995004564, 9651.586528679223, 9699.397008287482, 9656.969986928194, 9719.818371305859, 9705.571106096097, 9644.94431928618, 9718.677510537647, 9673.490390733012, 9662.817760217818, 9627.469262030845, 9688.991497431609, 9643.125193056185, 9618.29218005718, 9634.652305545747, 9604.839138155636, 9619.536474983002, 9616.763928676613, 9609.295766688343, 9631.586334564352, 9611.550719925619, 9622.83783186718, 9637.31895797894, 9591.241383922406, 9757.195046767662, 9533.309561567476, 9582.58949887981, 9666.972104694027, 9654.838859787307, 9604.903657935181, 9627.32871266489, 9601.818665552413, 9626.898557347744, 9607.356769584563, 9532.932044717807, 9777.57192887533, 9667.165066882177, 9588.597055680828, 9630.9953964009, 9612.956456796377, 9618.933476283932, 9580.604821157638, 9653.239192229565, 9532.04916792691, 9625.956049081235, 9615.189809683201, 9599.354231229288, 9628.829709166994, 9605.84863437913, 9624.283183356396, 9609.796584548112, 9624.140772960342, 9622.38576877645, 9615.110544563167, 9556.311932531069, 9628.701121061511, 9651.067693169252, 9331.365137743776, 9544.860037951898, 9646.107543163493, 9060.221796870594, 9562.31109023956, 9544.878204379045, 9745.345590650999, 9944.4870307127, 9650.914290695231, 9914.27717057272, 9713.72650655411, 9816.0579248213, 9638.329745838435, 9704.014630736501, 9327.963915343693, 9645.046262248952, 9380.324852443397, 9422.889703206045, 9606.060336990282, 9602.25494854504, 9581.879216440733, 9303.317421892829, 9692.75331022505, 9588.374758801585, 9325.192202731896, 9484.240183233764, 9294.155292943971, 9275.664891375056, 9653.534421059672, 9312.88082748614, 9317.081818708315, 9893.260133330668, 9624.00943232219, 9391.655987886023, 9672.444529086899, 9269.148706930975, 9470.370154933566, 9254.31719802595, 9521.640897828642, 9333.882498460182, 9798.804715846534, 9089.884199546927, 9911.171267570408, 9558.42512073583, 9325.255359874573, 9432.258769387545, 9366.841710573346, 9606.597614357011, 9771.747330771805, 9405.953395106568, 9270.02404662083, 9402.227703786097, 9503.058538523821, 9800.961262456287, 9454.204555528624, 9837.48257284676, 9934.2407678224, 9462.787831754717, 9672.0676220112, 9449.679765694389, 9328.64399374765, 9299.179245948748, 9273.626552708316, 9537.830561136927, 9473.108524086656, 9510.194925607388, 9491.260106642856, 9629.35318285833, 9701.126803402465, 9487.145537356546, 9689.763194070203, 9584.36749140803, 9390.477698239783, 9659.172843741744, 9525.887895644912, 9628.551342711928, 9665.54016778345, 9198.246104381202, 10391.171179668625, 9920.501847065218, 9596.465118527149, 9817.172343684857, 9825.354793178612, 10066.269824173653, 9471.030662500416, 9174.974861412386, 9726.957761298285, 9539.978585119765, 9331.658918017241, 9572.434796747864, 9338.803543852502, 9292.130598197447, 9521.488736779038, 9850.665844469242, 9763.240430821283, 9622.688969336448, 9450.689381076732, 9650.753753114628],
        }

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

firstNumEventsColumn = 5

for procIndex, proc in enumerate(allProcs):

    row = 1
    ws.cell(
        row = row + (4 + numPDFs) * procIndex,
        column = firstNumEventsColumn,
        value = proc)

    for catIndex, cat in enumerate(allCats):
        # row = 2 + (4 + numPDFs) * procIndex
        row = 2 + (4 + numPDFs + 3 * numPDFfamilies) * procIndex

        # normal observable
        ws.cell(
            row = row,
            column = firstNumEventsColumn + catIndex,
            value = cat)

        # delta+ / delta- columns
        col = firstNumEventsColumn + numCats + 1 + 2 * catIndex

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
                column = firstNumEventsColumn + catIndex,
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
                    col = firstNumEventsColumn + numCats + 1 + 2 * catIndex

                    origCol = openpyxl.cell.get_column_letter(firstNumEventsColumn + catIndex)

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

                    col = firstNumEventsColumn + numCats + 1 + 2 * catIndex

                    origCol = openpyxl.cell.get_column_letter(firstNumEventsColumn + catIndex)

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
                    col = firstNumEventsColumn + numCats + 1 + 2 * catIndex

                    colName = openpyxl.cell.get_column_letter(firstNumEventsColumn + catIndex)

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
        column = firstNumEventsColumn + catIndex

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
