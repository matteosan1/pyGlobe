import ROOT

# the garbage collection saver (to avoid python deleting ROOT objects which ROOT still uses internally)
gcs = []


class WSProducer:
    mass = ROOT.RooRealVar("CMS_emu_mass", "CMS_emu_mass", 2000, 0, 200)
    workspace = ROOT.RooWorkspace("CMS_emu_workspace") 
    datasets  = {}
    datahists = {}

    # other objects to import into the workspace
    otherObjectsToImport = []

    set = ROOT.RooArgSet("set")
    set.add(mass)
    usedXsectBR = 0.
    #----------------------------------------
    
    def setXsectBR(self, val):
        self.usedXsectBR = val

    def prepareDataSets(self, cats):
        # keep the number of categories
        self.numCategories = cats

        for chargeStr in ("", "_muplus", "_muminus"):
            for i in xrange(cats):
                name = "sig" + chargeStr + "_cat"+str(i)
                self.addDataHist(name)
                name = "bkg" + chargeStr + "_cat"+str(i)
                self.addDataHist(name)
                name = "data" + chargeStr + "_cat"+str(i)
                self.addDataSet(name)
                name = "data" + chargeStr + "_binned_cat"+str(i)
                self.addDataHist(name)

    #----------------------------------------
        
    def addDataSet(self, name):
        self.datasets[name] = ROOT.RooDataSet(name, name, self.set)

    #----------------------------------------

    def addDataHist(self, name):
        self.datahists[name] = ROOT.RooDataHist(name, name, self.set, "weight")

    #----------------------------------------
        
    def saveWS(self):
        self.usedXsectBRVar = ROOT.RooConstVar("usedXsectBR", "cross section *BR used to produce the initial workspace", self.usedXsectBR)

        getattr(self.workspace, 'import')(self.usedXsectBRVar, ROOT.RooFit.RecycleConflictNodes())
        getattr(self.workspace, 'import')(self.mass)
        
        for d in self.datasets.values():
            getattr(self.workspace, 'import')(d)

        for h in self.datahists.values():
            getattr(self.workspace, 'import')(h)

        self.workspace.writeToFile("workspace.root")

    #----------------------------------------

    def fillDataset(self, itype, cat, mass, weight, muonCharge):

        self.mass.setVal(mass)

        chargeStrs = [ "" ]
        if muonCharge == +1:
            chargeStrs.append("_muplus")
        elif muonCharge == -1:
            chargeStrs.append("_muminus")
        else:
            raise Exception("muon charge must be +1 or -1, got " + str(muonCharge))

        # loop over 'no charge distinction' and 'charge of the muon'
        for chargeStr in chargeStrs:
   
            if (itype == 0):
                name = "data" + chargeStr + "_cat"+str(cat)
                self.datasets[name].add(self.set, weight)
                name = "data_binned" + chargeStr + "_cat"+str(cat)
                self.datahists[name].add(self.set, weight)
            elif (itype > 0):
                name = "bkg" + chargeStr + "_cat"+str(cat)
                self.datahists[name].add(self.set, weight)
            else:
                name = "sig" + chargeStr + "_cat"+str(cat)
                self.datahists[name].add(self.set, weight)

    #----------------------------------------            
