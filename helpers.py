import ROOT
import sys

def getEMuPair(nPairs, sumpts):
    bestSumpt = 0
    bestPair = -1
    for p in xrange(nPairs):
        if (sumpts[p] > bestSumpt):
            bestSumpt = sumpts
            bestPair = p
            
    return bestPair

def emuSelectionV2(cat, et1, et2, id1, id2, iso1, iso2, met, btag1, btag2, njets):
    if (id2 != 11):
        return False
    if (njets >= 3):
        return False
    if (cat == 0 and njets == 0):
        if (et1 > 25.2 and et2 > 21.7 and id1 > 0.706 and iso1 < 0.318 and met < 32.6):
            return True
    if (cat == 1 and njets == 0):
        if (et1 > 20.2 and et2 > 22.4 and id1 > 0.717 and iso1 < 0.248 and met < 32.9):
            return True
    if (cat == 2 and njets == 0):
        if (et1 > 22.0 and et2 > 24.5 and id1 > 0.827 and iso1 < 0.174 and met < 20.1):
            return True

    if (cat == 0 and njets == 1):
        if (et1 > 29.9 and et2 > 22.3 and id1 > 0.896 and iso1 < 0.095 and met < 25.1 and btag1 < 0.398):
            return True
    if (cat == 1 and njets == 1):
        if (et1 > 20.7 and et2 > 21.0 and id1 > 0.798 and iso1 < 0.374 and met < 28.8 and btag1 < 0.508):
            return True
    if (cat == 2 and njets == 1):
        if (et1 > 26.4 and et2 > 20.9 and id1 > 0.734 and iso1 < 0.353 and met < 32.5 and btag1 < 0.816):
            return True

    if (cat == 0 and njets >= 2):
        if (et1 > 24.5 and et2 > 28.6 and id1 > 0.835 and iso1 < 0.081 and met < 35.9 and btag1 < 0.353 and btag2 < 0.495):
            return True
    if (cat == 1 and njets >= 2):
        if (et1 > 22.7 and et2 > 21.2 and id1 > 0.754 and iso1 < 0.331 and met < 32.7 and btag1 < 0.539 and btag2 < 0.768):
            return True
    if (cat == 2 and njets >= 2):
        if (et1 > 23.2 and et2 > 21.2 and id1 > 0.829 and iso1 < 0.178 and met < 24.6 and btag1 < 0.242 and btag2 < 0.751):
            return True

    return False

def emuSelectionV3(cat, vbfcat, et1, et2, id1, id2, iso1, iso2, met, btag1, btag2, njets):
    if (id2 != 11):
        return False
    if (njets >= 3):
        return False
    if (vbfcat == -1):
        if (cat == 0 and njets == 0):
            if (et1 > 26.3 and et2 > 28.1 and id1 > 0.800 and iso1 < 0.497 and met < 30.2):
                return True
        if (cat == 1 and njets == 0):
            if (et1 > 21.3 and et2 > 20.6 and id1 > 0.576 and iso1 < 0.472 and met < 30.7):
                return True
        if (cat == 2 and njets == 0):
            if (et1 > 21.3 and et2 > 20.6 and id1 > 0.576 and iso1 < 0.472 and met < 30.7):
                return True
    
        if (cat == 0 and njets == 1):
            if (et1 > 21.1 and et2 > 22.7 and id1 > 0.652 and iso1 < 0.109 and met < 27.1 and btag1 < 0.38):
                return True
        if (cat == 1 and njets == 1):
            if (et1 > 22.4 and et2 > 21.8 and id1 > 0.622 and iso1 < 0.095 and met < 26.3 and btag1 < 0.480):
                return True
        if (cat == 2 and njets == 1):
            if (et1 > 23.3 and et2 > 24.8 and id1 > 0.684 and iso1 < 0.083 and met < 22.7 and btag1 < 0.308):
                return True
    
        if (cat == 0 and njets >= 2):
            if (et1 > 26.4 and et2 > 27.3 and id1 > 0.810 and iso1 < 0.197 and met < 26.4 and btag1 < 0.378 and btag2 < 0.476):
                return True
        if (cat == 1 and njets >= 2):
            if (et1 > 21.5 and et2 > 20.4 and id1 > 0.684 and iso1 < 0.223 and met < 32.2 and btag1 < 0.508 and btag2 < 0.568):
                return True
        if (cat == 2 and njets >= 2):
            if (et1 > 21.5 and et2 > 20.4 and id1 > 0.684 and iso1 < 0.223 and met < 32.2 and btag1 < 0.508 and btag2 < 0.568):
                return True
    else:
        if (vbfcat == 1):
            if (et1 > 21.3 and et2 > 20.8 and id1 > 0.780 and iso1 < 0.0666 and met < 30.5 and btag1 < 0.58 and btag2 < 0.007):
                return True
        if (vbfcat == 2):
            if (et1 > 21.3 and et2 > 20.9 and id1 > 0.970 and iso1 < 0.0594 and met < 27.4 and btag1 < 0.62 and btag2 < 0.33):
                return True

    return False


