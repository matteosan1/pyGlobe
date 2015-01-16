import ROOT
import re

# the garbage collection saver (to avoid python deleting ROOT objects which ROOT still uses internally)
gcs = []


# whether or not to symmetrize the histograms and normalizations
# for the two charges for the expected
symmetrizeCharges = True

# whether to produce the charge separated objects or not
makeAcpObjects = False


#----------------------------------------------------------------------

def makeSumOfGaussians(pdfName, recoMassVar, mhypVar, deltaMuVars, sigmaVars, fractionVars):
    # mhypVar can be a float or int or a RooAbsReal

    numGaussians = len(deltaMuVars)
    assert numGaussians == len(sigmaVars)
    assert len(fractionVars) == numGaussians - 1

    pdfs = ROOT.RooArgList()

    for i in range(numGaussians):
        # massHypothesis + deltaM
        if isinstance(mhypVar, int) or isinstance(mhypVar, float):
            expr = "%f + @0" % mhypVar
            args = ROOT.RooArgList(deltaMuVars[i])
        else:
            expr = "@0 + @1"
            args = ROOT.RooArgList(mhypVar, deltaMuVars[i])

        meanVar = ROOT.RooFormulaVar(pdfName + "_mu", "mean Gaussian %d" % i,
                                     expr,
                                     args)
        gcs.append(meanVar)

        pdf = ROOT.RooGaussian(pdfName + "_g%d" % i, "Gaussian %d" % i,
                               recoMassVar,
                               meanVar,
                               sigmaVars[i])
        gcs.append(pdf)

        pdfs.add(pdf)


    # build the sum
    coeffs = ROOT.RooArgList()
    for fractionVar in fractionVars:
        coeffs.add(fractionVar)

    return ROOT.RooAddPdf(pdfName, pdfName, pdfs, coeffs, True)

#----------------------------------------------------------------------

class WSProducer:
    mass = ROOT.RooRealVar("CMS_emu_mass", "CMS_emu_mass", 180, 20, 200)
    workspace = ROOT.RooWorkspace("CMS_emu_workspace") 
    datasets  = {}
    datahists = {}

    # other objects to import into the workspace
    otherObjectsToImport = []

    set = ROOT.RooArgSet("set")
    set.add(mass)
    lumi = 0.
    signalLabels = dict()

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
                self.addDataSet("sig_Hem_unbinned_%s_%d_cat%d" % (proc, mass, cat))

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
        
    def addDataSet(self, name):
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

        self.workspace.writeToFile("workspace.root")

    #----------------------------------------

    def fillDataset(self, itype, cat, mass, weight):
        self.mass.setVal(mass)

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
                    self.datasets["sig_Hem" + chargeStr + "_unbinned_%s_%d_cat%d" % (proc, massHyp, cat)].add(self.set, weight)

                    name = "sig_Hem" + chargeStr + "_%s_%d_cat%d" % (proc, massHyp, cat)

                self.datahists[name].add(self.set, weight * weightFactor)

    #----------------------------------------

    def makeSignalPdfsForFit(self):
        # produces sum of Gaussian PDFs for fitting (i.e. without interpolation, independent
        # at each mass point)

        # assume we have all signal processes at all signal mass points

        numGaussians = 2

        for cat in range(self.numCategories):
            catname = "cat%d" % cat

            for proc in self.signalProcesses:

                # self.signalMasses is ordered
                for massIndex, mass in enumerate(self.signalMasses):
                    suffix = "_".join([
                        proc,
                        catname,
                        str(mass),
                        ])
                    

                    # create the delta mu and sigma vars
                    dmuvars = [ ROOT.RooRealVar(("dmu_g%d_m%d_" % (gaussIndex, mass)) + suffix,
                                                "delta mu",
                                                0,
                                                -10,
                                                +10)
                                for gaussIndex in range(numGaussians)]
                    sigmavars = [ ROOT.RooRealVar(("sigma_g%d_m%d_" % (gaussIndex, mass)) + suffix,
                                                "delta mu",
                                                1,
                                                0.001,
                                                10)
                                for gaussIndex in range(numGaussians)]

                    fractionvars = [ ROOT.RooRealVar(("frac_g%d_m%d_" % (gaussIndex, mass)) + suffix,
                                                "fraction variable for Gaussian sum",
                                                0.5,
                                                0,
                                                     1)
                                     for gaussIndex in range(numGaussians - 1)]
                    
                    pdf = makeSumOfGaussians("sigpdf_" + suffix,
                                             self.mass,
                                             self.mhypVar,
                                             dmuvars,
                                             sigmavars,
                                             fractionvars)
                                             
                    # import into workspace
                    self.imp(pdf, True)
                # end of loop over masses
            # end of loop over signal processes
        # end of loop over categories
