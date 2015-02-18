#!/usr/bin/env python
import utils

#----------------------------------------------------------------------
wsname = "CMS_emu_workspace"

#----------------------------------------------------------------------

def readNumbersFromWorkspace(inputFname, wsname = wsname, mass = 125):
    # returns a dict with first index = category name,
    # second index is process type

    import ROOT

    fin = ROOT.TFile(inputFname)
    assert fin.IsOpen(), "could not open input workspace file " + inputFname

    ws = fin.Get(wsname)
    assert ws != None, "could not find workspace '%s' in file '%s'" % (wsname, inputFname)

    # get the list of all categories
    allCats   = utils.getCatEntries(utils.getObj(ws, 'allCategories'))
    allProcs  = utils.getCatEntries(utils.getObj(ws, 'allSigProcesses'))

    retval = {}

    for cat in allCats:
        thisData = {}
        retval[cat] = thisData

        for sigProc in allProcs:
            ds = utils.getObj(ws,
                              "_".join([
                                        "sig",
                                        "Hem",
                                        "unbinned",
                                        sigProc,
                                        str(mass),
                                        cat]))
            thisData[sigProc] = ds.sumEntries()

        # background
        ds = utils.getObj(ws, "_".join([
                                        "bkg",
                                        cat]))
        thisData['bkg'] = ds.sumEntries()

        # data
        ds = utils.getObj(ws, "_".join([
                                        "data",
                                        cat]))
        thisData['data'] = ds.sumEntries()
    # end of loop over categories
    return allCats, retval

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------

from optparse import OptionParser
parser = OptionParser("""

  usage: %prog [options] workspace.root

  produces datacards for a counting experiment combine from the number of events
  in the given workspace file

  run like

     %prog > datacards.txt

  then run

     combine datacards.txt -M Asymptotic --run expected

"""
)


### parser.add_option("--numcats",
###                   default = 3,
###                   type=int,
###                   help="number of categories",
###                   )

### parser.add_option("--acp",
###                   default = False,
###                   action = "store_true",
###                   help="use acp objects in the workspace instead of charge blind ones",
###                   )


(options, ARGV) = parser.parse_args()

assert len(ARGV) == 1, "must specify exactly one non-option argument: the workspace file"

#----------------------------------------

allCats, numEvents = readNumbersFromWorkspace(ARGV[0])



print "#"
print "#"
print "----------------------------------------"
print "imax *"
print "jmax *"
print "kmax *"
print "----------------------------------------"


    
print "---------------------------------------------"

print "bin           "," ".join(allCats)
print "observation   "," ".join(str(numEvents[cat]['data']) for cat in allCats)

print "---------------------------------------------"

lineBin = [ "bin" ]
lineProcess1 = [ "process" ]
lineProcess2 = [ "process" ]
lineRate = [ "rate" ]

# example:
# bin      cat0 cat0  cat0 cat1 cat1  cat1 cat2 cat2  cat2 cat3 cat3  cat3 
# process  ggH  qqH  bkg   ggH  qqH  bkg   ggH  qqH  bkg   ggH  qqH  bkg   
# process  0    -1   1     0    -1   1     0    -1   1     0    -1   1     
# rate     -1   -1   1     -1   -1   1     -1   -1   1     -1   -1   1     

sigProcessNumbers = {}

for cat in allCats:

    for proc, nev in numEvents[cat].items():
        if proc == 'data':
            continue

        lineBin.append(cat)

        lineProcess1.append(proc)

        if proc == 'bkg':
            procIndex = 1
        else:
            # a signal process
            procIndex = sigProcessNumbers.setdefault(proc, - len(sigProcessNumbers))

        lineProcess2.append(procIndex)

        lineRate.append(nev)


for line in [lineBin, lineProcess1, lineProcess2, lineRate]:
    print " ".join(str(x) for x in line)

print "---------------------------------------------"

# lumi_8TeV     lnN     1.026    1.026    - 1.026    1.026    - 1.026    1.026    - 1.026    1.026    - 

print "lumi_8TeV","lnN",

numEntries = len(allCats)

lumiUncert = 1.026

for cat in allCats:
    for proc in numEvents[cat].keys():
        if proc == 'data':
            continue

        if proc == 'bkg':
            print "-",
        else:
            print lumiUncert,

print