#----------------------------------------------------------------------
# first index is number of jets,
# second index is lepton category
# value is the list of btag (upper) cuts
emuSelectionV3Simplified_inclCatBtagCuts = {
    # 0 jets
    0: { 0: [], 1: [], 2: [] },

    # 1 jet
    1: { 0: [ 0.38 ],
         1: [ 0.48 ],
         2: [ 0.48 ] },

    # 2 jets
    2: { 0: [ 0.38, 0.48 ],
         1: [ 0.51, 0.57 ],
         2: [ 0.51, 0.57 ],
                  }
        }

# index is vbf category
emuSelectionV3Simplified_vbfCatBtagCuts = {
    # cat9
    1: [ 0.58, 0.244 ],

    # cat10
    2: [ 0.62, 0.30 ],
    }


def getMetCutOld(cat, njets, vbfcat):
    # originally optimized values, before ARC comments of 2015-05-20
    if (vbfcat == -1):
        if (cat == 0 and njets == 0):
            return 30

        if (cat == 1 and njets == 0):
            return 30

        if (cat == 2 and njets == 0):
            return 30
    
        if (cat == 0 and njets == 1):
            return 30

        if (cat == 1 and njets == 1):
            return 22

        if (cat == 2 and njets == 1):
            return 22
    
        if (cat == 0 and njets >= 2):
            return 25

        if (cat == 1 and njets >= 2):
            return 32

        if (cat == 2 and njets >= 2):
            return 32

    else:
        if (vbfcat == 1):
            return 30

        if (vbfcat == 2):
            return 25     
    
    

def emuSelectionV3SimplifiedExceptBtag(cat, vbfcat, et1, et2, id1, id2, iso1, iso2, met, njets):
    if (id2 != 11):
        return False
    if (njets >= 3):
        return False

    metCut = getMetCutOld(cat, njets, vbfcat)

    if (vbfcat == -1):
        if (cat == 0 and njets == 0):
            # cat 0
            if (et1 > 25 and et2 > 25 and id1 > 0.800 and iso1 < 0.500 and met < metCut):
                return True

        if (cat == 1 and njets == 0):
            # cat 3
            if (et1 > 20 and et2 > 20 and id1 > 0.580 and iso1 < 0.470 and met < metCut):
                return True

        if (cat == 2 and njets == 0):
            # cat 6
            if (et1 > 20 and et2 > 20 and id1 > 0.580 and iso1 < 0.470 and met < metCut):
                return True
    
        if (cat == 0 and njets == 1):
            # cat 1
            if (et1 > 22 and et2 > 22 and id1 > 0.650 and iso1 < 0.110 and met < metCut):
                return True

        if (cat == 1 and njets == 1):
            # cat 4
            if (et1 > 22 and et2 > 22 and id1 > 0.680 and iso1 < 0.095 and met < metCut):
                return True

        if (cat == 2 and njets == 1):
            # cat 7
            if (et1 > 22 and et2 > 22 and id1 > 0.680 and iso1 < 0.095 and met < metCut):
                return True
    
        if (cat == 0 and njets >= 2):
            # cat 2
            if (et1 > 25 and et2 > 25 and id1 > 0.810 and iso1 < 0.200 and met < metCut):
                return True

        if (cat == 1 and njets >= 2):
            # cat 5
            if (et1 > 20 and et2 > 20 and id1 > 0.690 and iso1 < 0.220 and met < metCut):
                return True

        if (cat == 2 and njets >= 2):
            # cat 8
            if (et1 > 20 and et2 > 20 and id1 > 0.690 and iso1 < 0.220 and met < metCut):
                return True
    else:
        if (vbfcat == 1):
            # cat 9
            if (et1 > 22 and et2 > 22 and id1 > 0.78 and iso1 < 0.067 and met < metCut):
                return True

        if (vbfcat == 2):
            # cat 10
            if (et1 > 22 and et2 > 22 and id1 > 0.97 and iso1 < 0.060 and met < metCut):
                return True

    return False

