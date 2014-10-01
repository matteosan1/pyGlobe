#include <cstdlib>
#include <iostream>
#include <map>
#include <string>

#include "TChain.h"
#include "TFile.h"
#include "TTree.h"
#include "TString.h"
#include "TObjString.h"
#include "TSystem.h"
#include "TROOT.h"

//#if not defined(__CINT__) || defined(__MAKECINT__)
// needs to be included when makecint runs (ACLIC)
#include "TMVA/Factory.h"
#include "TMVA/Tools.h"
#include "TMVA/MethodCategory.h"
#include "TMVA/MethodBase.h"
#include "TMVA/MethodCuts.h"
//#endif

void optimizator_v3(const char* outputFileName = "TMVA_cic") {
  
  TMVA::Tools::Instance();
  char a[100];
  sprintf(a, "%s.root", outputFileName);
  TFile* outputFile = TFile::Open(a, "RECREATE");
  TMVA::Factory *factory = new TMVA::Factory(outputFileName, outputFile, "!V:!Silent");

  factory->AddVariable("id1", 'F');
  factory->AddVariable("iso1", 'F');
  factory->AddVariable("met", 'F');
  factory->AddVariable("njets20", 'F');
  factory->AddVariable("btag1", 'F');
  factory->AddVariable("btag2", 'F');

  factory->AddSpectator("itype", 'F'); 
  //factory->AddSpectator("cat", 'F');


  TFile* input = TFile::Open("test.root");
  TTree* inputTree = (TTree*)input->Get("new_opttree");
  outputFile->cd();

  factory->SetInputTrees(inputTree, "itype < 0 && iso1<0.5 && mass >100 && id2==11", "itype > 0 && iso1<0.5 && mass>100 && id2==11");  
  factory->SetWeightExpression("weight");

  factory->PrepareTrainingAndTestTree("", "",
				      "nTrain_Signal=0:nTrain_Background=0::nTest_Signal=0:nTest_Background=0:SplitMode=Random:!V" );

  const int nCategories = 1;
  const int nMethods = 1;
  TMVA::MethodCategory* mcat[nMethods];
  TMVA::MethodBase* methodBase[nMethods];

  TString vars = "id1:iso1:met:njets20:btag1:btag2";
  
  TCut cat_definition[nCategories];
  cat_definition[0] = "cat == 0";
  
  TString methodOptions[nMethods];
  methodOptions[1] = "!H:!V:EffMethod=EffSel:FitMethod=MC";
  methodOptions[0] = "!H:!V:EffMethod=EffSel:FitMethod=GA:VarProp[0]=FMax:VarProp[1]=FMin:VarProp[2]=FMin:VarProp[3]=FMin:VarProp[3]=FMin";
  
  for (int i=0; i<1; i++) {
    sprintf(a, "Category_Cuts%d", i);
    methodBase[i] = factory->BookMethod(TMVA::Types::kCategory, a, "!V");
    
    mcat[i] = dynamic_cast<TMVA::MethodCategory*>(methodBase[i]);
    for (int j=0; j<nCategories; j++) {
      sprintf(a, "Category_Cuts%d_%d", i, j);
      mcat[i]->AddMethod(cat_definition[j], vars, TMVA::Types::kCuts, a, methodOptions[i]);
    }
  }
  
  factory->TrainAllMethods();
  factory->TestAllMethods();
  factory->EvaluateAllMethods();
  
  outputFile->Close();

  delete factory;
}
