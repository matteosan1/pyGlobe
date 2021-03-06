#!/usr/bin/env python

import helpers

import ROOT

ROOT.gROOT.LoadMacro("SFlightFuncs_EPS2013.C++")

#----------------------------------------------------------------------

def getEtaRange(tagger, workingPoint, eta):
    # returns the eta range for this tagger
    # note that the eta ranges are different for the different working points
    # 
    # we only need L and M here

    eta = abs(eta)

    assert tagger == 'CSV' # rest is not implemented

    if workingPoint == 'L':
        boundaries = [ 0.0, 0.5, 1.0, 1.5, 2.4 ]
    elif workingPoint == 'M':
        boundaries = [  0.0, 0.8, 1.6, 2.4 ]
    elif workingPoint == 'T':
        boundaries = [ 0.0, 2.4 ]
    else:
        assert False

    for i in range(len(boundaries) - 1):
        if eta >= boundaries[i] and eta < boundaries[i+1]:
            return (boundaries[i], boundaries[i+1])

    raise Exception("abs eta " + str(eta) + " outside scale factor acceptance")

#----------------------------------------------------------------------

def getSignalWeightFactorHelper(pts, etas, btags, btagCuts, wps, systType):
    # wps are the working points to try
    # for all categories (except 9), this is normally [ ... ['L', 'M'] .. ]
    # for cat 9 we set wps2 to  [ ... , ['L']  ] because the cut is exactly
    # on the medium working point

    tagger = "CSV"

    # first index is the jet index, second index is the working point
    etaRanges = []

    # we assume that we only have light (non-b and non-c) jets
    numJets = len(pts)

    passesTag = [ btag >= btagCut for btag, btagCut in zip(btags, btagCuts) ]

    # list of weight factors under all possible combinations
    values = []

    # same but with potentially a systematic shift applied 
    valuesShifted = []

    # note that we should fully correlate the errors
    # on the scale factors of the two jets
    #
    # assume that 'max' and 'min' are absolute
    # (in fact, 'min' seems to be above 1 at 20 GeV for an example)
    # i.e. no need to add to / subtract from the mean value

    if systType == 'mean':
        funcName = 'mean'
    elif systType == 'up':
        funcName = 'max'
    elif systType == 'down':
        funcName = 'min'
    else:
        assert False

    # loop over combinations of working points
    import itertools
    for thisWorkingPoints in itertools.product(*wps):

        # get the scale factors for the jets
        scaleFactors = [ ]

        # scale factor after shifting systematic uncertainty
        scaleFactorsShifted = []

        for i in range(numJets):

            # note that we only need to calculate the product
            # of factors (1 - SF[i]) for the jets i which
            # pass the btag cut

            if not passesTag[i]:
                scaleFactors.append(1)
                continue

            # jet passes btag cut
            thisWp = thisWorkingPoints[i]

            # returns the eta range for this tagger and working point for the given jet
            etaRange = getEtaRange(tagger, thisWp, etas[i])

            # get the mean value (for deciding which point to take)
            func = ROOT.GetSFLight("mean", # meanminmax, 
                                   tagger, 
                                   thisWp, # TaggerStrength, 
                                   etaRange[0], etaRange[1], # Etamin, Etamax, 
                                   "2012", # DataPeriod -- not used ?! 
                                   )
            # evaluate the function at the given pt
            # (they seem to start at pt = 20 GeV)
            scaleFactors.append(func.Eval(pts[i]))

            # get the value with uncertainty moved
            func = ROOT.GetSFLight(funcName, # meanminmax, 
                                   tagger, 
                                   thisWp, # TaggerStrength, 
                                   etaRange[0], etaRange[1], # Etamin, Etamax, 
                                   "2012", # DataPeriod -- not used ?! 
                                   )

            scaleFactorsShifted.append(func.Eval(pts[i]))


        # now calculate w(0|number of tagged jets)
        # by taking the product of scaleFactors
        import operator

        values.append(reduce(operator.__mul__, scaleFactors, 1))
        valuesShifted.append(reduce(operator.__mul__, scaleFactorsShifted, 1))

    # end of loop over combinations of working points

    # be conservative: return the minimum over all possible
    #                  working point combinations for THIS event
    # 
    # we could be a bit less conservative by trying a fixed
    # set of working points globally, apply it to ALL EVENTS
    # (e.g. at 125 GeV) and only then take the minimum
    # (which will give a larger average scaling factor)
    #
    # use values to find the minimum scale factor
    # return the corresponding value in valuesShifted
    minPos = min(zip(values, range(len(values))))[1]

    return valuesShifted[minPos]

#----------------------------------------------------------------------

def getSignalWeightFactor(lepCat, vbfCat, njets, pts, etas, btags, systType):
    # find the cut values

    workingPointsToTest = [ [ 'L', 'M' ], [ 'L', 'M' ]]

    pts = pts[:njets]
    etas = etas[:njets]
    btags = btags[:njets]

    workingPointsToTest = [ [ 'L', 'M' ], [ 'L', 'M' ]][:njets]

    if (vbfCat == -1):
        # inclusive categories
        btagCuts = helpers.emuSelectionV3Simplified_inclCatBtagCuts[njets][lepCat]

    else:
        # VBF categories
        btagCuts = helpers.emuSelectionV3Simplified_vbfCatBtagCuts[vbfCat]

        # special treatment for working points
        if vbfCat == 1:
            # cat9
            workingPointsToTest = [ [ 'L', 'M' ], [ 'L' ]]

    return getSignalWeightFactorHelper(pts, etas, btags, btagCuts, workingPointsToTest, systType)
    
    