def emuSelectionV3SimplifiedBtagOnly(cat, vbfcat, btag1, btag2, njets):
    # btag only part of original emuSelectionV3Simplified(..)
    if (njets >= 3):
        return False

    btags = [ btag1, btag2 ]

    if (vbfcat == -1):
        # inclusive categories
        btagCuts = emuSelectionV3Simplified_inclCatBtagCuts[njets][cat]

    else:
        # VBF categories
        btagCuts = emuSelectionV3Simplified_vbfCatBtagCuts[vbfcat]

    # apply the cuts
    for btag, cut in zip(btags, btagCuts):
      if btag >= cut:
         return False

    return True

#----------------------------------------------------------------------

def emuSelectionV3SimplifiedN_1ET2(cat, vbfcat, et1, et2, id1, id2, iso1, iso2, met, btag1, btag2, njets):
    if (id2 != 11):
        return False
    if (njets >= 3):
        return False
    if (vbfcat == -1):
        if (cat == 0 and njets == 0):
            if (et1 > 25 and id1 > 0.800 and iso1 < 0.500 and met < 30):
                return True
        if (cat == 1 and njets == 0):
            if (et1 > 20 and id1 > 0.580 and iso1 < 0.470 and met < 30):
                return True
        if (cat == 2 and njets == 0):
            if (et1 > 20 and id1 > 0.580 and iso1 < 0.470 and met < 30):
                return True
    
        if (cat == 0 and njets == 1):
            if (et1 > 22 and id1 > 0.650 and iso1 < 0.110 and met < 30 and btag1 < 0.38):
                return True
        if (cat == 1 and njets == 1):
            if (et1 > 22 and id1 > 0.680 and iso1 < 0.095 and met < 22 and btag1 < 0.48):
                return True
        if (cat == 2 and njets == 1):
            if (et1 > 22 and id1 > 0.680 and iso1 < 0.095 and met < 22 and btag1 < 0.48):
                return True
    
        if (cat == 0 and njets >= 2):
            if (et1 > 25 and id1 > 0.810 and iso1 < 0.200 and met < 25 and btag1 < 0.38 and btag2 < 0.48):
                return True
        if (cat == 1 and njets >= 2):
            if (et1 > 20 and id1 > 0.690 and iso1 < 0.220 and met < 32 and btag1 < 0.51 and btag2 < 0.57):
                return True
        if (cat == 2 and njets >= 2):
            if (et1 > 20 and id1 > 0.690 and iso1 < 0.220 and met < 32 and btag1 < 0.51 and btag2 < 0.57):
                return True
    else:
        if (vbfcat == 1):
            if (et1 > 22 and id1 > 0.78 and iso1 < 0.067 and met < 30 and btag1 < 0.58 and btag2 < 0.01):
                return True
        if (vbfcat == 2):
            if (et1 > 22 and id1 > 0.97 and iso1 < 0.060 and met < 25 and btag1 < 0.62 and btag2 < 0.30):
                return True

    return False

