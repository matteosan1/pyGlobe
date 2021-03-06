import ROOT
import re

import utils

# the garbage collection saver (to avoid python deleting ROOT objects which ROOT still uses internally)
gcs = []


# whether or not to symmetrize the histograms and normalizations
# for the two charges for the expected
symmetrizeCharges = True

# whether to produce the charge separated objects or not
makeAcpObjects = False


#----------------------------------------------------------------------

class WSProducer:

    # for filling weighted datsets (for signal)
    weightVar = ROOT.RooRealVar("weight","weight",1)
    
    workspace = ROOT.RooWorkspace("CMS_emu_workspace") 
    datasets  = {}
    datahists = {}

    # other objects to import into the workspace
    otherObjectsToImport = []

    set = ROOT.RooArgSet("set")

    massWithWeight = ROOT.RooArgSet("massWithWeight")
    massWithWeight.add(weightVar)

    lumi = 0.
    signalLabels = dict()

    #----------------------------------------
    def __init__(self, options):
        self.options = options

        # TODO: should ensure that 140 is within the specified limit...
        self.mass = ROOT.RooRealVar("CMS_emu_mass", "m_{e#mu}", 140, options.mmin, options.mmax)
        self.mass.setUnit("GeV/c^{2}")

        self.set.add(self.mass)

        self.massWithWeight.add(self.mass)

    #----------------------------------------
    
    def setGlobalParameters(self, lumi):
        self.lumi = lumi

    def prepareDataSets(self, cats, signals):
        # signals is a dict of itype to a tuple (name, used_cross_section)

        # keep the number of categories
        self.numCategories = cats
        self.signalLabels = signals

        # all production processes found
        self.signalProcesses = set()

        # all mass points found
        self.signalMasses = set()

        # maps from itype to mass hypothesis and signal process
        self.itypeToMassAndProc = {}
        
        #----------
        # find all mass points at which we have signal MC
        #----------
        for itype, value in self.signalLabels.items():
            # e.g. "Hem_ggh_120"
            name = value[0]
            mo = re.match("Hem_(\S+)_(\S+)$", name)
            assert mo, "unexpected signal process name " + name

            proc = mo.group(1)
            mass = int(mo.group(2))

            self.signalProcesses.add(proc)
            self.signalMasses.add(mass)

            self.itypeToMassAndProc[itype] = dict(mass = mass, proc = proc)

            # add a dataset for signal MC
            assert not makeAcpObjects, "not yet implemented for charge separation"
            for cat in range(cats):
                self.addDataSet("sig_Hem_unbinned_%s_%d_cat%d" % (proc, mass, cat), True)

        # convert to a list
        self.signalMasses = sorted(list(self.signalMasses))

        # mass hypothesis variable
        self.mhypVar = ROOT.RooRealVar("mh","mass hypothesis", min(self.signalMasses), max(self.signalMasses))

        #----------            

        for i in xrange(cats):
            for s in self.signalLabels:
                name = "sig_"+self.signalLabels[s][0]+"_cat"+str(i)
                self.addDataHist(name)
            name = "bkg_cat"+str(i)
            self.addDataHist(name)
            name = "data_cat"+str(i)
            self.addDataSet(name)
            name = "data_binned_cat"+str(i)
            self.addDataHist(name)

    #----------------------------------------
        
    def addDataSet(self, name, weighted = False):
        if weighted:
            self.datasets[name] = ROOT.RooDataSet(name, name, self.massWithWeight, self.weightVar.GetName())
        else:
            self.datasets[name] = ROOT.RooDataSet(name, name, self.set)

    #----------------------------------------

    def addDataHist(self, name):
        self.datahists[name] = ROOT.RooDataHist(name, name, self.set, "weight")

    #----------------------------------------

    def imp(self, obj, recycle = False):
        # helper function to import objects into the output workspace
        if recycle:
            getattr(self.workspace,'import')(obj, ROOT.RooFit.RecycleConflictNodes())
        else:
            getattr(self.workspace,'import')(obj)

    #----------------------------------------

    def _makeRooCategory(self, varname, values):
        var = ROOT.RooCategory(varname, varname)
        for value in values:
            var.defineType(str(value))

        self.imp(var)

    #----------------------------------------
        
    def saveWS(self):
        for s in self.signalLabels:
            self.usedXsectBRVar = ROOT.RooConstVar("usedXsectBR_"+self.signalLabels[s][0], "cross section *BR used to produce the initial workspace", self.signalLabels[s][1])
            self.imp(self.usedXsectBRVar, True)
        
        self.imp(self.mass)

        self.lumiVar = ROOT.RooConstVar("lumi", "Integrated luminosity", self.lumi)
        self.imp(self.lumiVar, True)

        for d in self.datasets.values():
            self.imp(d)

        for h in self.datahists.values():
            self.imp(h)

        #----------
        # create RooCategories with signal masses, signal processes and categories
        # so we don't have to guess them in other programs such as
        # the signal fit
        #----------
        self._makeRooCategory("allCategories", [ "cat%d" % cat for cat in range(self.numCategories) ])
        self._makeRooCategory("allSigProcesses", sorted(self.signalProcesses))
        self._makeRooCategory("allSigMasses", sorted(self.signalMasses))

        #----------

        self.workspace.writeToFile(self.options.wsoutFname)

    #----------------------------------------

    def fillDataset(self, itype, cat, mass, weight):

        # the underflow/overflow behaviour seems to be
        # such that in the dataset we get e.g. lots
        # of entries in the dataset at the lower and
        # higher end of the variable range...
        if mass < self.mass.getMin() or mass >= self.mass.getMax():
            return

        self.mass.setVal(mass)
        self.weightVar.setVal(weight)

        chargeStrs = [ "" ]
        weightFactors = [ 1 ] # mostly for symmetrizing the expected charge specific histograms

        if makeAcpObjects:
            if symmetrizeCharges:
                # we append half of the weight to both charges
                # (note that the errors on the bins will be too small
                # by a factor sqrt(2))
                chargeStrs.extend(["_muplus", "_muminus"])
                weightFactors.extend([0.5, 0.5])
            else:
                if muonCharge == +1:
                    chargeStrs.append("_muplus")
                    weightFactors.append(1)
                elif muonCharge == -1:
                    chargeStrs.append("_muminus")
                    weightFactors.append(1)
                else:
                    raise Exception("muon charge must be +1 or -1, got " + str(muonCharge))



        # loop over 'no charge distinction' and 'charge of the muon'
        for chargeStr, weightFactor in zip(chargeStrs, weightFactors):
   
            if (itype == 0):
                # this is data
                name = "data" + chargeStr + "_cat"+str(cat)
                self.datasets[name].add(self.set, weight)
                name = "data_binned" + chargeStr + "_cat"+str(cat)
                self.datahists[name].add(self.set, weight)
            else:
                # this is MC
                if (itype > 0):
                    name = "bkg" + chargeStr + "_cat"+str(cat)
                else:
                    # must find mass hypothesis and production process first
                    massHyp = self.itypeToMassAndProc[itype]['mass']
                    proc    = self.itypeToMassAndProc[itype]['proc']

                    # add also to signal datasets
                    self.weightVar.setVal(weight * weightFactor)
                    self.datasets["sig_Hem" + chargeStr + "_unbinned_%s_%d_cat%d" % (proc, massHyp, cat)].add(self.massWithWeight, weight * weightFactor)

                    name = "sig_Hem" + chargeStr + "_%s_%d_cat%d" % (proc, massHyp, cat)

                self.datahists[name].add(self.set, weight * weightFactor)

    #----------------------------------------

