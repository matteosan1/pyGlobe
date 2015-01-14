import ROOT

# the garbage collection saver (to avoid python deleting ROOT objects which ROOT still uses internally)
gcs = []


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
        
    def saveWS(self):
        for s in self.signalLabels:
            self.usedXsectBRVar = ROOT.RooConstVar("usedXsectBR_"+self.signalLabels[s][0], "cross section *BR used to produce the initial workspace", self.signalLabels[s][1])
            getattr(self.workspace, 'import')(self.usedXsectBRVar, ROOT.RooFit.RecycleConflictNodes())
        
        getattr(self.workspace, 'import')(self.mass)

        self.lumiVar = ROOT.RooConstVar("lumi", "Integrated luminosity", self.lumi)
        getattr(self.workspace, 'import')(self.lumiVar, ROOT.RooFit.RecycleConflictNodes())

        for d in self.datasets.values():
            getattr(self.workspace, 'import')(d)

        for h in self.datahists.values():
            getattr(self.workspace, 'import')(h)

        self.workspace.writeToFile("workspace.root")

    #----------------------------------------

    def fillDataset(self, itype, cat, mass, weight):
        self.mass.setVal(mass)
   
        if (itype == 0):
            name = "data_cat"+str(cat)
            self.datasets[name].add(self.set, weight)
            name = "data_binned_cat"+str(cat)
            self.datahists[name].add(self.set, weight)
        elif (itype > 0):
            name = "bkg_cat"+str(cat)
            self.datahists[name].add(self.set, weight)
        else:
            name = "sig_"+self.signalLabels[itype][0]+"_cat"+str(cat)
            self.datahists[name].add(self.set, weight)

    #----------------------------------------            
