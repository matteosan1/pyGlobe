#include "TFile.h"
#include "TTree.h"

float getBestPair(int nPairs, float* sumpts) {
  float bestSumpt = 0;
  float bestPair = -1;
  for (int p=0; p<nPairs; p++) {
    if (sumpts[p] > bestSumpt) {
      bestSumpt = sumpts[p];
      bestPair = p;
    }
  }
   
  return bestPair;
}
 
void reduceOptree(char* inputFile, char* outputFile="test.root") {

  TFile* out_file = new TFile(outputFile, "recreate");
  TTree* out_tree = new TTree("new_opttree", "new_opttree");

  TFile* file = TFile::Open(inputFile);
  TTree* inputTree = (TTree*)file->Get("opttree");

  Int_t itype, pairs, njets20, njets30, cat[100], vbfcat[100], catnew, vbfcatnew;
  Float_t met, weight, mass_new, id_new1, id_new2, iso_new1, iso_new2, et_new1, et_new2, btag1, btag2;
  Float_t id1[100], id2[100], iso1[100], iso2[100], et1[100], et2[100];
  Float_t btag[100], mass[100], sumpt[100];
  
  inputTree->SetBranchStatus("*", 0);
  inputTree->SetBranchStatus("itype", 1);
  inputTree->SetBranchStatus("pairs", 1);
  inputTree->SetBranchStatus("weight", 1);
  inputTree->SetBranchStatus("njets20", 1);
  inputTree->SetBranchStatus("njets30", 1);
  inputTree->SetBranchStatus("met", 1);
  inputTree->SetBranchStatus("mass", 1);
  inputTree->SetBranchStatus("id1", 1);
  inputTree->SetBranchStatus("id2", 1);
  inputTree->SetBranchStatus("iso1", 1);
  inputTree->SetBranchStatus("iso2", 1);
  inputTree->SetBranchStatus("cat", 1);
  inputTree->SetBranchStatus("vbfcat", 1);
  inputTree->SetBranchStatus("et1", 1);
  inputTree->SetBranchStatus("et2", 1);
  inputTree->SetBranchStatus("btag", 1);
  inputTree->SetBranchStatus("sumpt", 1);

  inputTree->SetBranchAddress("itype"  , &itype);
  inputTree->SetBranchAddress("pairs"  , &pairs);
  inputTree->SetBranchAddress("weight" , &weight);
  inputTree->SetBranchAddress("njets20", &njets20);
  inputTree->SetBranchAddress("njets30", &njets30);
  inputTree->SetBranchAddress("met"    , &met);
  inputTree->SetBranchAddress("mass"   , &mass);
  inputTree->SetBranchAddress("id1"    , &id1);
  inputTree->SetBranchAddress("id2"    , &id2);
  inputTree->SetBranchAddress("iso1"   , &iso1);
  inputTree->SetBranchAddress("iso2"   , &iso2);
  inputTree->SetBranchAddress("cat"    , &cat);
  inputTree->SetBranchAddress("vbfcat"    , &vbfcat);
  inputTree->SetBranchAddress("et1"    , &et1);
  inputTree->SetBranchAddress("et2"    , &et2);
  inputTree->SetBranchAddress("btag"    , &btag);
  inputTree->SetBranchAddress("sumpt"    , &sumpt);


  out_tree->Branch("itype"  , &itype,    "itype/I");
  out_tree->Branch("pairs"  , &pairs,    "pairs/I");
  out_tree->Branch("weight" , &weight,   "weight/F");
  out_tree->Branch("njets20", &njets20,  "njets20/I");
  out_tree->Branch("njets30", &njets30,  "njets30/I");
  out_tree->Branch("met"    , &met,      "met/F");
  out_tree->Branch("mass"   , &mass_new, "mass/F");
  out_tree->Branch("id1"    , &id_new1,  "id1/F");
  out_tree->Branch("id2"    , &id_new2,  "id2/F");
  out_tree->Branch("iso1"   , &iso_new1, "iso1/F");
  out_tree->Branch("iso2"   , &iso_new2, "iso2/F");
  out_tree->Branch("cat"    , &catnew,   "cat/I");
  out_tree->Branch("vbfcat"    , &vbfcatnew,   "vbfcat/I");
  out_tree->Branch("et1"    , &et_new1,  "et1/F");
  out_tree->Branch("et2"    , &et_new2,  "et2/F");
  out_tree->Branch("btag1"  , &btag1,    "btag1/F");
  out_tree->Branch("btag2"  , &btag2,    "btag2/F");

  Int_t entries = inputTree->GetEntries();
 
  for (int z=0; z<entries; z++) {
    inputTree->GetEntry(z);
    
    if (itype == 0) 
      continue;

    int bestPair = getBestPair(pairs, sumpt);
    catnew = cat[bestPair];
    vbfcatnew = vbfcat[bestPair];
    et_new1 = et1[bestPair];
    et_new2 = et2[bestPair];
    id_new1 = id1[bestPair];
    id_new2 = id2[bestPair];
    iso_new1 = iso1[bestPair];
    iso_new2 = iso2[bestPair];
    mass_new = mass[bestPair];
    if (njets20 == 0) {
      btag1 = 0;
      btag2 = 0;
    } else  if (njets20 == 1) {
      btag1 = btag[0];
      btag2 = 0;
    } else {
      btag1 = btag[0];
      btag2 = btag[1];
    }

    if (btag1 < 0)
      btag1 = 0;

    if (btag2 < 0)
      btag2 = 0;


    out_tree->Fill();
  }
  

  //print "Write otuput"
  out_file->cd();
  out_tree->Write();
  out_file->Close();
  file->Close();
}
