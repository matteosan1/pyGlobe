import ROOT
import sys, array

sieie = array.array('f',[0])
r9 = array.array('f',[0])
iso = array.array('f',[0])
isow = array.array('f',[0])
tkiso = array.array('f',[0])
hoe = array.array('f',[0])
sieip = array.array('f',[0])
etawidth = array.array('f',[0])
phiwidth = array.array('f',[0])
s4ratio = array.array('f',[0])
itype = array.array('f',[0])
eta = array.array('f',[0])
genmatch = array.array('f',[0])

def BookMVA():
    global sieie, r9, iso, isow, tkiso, hoe, itype, eta, genmatch
    readers= []
    for i in xrange(4):
        readers.append(ROOT.TMVA.Reader())    
        
        readers[-1].AddVariable("sieie", sieie)
        readers[-1].AddVariable("r9", r9)
        #readers[-1].AddVariable("iso:=((chiso+phoiso-rho*0.09)/et)", iso)
        #readers[-1].AddVariable("isow:=((chisow+phoiso-rho*0.23)/et)", isow)
        readers[-1].AddVariable("isorv", iso)
        readers[-1].AddVariable("isowv", isow)
        readers[-1].AddVariable("tkiso:=chiso*50./et", tkiso)
        readers[-1].AddVariable("hoe", hoe)
        #readers[-1].AddVariable("sieip", sieip)
        #readers[-1].AddVariable("etawidth", etawidth)
        #readers[-1].AddVariable("phiwidth", phiwidth)
        #readers[-1].AddVariable("s4ratio", s4ratio)
        readers[-1].AddSpectator("itype", itype); 
        readers[-1].AddSpectator("eta", eta);
        readers[-1].AddSpectator("genmatch", genmatch);
        
        #readers[-1].BookMVA("Cuts", "weights/TMVA_CiC_Cuts_cat"+str(i)+".weights.xml")
        #readers[-1].BookMVA("Cuts", "weights/allvar_cat"+str(i)+"_Cuts_cat"+str(i)+".weights.xml")
        #readers[-1].BookMVA("Cuts", "weights/newtest_"+str(i)+"_Cuts_cat"+str(i)+".weights.xml")
        #readers[-1].BookMVA("Cuts", "weights/maxweighttest_v2_Cuts_cat"+str(i)+".weights.xml")
        #readers[-1].BookMVA("Cuts", "weights/test_Cuts_cat"+str(i)+".weights.xml")
        readers[-1].BookMVA("Cuts", "weights/newMCTraining.root_Cuts_cat"+str(i)+".weights.xml")
        
    return readers

modEffS = [0,0,0,0]
effS = [0.95, 0.84, 0.89, 0.71]

markers = (21, 22, 23, 24)
colors = (ROOT.kBlue, ROOT.kRed, ROOT.kGreen, ROOT.kOrange)

hnum=[]
hden=[]
hnumpt=[]
hdenpt=[]

for i in xrange(4):
    hnum.append(ROOT.TH1F("hnum"+str(i), "hnum"+str(i), 50, -2.5, 2.5))
    hden.append(ROOT.TH1F("hden"+str(i), "hden"+str(i), 50, -2.5, 2.5))
    hnum[-1].Sumw2()
    hden[-1].Sumw2()
    hnum[-1].SetMarkerStyle(markers[i])
    hnum[-1].SetMarkerColor(colors[i])
    hnum[-1].SetLineColor(colors[i])

    hnumpt.append(ROOT.TH1F("hnumpt"+str(i), "hnumpt"+str(i), 40, 20, 100))
    hdenpt.append(ROOT.TH1F("hdenpt"+str(i), "hdenpt"+str(i), 40, 20, 100))
    hnumpt[-1].Sumw2()
    hdenpt[-1].Sumw2()
    hnumpt[-1].SetMarkerStyle(markers[i])
    hnumpt[-1].SetMarkerColor(colors[i])
    hnumpt[-1].SetLineColor(colors[i])

readers = BookMVA()

file = ROOT.TFile(sys.argv[1])
tree = file.Get(sys.argv[2])
isSignal = False
if (int(sys.argv[3]) != 0):
    isSignal = True

entries = tree.GetEntries()

results = []

for r in xrange(0, 1):
    for i in xrange(4):
        modEffS[i] = effS[i] + r*0.01

    nnum=[0,0,0,0]
    nden=[0,0,0,0]

    for z in xrange(entries):
        tree.GetEntry(z)
        if ((tree.itype < 0 and tree.genmatch==1 and isSignal) or
            #(tree.itype > 0 and tree.itype!=3 and tree.genmatch==0 and not isSignal)):
            (tree.itype > 0 and tree.itype !=3 and not isSignal)):
        
            cat = -1
            if (abs(tree.eta) < 1.479 and  tree.r9 > 0.94):
                cat = 0
            elif (abs(tree.eta) < 1.479 and tree.r9 < 0.94):
                cat = 1
            elif (abs(tree.eta) > 1.479 and tree.r9 > 0.94):
                cat = 2
            elif (abs(tree.eta) > 1.479 and tree.r9 < 0.94):
                cat = 3

            if (cat == -1):
                continue

            sieie[0]    = tree.sieie
            r9[0]       = tree.r9
            iso[0]      = tree.isorv
            isow[0]     = tree.isowv
            tkiso[0]    = tree.chiso*50./tree.et
            hoe[0]      = tree.hoe
            #sieip[0]    = tree.sieip
            #etawidth[0] = tree.etawidth
            #phiwidth[0] = tree.phiwidth
            #s4ratio[0]  = tree.s4ratio
            itype[0]    = tree.itype
            eta[0]      = tree.eta
            genmatch[0] = tree.genmatch

            hden[cat].Fill(tree.eta, tree.full_weight)
            hdenpt[cat].Fill(tree.et, tree.full_weight)
            nden[cat] = nden[cat] + 1
            if (readers[cat].EvaluateMVA("Cuts", modEffS[cat])):
                hnum[cat].Fill(tree.eta, tree.full_weight)
                hnumpt[cat].Fill(tree.et, tree.full_weight)
                nnum[cat] = nnum[cat] + 1

    print modEffS
    for i in xrange(4):
        print float(nnum[i])/float(nden[i])
        results.append(float(nnum[i])/float(nden[i]))
    print "__________________"

c = ROOT.TCanvas("c", "c")
for i in xrange(4):
    hnum[i].Divide(hden[i])
    if (i==0):
        hnum[i].Draw("PE")
    else:
        hnum[i].Draw("PESAME")

c1 = ROOT.TCanvas("c1", "c1")
for i in xrange(4):
    hnumpt[i].Divide(hdenpt[i])
    if (i==0):
        hnumpt[i].Draw("PE")
    else:
        hnumpt[i].Draw("PESAME")

c2 = ROOT.TCanvas("c2", "c2")
for i in xrange(4):
    if (i==0):
        hnum[i].Draw("PE")
    else:
        hnum[i].Draw("PESAME")

#c.SaveAs("effMVA.png")
#for r in results:
#    print r+",",
raw_input()
