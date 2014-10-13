import ROOT

# the garbage collection saver (to avoid python deleting ROOT objects which ROOT still uses internally)
gcs = []


class WSProducer:
    mass = ROOT.RooRealVar("CMS_emu_mass", "CMS_emu_mass", 100, 20, 200)
    mass.setBins(90)
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
                name = "data_binned" + chargeStr + "_cat"+str(i)
                self.addDataHist(name)

    #----------------------------------------
        
    def addDataSet(self, name):
        self.datasets[name] = ROOT.RooDataSet(name, name, self.set)

    #----------------------------------------

    def addDataHist(self, name):
        self.datahists[name] = ROOT.RooDataHist(name, name, self.set, "weight")

    #----------------------------------------

    def getWsObj(self, name):
        # retrieves an object by name from the workspace
        obj = self.workspace.obj(name)
        if obj == None:
            raise Exception("could not find an object named '%s' in the workspace" % name)

        return obj
    
    #----------------------------------------

    def importObj(self, obj):
        # imports and object into the workspace
        getattr(self.workspace, 'import')(obj, ROOT.RooFit.RecycleConflictNodes())

    #----------------------------------------

    # produce charge asymmetry related objects and import into the workspace
    def saveAcpObjects():
        # common to all categories (for the moment)
        acpVar = ROOT.RooRealVar("aCP","CP/charge asymmetry",0, -1, +1); gcs.append(acpVar)

        for cat in xrange(self.numCategories):

            # for building the sum affected by aCP 
            pdfList = ROOT.RooArgList()
            coeffList = ROOT.RooArgList()

            for muonCharge, chargeStr in ((-1, "_muminus"),
                                          (+1, "_muplus")):

                # get the number of expected events variable
                normVar = self.getWsObj("pdf_{proc}_cat{cat}_norm".format(**locals()))
                assert normVar != None

                # build a normalization variable which changes with aCP
                sign = ("%+d" % muonCharge)[0] # '+' or '-'

                name = "acp_sig{chargeStr}_cat{cat}".format(**locals())

                # n+/- = n / 2 * (1 +/- aCP)
                tmp = ROOT.RooArgList(self.getWsObj("pdf_sig_cat{cat}_norm".format(**locals())), # the total number of expected events for both charges
                                      acpVar)

                normVar = ROOT.RooFormulaVar(name + "_norm", name + "_norm",
                                             "0.5 * @0 * (1 %s @1)" % sign, tmp)
                gcs.append(normVar)

                # for the RooAddPdf
                coeffList.add(normVar)
                pdfList.add(self.getWsObj("pdf_sig{chargeStr}_cat{cat}".format(**locals())))

            # end of loop over muon charges

            # build a RooAddPdf 
            name = "acp_sig_cat{cat}".format(**locals())
            pdf = ROOT.RooAddPdf(name,
                                 "aCP enabled signal PDF for cat {cat}".format(**locals()),
                                 pdfList,
                                 coeffList,
                                 False        # recursive fraction
                                 )

            gcs.append(pdf)
            self.importObj(pdf)

            # do we need the corresponding norm variable for combine or does it take it from the RooAddPdf ?
            if True:
                # this is essentially a clone (under a different name so combine can find it)
                # of the sum of + and - expected number of events
                name = "acp_sig_cat{cat}_norm".format(**locals())

                normVar = self.getWsObj("pdf_sig_cat{cat}_norm".format(**locals())).Clone(name)
                gcs.append(normVar)

                self.importObj(normVar)


        # end of loop over all categories

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