def emuSelectionV3SimplifiedN_1ET1(cat, vbfcat, et1, et2, id1, id2, iso1, iso2, met, btag1, btag2, njets):
    if (id2 != 11):
        return False
    if (njets >= 3):
        return False
    if (vbfcat == -1):
        if (cat == 0 and njets == 0):
            if (et2 > 25 and id1 > 0.800 and iso1 < 0.500 and met < 30):
                return True
        if (cat == 1 and njets == 0):
            if (et2 > 20 and id1 > 0.580 and iso1 < 0.470 and met < 30):
                return True
        if (cat == 2 and njets == 0):
            if (et2 > 20 and id1 > 0.580 and iso1 < 0.470 and met < 30):
                return True
    
        if (cat == 0 and njets == 1):
            if (et2 > 22 and id1 > 0.650 and iso1 < 0.110 and met < 30 and btag1 < 0.38):
                return True
        if (cat == 1 and njets == 1):
            if (et2 > 22 and id1 > 0.680 and iso1 < 0.095 and met < 22 and btag1 < 0.48):
                return True
        if (cat == 2 and njets == 1):
            if (et2 > 22 and id1 > 0.680 and iso1 < 0.095 and met < 22 and btag1 < 0.48):
                return True
    
        if (cat == 0 and njets >= 2):
            if (et2 > 25 and id1 > 0.810 and iso1 < 0.200 and met < 25 and btag1 < 0.38 and btag2 < 0.48):
                return True
        if (cat == 1 and njets >= 2):
            if (et2 > 20 and id1 > 0.690 and iso1 < 0.220 and met < 32 and btag1 < 0.51 and btag2 < 0.57):
                return True
        if (cat == 2 and njets >= 2):
            if (et2 > 20 and id1 > 0.690 and iso1 < 0.220 and met < 32 and btag1 < 0.51 and btag2 < 0.57):
                return True
    else:
        if (vbfcat == 1):
            if (et2 > 22 and id1 > 0.78 and iso1 < 0.067 and met < 30 and btag1 < 0.58 and btag2 < 0.01):
                return True
        if (vbfcat == 2):
            if (et2 > 22 and id1 > 0.97 and iso1 < 0.060 and met < 25 and btag1 < 0.62 and btag2 < 0.30):
                return True

    return False


def emuSelectionV3SimplifiedN_1NJETS(cat, vbfcat, et1, et2, id1, id2, iso1, iso2, met, btag1, btag2, njets):
    if (id2 != 11):
        return False
    if (vbfcat == -1):
        if (cat == 0 and njets == 0):
            if (et1 > 25 and et2 > 25 and id1 > 0.800 and iso1 < 0.500 and met < 30):
                return True
        if (cat == 1 and njets == 0):
            if (et1 > 20 and et2 > 20 and id1 > 0.580 and iso1 < 0.470 and met < 30):
                return True
        if (cat == 2 and njets == 0):
            if (et1 > 20 and et2 > 20 and id1 > 0.580 and iso1 < 0.470 and met < 30):
                return True
    
        if (cat == 0 and njets == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.650 and iso1 < 0.110 and met < 30 and btag1 < 0.38):
                return True
        if (cat == 1 and njets == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.680 and iso1 < 0.095 and met < 22 and btag1 < 0.48):
                return True
        if (cat == 2 and njets == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.680 and iso1 < 0.095 and met < 22 and btag1 < 0.48):
                return True
    
        if (cat == 0 and njets >= 2):
            if (et1 > 25 and et2 > 25 and id1 > 0.810 and iso1 < 0.200 and met < 25 and btag1 < 0.38 and btag2 < 0.48):
                return True
        if (cat == 1 and njets >= 2):
            if (et1 > 20 and et2 > 20 and id1 > 0.690 and iso1 < 0.220 and met < 32 and btag1 < 0.51 and btag2 < 0.57):
                return True
        if (cat == 2 and njets >= 2):
            if (et1 > 20 and et2 > 20 and id1 > 0.690 and iso1 < 0.220 and met < 32 and btag1 < 0.51 and btag2 < 0.57):
                return True
    else:
        if (vbfcat == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.78 and iso1 < 0.067 and met < 30 and btag1 < 0.58 and btag2 < 0.01):
                return True
        if (vbfcat == 2):
            if (et1 > 22 and et2 > 22 and id1 > 0.97 and iso1 < 0.060 and met < 25 and btag1 < 0.62 and btag2 < 0.30):
                return True

    return False



