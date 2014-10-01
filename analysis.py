import ROOT
from helpers import getEMuPair, emuSelection
from  makeWS import WSProducer
import plotfromoptree, table

class Analysis:
    def __init__(self, options):
        self.options = options
        self.counter = []
        self.generalInfo = []

    def Run(self):
        self.initialize()
        self.loadTree()
        self.loop()
        self.finalize()

    def finalize(self):
        #self.wsProducer.finalize()
        self.wsProducer.setXsectBR(self.generalInfo[0])
        self.wsProducer.saveWS()

        self.counter.Print(self.samples)

        output = ROOT.TFile(self.options.output, "recreate")
        for h in self.allHistos.histos.values():
            h.Write()
        
        self.inputfiletree.Write()
        self.plotvariabletree.Write()
        output.Close()

    def initialize(self):
        print "Parsing inputfiles..."
        self.samples, self.generalInfo = plotfromoptree.parseInputfiles(self.options.inputfile)
        print "Parsing plotvariables..."
        self.allHistos = plotfromoptree.parsePlotvariables(self.options.plotvariables, self.samples)
        print "Writing inputfiles Tree..."
        self.inputfiletree = plotfromoptree.inputfileTree(self.samples)
        print "Writing plotvariables Tree..."
        self.plotvariabletree = plotfromoptree.plotvariableTree(self.allHistos)

        self.wsProducer = WSProducer()
        self.counter = table.table(2, 3)
        self.wsProducer.prepareDataSets(3)
        

    def loadTree(self):
        self.file = ROOT.TFile(self.options.input)
        self.tree = self.file.Get("opttree")

        self.tree.SetBranchStatus("*",0)
        self.tree.SetBranchStatus("run",1)
        self.tree.SetBranchStatus("itype",1)
        self.tree.SetBranchStatus("weight",1)
        self.tree.SetBranchStatus("pairs", 1)
        self.tree.SetBranchStatus("mass",1)
        self.tree.SetBranchStatus("cat",1)
        self.tree.SetBranchStatus("sumpt", 1)
        self.tree.SetBranchStatus("ch1_1", 1)
        self.tree.SetBranchStatus("ch2_1", 1)
        self.tree.SetBranchStatus("ch3_1", 1)
        self.tree.SetBranchStatus("ch1_2", 1)
        self.tree.SetBranchStatus("ch2_2", 1)
        self.tree.SetBranchStatus("ch3_2", 1)
        self.tree.SetBranchStatus("id1", 1)
        self.tree.SetBranchStatus("id2", 1)
        self.tree.SetBranchStatus("iso1", 1)
        self.tree.SetBranchStatus("iso2", 1)
        self.tree.SetBranchStatus("met",1)
        self.tree.SetBranchStatus("njets30",1)
        self.tree.SetBranchStatus("njets20",1)
        self.tree.SetBranchStatus("btag", 1)
        self.tree.SetBranchStatus("et1", 1)
        self.tree.SetBranchStatus("et2", 1)
        self.tree.SetBranchStatus("eta1", 1)
        self.tree.SetBranchStatus("eta2", 1)
        self.tree.SetBranchStatus("phi1", 1)
        self.tree.SetBranchStatus("phi2", 1)

        self.entries = self.tree.GetEntries()

    def loop(self):
        for z in xrange(self.entries):
            self.tree.GetEntry(z)
            self.processPair()
            
    def processPair(self):
        itype = self.tree.itype
        if (itype not in self.samples):
            return

        pairs = self.tree.pairs
        cats = self.tree.cat
        weight = self.tree.weight
        masses = self.tree.mass
        et1 = self.tree.et1
        et2 = self.tree.et2
        id1 = self.tree.id1
        id2 = self.tree.id2
        iso1 = self.tree.iso1
        iso2 = self.tree.iso2
        met = self.tree.met
        njets20 = self.tree.njets20
        btag1 = -9999.
        btag2 = -9999.
        if (njets20 == 1):
            btag1 = self.tree.btag[0]
        if (njets20 > 1):
            btag2 = self.tree.btag[1]
        
        p = getEMuPair(pairs, self.tree.sumpt)
        if (p == -1):
            return

        #self.counter.Fill(0, itype, cats[p], weight)
        self.counter.Fill(0, itype, cats[p], 1)

        if (masses[p] > 20.):
            #print "cat:",cats[p]
            #print "print:",emuSelection(cats[p], id1[p], id2[p], iso1[p], iso2[p], met, btag1, btag2, njets20)
            if (emuSelection(cats[p], id1[p], id2[p], iso1[p], iso2[p], met, btag1, btag2, njets20)):
                #print "si"
                self.allHistos.fillHisto("massFinal", cats[p], self.samples[itype], masses[p], weight)
                self.allHistos.fillHisto("massZoomFinal", cats[p], self.samples[itype], masses[p], weight)
                self.counter.Fill(1, itype, cats[p], 1)
                self.wsProducer.fillDataset(itype, cats[p], masses[p], weight)

            self.allHistos.fillHisto("met", cats[p], self.samples[itype], met, weight)
            self.allHistos.fillHisto("et1",  cats[p], self.samples[itype], et1[p],    weight)
            self.allHistos.fillHisto("et2",  cats[p], self.samples[itype], et2[p],    weight)
            
            self.allHistos.fillHisto("id1",  cats[p], self.samples[itype], id1[p],    weight)
            self.allHistos.fillHisto("id2",  cats[p], self.samples[itype], id2[p],    weight)
            self.allHistos.fillHisto("iso1", cats[p], self.samples[itype], iso1[p],   weight)
            self.allHistos.fillHisto("iso2", cats[p], self.samples[itype], iso2[p],   weight)
            
            if (met < 45.):
                self.allHistos.fillHisto("njet20", cats[p], self.samples[itype], njets20, weight)
            
                if    ((njets20 == 0)):
                    if (self.options.blind and itype == 0 and masses[p] >=110 and masses[p] <= 160):
                        self.allHistos.fillHisto("mass", cats[p], self.samples[itype], 0, weight)
                        self.allHistos.fillHisto("masszoom", cats[p], self.samples[itype], 0, weight)
                    else:
                        self.allHistos.fillHisto("mass", cats[p], self.samples[itype], masses[p], weight)
                        self.allHistos.fillHisto("masszoom", cats[p], self.samples[itype], masses[p], weight)

