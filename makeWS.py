import ROOT

# the garbage collection saver (to avoid python deleting ROOT objects which ROOT still uses internally)
gcs = []


# whether or not to symmetrize the histograms and normalizations
# for the two charges for the expected
symmetrizeCharges = True

# whether to produce the charge separated objects or not
makeAcpObjects = False

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
        # keep the number of categories
        self.numCategories = cats
        self.signalLabels = signals

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
                    name = "sig" + chargeStr + "_cat"+str(cat)

                self.datahists[name].add(self.set, weight * weightFactor)

    #----------------------------------------            