def emuSelectionV3SimplifiedN_1BTAG(cat, vbfcat, et1, et2, id1, id2, iso1, iso2, met, btag1, btag2, njets):
    if (id2 != 11):
        return False
    if (njets >= 3):
        return False
    if (vbfcat == -1):
        if (cat == 0 and njets == 0):
            if (et1 > 25 and et2 > 25 and id1 > 0.800 and iso1 < 0.500 and met < 30):
                return True
        if (cat == 1 and njets == 0):
            if (et1 > 20 and et2 > 20 and id1 > 0.580 and iso1 < 0.470 and met < 30):
                return True
        if (cat == 2 and njets == 0):
            if (et1 > 20 and et2 > 20 and id1 > 0.580 and iso1 < 0.470 and met < 30):
                return True
    
        if (cat == 0 and njets == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.650 and iso1 < 0.110 and met < 30):
                return True
        if (cat == 1 and njets == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.680 and iso1 < 0.095 and met < 22):
                return True
        if (cat == 2 and njets == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.680 and iso1 < 0.095 and met < 22):
                return True
    
        if (cat == 0 and njets >= 2):
            if (et1 > 25 and et2 > 25 and id1 > 0.810 and iso1 < 0.200 and met < 25):
                return True
        if (cat == 1 and njets >= 2):
            if (et1 > 20 and et2 > 20 and id1 > 0.690 and iso1 < 0.220 and met < 32):
                return True
        if (cat == 2 and njets >= 2):
            if (et1 > 20 and et2 > 20 and id1 > 0.690 and iso1 < 0.220 and met < 32):
                return True
    else:
        if (vbfcat == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.78 and iso1 < 0.067 and met < 30):
                return True
        if (vbfcat == 2):
            if (et1 > 22 and et2 > 22 and id1 > 0.97 and iso1 < 0.060 and met < 25):
                return True

    return False

def emuSelectionV3SimplifiedN_1MET(cat, vbfcat, et1, et2, id1, id2, iso1, iso2, met, btag1, btag2, njets):
    if (id2 != 11):
        return False
    if (njets >= 3):
        return False
    if (vbfcat == -1):
        if (cat == 0 and njets == 0):
            if (et1 > 25 and et2 > 25 and id1 > 0.800 and iso1 < 0.500):
                return True
        if (cat == 1 and njets == 0):
            if (et1 > 20 and et2 > 20 and id1 > 0.580 and iso1 < 0.470):
                return True
        if (cat == 2 and njets == 0):
            if (et1 > 20 and et2 > 20 and id1 > 0.580 and iso1 < 0.470):
                return True
    
        if (cat == 0 and njets == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.650 and iso1 < 0.110 and btag1 < 0.38):
                return True
        if (cat == 1 and njets == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.680 and iso1 < 0.095 and btag1 < 0.48):
                return True
        if (cat == 2 and njets == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.680 and iso1 < 0.095 and btag1 < 0.48):
                return True
    
        if (cat == 0 and njets >= 2):
            if (et1 > 25 and et2 > 25 and id1 > 0.810 and iso1 < 0.200 and btag1 < 0.38 and btag2 < 0.48):
                return True
        if (cat == 1 and njets >= 2):
            if (et1 > 20 and et2 > 20 and id1 > 0.690 and iso1 < 0.220 and btag1 < 0.51 and btag2 < 0.57):
                return True
        if (cat == 2 and njets >= 2):
            if (et1 > 20 and et2 > 20 and id1 > 0.690 and iso1 < 0.220 and btag1 < 0.51 and btag2 < 0.57):
                return True
    else:
        if (vbfcat == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.78 and iso1 < 0.067 and btag1 < 0.58 and btag2 < 0.01):
                return True
        if (vbfcat == 2):
            if (et1 > 22 and et2 > 22 and id1 > 0.97 and iso1 < 0.060 and btag1 < 0.62 and btag2 < 0.30):
                return True

    return False


def emuSelectionV3SimplifiedN_1ISO(cat, vbfcat, et1, et2, id1, id2, iso1, iso2, met, btag1, btag2, njets):
    if (id2 != 11):
        return False
    if (njets >= 3):
        return False
    if (vbfcat == -1):
        if (cat == 0 and njets == 0):
            if (et1 > 25 and et2 > 25 and id1 > 0.800 and met < 30):
                return True
        if (cat == 1 and njets == 0):
            if (et1 > 20 and et2 > 20 and id1 > 0.580 and met < 30):
                return True
        if (cat == 2 and njets == 0):
            if (et1 > 20 and et2 > 20 and id1 > 0.580 and met < 30):
                return True
    
        if (cat == 0 and njets == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.650 and met < 30 and btag1 < 0.38):
                return True
        if (cat == 1 and njets == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.680 and met < 22 and btag1 < 0.48):
                return True
        if (cat == 2 and njets == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.680 and met < 22 and btag1 < 0.48):
                return True
    
        if (cat == 0 and njets >= 2):
            if (et1 > 25 and et2 > 25 and id1 > 0.810 and met < 25 and btag1 < 0.38 and btag2 < 0.48):
                return True
        if (cat == 1 and njets >= 2):
            if (et1 > 20 and et2 > 20 and id1 > 0.690 and met < 32 and btag1 < 0.51 and btag2 < 0.57):
                return True
        if (cat == 2 and njets >= 2):
            if (et1 > 20 and et2 > 20 and id1 > 0.690 and met < 32 and btag1 < 0.51 and btag2 < 0.57):
                return True
    else:
        if (vbfcat == 1):
            if (et1 > 22 and et2 > 22 and id1 > 0.78 and met < 30 and btag1 < 0.58 and btag2 < 0.01):
                return True
        if (vbfcat == 2):
            if (et1 > 22 and et2 > 22 and id1 > 0.97 and met < 25 and btag1 < 0.62 and btag2 < 0.30):
                return True

    return False



def emuSelectionV3SimplifiedN_1ID(cat, vbfcat, et1, et2, id1, id2, iso1, iso2, met, btag1, btag2, njets):
    if (id2 != 11):
        return False
    if (njets >= 3):
        return False
    if (vbfcat == -1):
        if (cat == 0 and njets == 0):
            if (et1 > 25 and et2 > 25 and iso1 < 0.500 and met < 30):
                return True
        if (cat == 1 and njets == 0):
            if (et1 > 20 and et2 > 20 and iso1 < 0.470 and met < 30):
                return True
        if (cat == 2 and njets == 0):
            if (et1 > 20 and et2 > 20 and iso1 < 0.470 and met < 30):
                return True
    
        if (cat == 0 and njets == 1):
            if (et1 > 22 and et2 > 22 and iso1 < 0.110 and met < 30 and btag1 < 0.38):
                return True
        if (cat == 1 and njets == 1):
            if (et1 > 22 and et2 > 22 and iso1 < 0.095 and met < 22 and btag1 < 0.48):
                return True
        if (cat == 2 and njets == 1):
            if (et1 > 22 and et2 > 22 and iso1 < 0.095 and met < 22 and btag1 < 0.48):
                return True
    
        if (cat == 0 and njets >= 2):
            if (et1 > 25 and et2 > 25 and iso1 < 0.200 and met < 25 and btag1 < 0.38 and btag2 < 0.48):
                return True
        if (cat == 1 and njets >= 2):
            if (et1 > 20 and et2 > 20 and iso1 < 0.220 and met < 32 and btag1 < 0.51 and btag2 < 0.57):
                return True
        if (cat == 2 and njets >= 2):
            if (et1 > 20 and et2 > 20 and iso1 < 0.220 and met < 32 and btag1 < 0.51 and btag2 < 0.57):
                return True
    else:
        if (vbfcat == 1):
            if (et1 > 22 and et2 > 22 and iso1 < 0.067 and met < 30 and btag1 < 0.58 and btag2 < 0.01):
                return True
        if (vbfcat == 2):
            if (et1 > 22 and et2 > 22 and iso1 < 0.060 and met < 25 and btag1 < 0.62 and btag2 < 0.30):
                return True

    return False


def emuSelection(cat, id1, id2, iso1, iso2, met, btag1, btag2, njets):
    #print cat, id1,id2,iso1,iso2,met,btag1,btag2, njets
    if (cat == 0):

        if (id1 < 0.95):
            return False
        if (iso1 > 0.1):
            return False
        if (met > 40):
            return False
        if (njets >= 3):
            return False
        if (btag1 > 0.4):
            return False
        if (btag2 > 0.4):
            return False
        return True
    elif (cat == 1):
        if (id2 != 11):
            return False
        if (id1 < 0.96):
            return False
        if (iso1 > 0.08):
            return False
        if (met > 35):
            return False
        if (njets >= 3):
            return False
        if (btag1 > 0.35):
            return False
        if (btag2 > 0.35):
            return False
        return True
    elif (cat == 2):
        if (id2 != 11):
            return False
        if (id1 < 0.98):
            return False
        if (iso1 > 0.1):
            return False
        if (met > 30):
            return False
        if (njets >= 2):
            return False
        if (btag1 > 0.35):
            return False
        if (btag2 > 0.35):
            return False
        return True


def getHighestSumPtPairs(nPairs, pairTypes, id1, id2, iso1, iso2, sumpts):
    bestSumpts = [0, 0, 0]
    bestPairs = [-1, -1, -1]
    for p in xrange(nPairs):
        goOn = False
        if (pairTypes[p] == 0):
            if (id1[p] ==11 and id2[p] == 11):
                goOn = True
        elif (pairTypes[p] == 1):
            if (id1[p] > 0.92 and id2[p] > 0.92 and
                iso1[p] < 0.1 and iso2[p] < 0.1):
                goOn = True
        else:
            if (id1[p] > 0.92 and iso1[p] < 0.1 and id2[p] == 11):
                goOn = True
        if (not goOn):
            continue
        if (sumpts[p] > bestSumpts[pairTypes[p]]):
            bestSumpts[pairTypes[p]] = sumpts[p]
            bestPairs[pairTypes[p]] = p

    return bestPairs

def getAllPairs(nPairs, pairTypes, id1, id2, iso1, iso2, eta1, eta2, phi1, phi2, sumpts):
    if (nPairs > 1):
        sortedPairs = sorted(zip(sumpts, range(nPairs)))
        sortedIndices = zip(*sortedPairs)[1]
        leptonList = []
        for p in sortedIndices:
            #goOn = False
            #if (pairTypes[p] == 0):
            #    if (id1[p] > 0 and id2[p] > 0):
            #        goOn = True
            #elif (pairTypes[p] == 1):
            #    if (id1[p] > 0.1 and id2[p] > 0.1 and
            #        iso1[p] < 0.5 and iso2[p] < 0.5):
            #        goOn = True
            #else:
            #    if (id1[p] > 0.1 and iso1[p] < 0.5 and id2[p] > 0):
            #        goOn = True
            #if (not goOn):
            #    continue
            leptonList.append((p,(eta1[p], phi1[p]),(eta2[p], phi2[p])))

        to_remove = []
        for i in xrange(len(leptonList)-1):
            for j in xrange(i+1, len(leptonList)):
                if (leptonList[i][1] == leptonList[j][1] or leptonList[i][1] == leptonList[j][2] 
                    or leptonList[i][2] == leptonList[j][1] or leptonList[i][2] == leptonList[j][2]):
                    to_remove.append(leptonList[j])
        for i in to_remove: 
            if (i in leptonList):
                leptonList.remove(i)
            
        finalList = [p[0] for p in leptonList]
        if (len(finalList) > 1):
            return finalList
        else:
            return []

def tightElectronCharge(ch11, ch21, ch31, ch12, ch22, ch32):
    ch1 = 19
    ch2 = 21
    if ((ch11 == ch21) and (ch11 == ch31)):
        ch1 = ch11
    if ((ch12 == ch22) and (ch12 == ch32)):
        ch2 = ch12

    return (ch1 == ch2)
