#!/usr/bin/env python

#----------------------------------------------------------------------
def makeGaussianVarname(varname, proc, mhyp, catname, gaussIndex):
    # produces a variable name related to a Gaussian pdf
    # which includes the process, mass hypothesis, category
    # and index of the Gaussian
    #
    # put into one function to have consistent naming across tools
    #
    # any of the elements can be none (e.g. mhyp), the corresponding part
    # is then not include in the variable name 


    if gaussIndex != None:
        gaussIndex = "g%d" % gaussIndex

    parts = [ str(item) for item in [
                varname,
                gaussIndex,
                proc,
                mhyp,
                catname,
              ]    

              if item != None
              ]

    return "_".join(parts)
    

#----------------------------------------------------------------------

def makePiecewiseLinearFunction(funcName, xvar, xvalues, yvalues):
    # creates a RooFormulaVar with an expression for a
    # piecewise linear function

    numPoints = len(xvalues)

    assert numPoints == len(yvalues)

    assert numPoints >= 2

    # sort indices such that xvlaues are sorted in ascending order
    indices = range(numPoints)
    indices.sort(key = lambda index: xvalues[index])

    parts = []

    # below the leftmost point, the function keeps
    # the value of the leftmost point
    parts.append("(@0 < %f) * %f" % (xvalues[indices[0]],
                                     yvalues[indices[0]]))

    for pos in range(1, numPoints):
        xleft = xvalues[indices[pos-1]]
        yleft = yvalues[indices[pos-1]]

        xright = xvalues[indices[pos]]
        yright = yvalues[indices[pos]]

        slope = (yright - yleft) / float(xright - xleft)

        condition = "(@0 >= %f && @0 < %f)" % (xleft, xright)
        
        parts.append("%s * (%f + (@0 - %f) * %f)" % (
            condition,
            yleft,
            xleft,
            slope))

    # beyond the rightmost point, the function again keeps
    # the value of the rightmost point
    
    parts.append("(@0 >= %f) * %f" % (xvalues[indices[-1]],
                                      yvalues[indices[-1]]))


    formula = " + ".join(parts)

    import ROOT
    return ROOT.RooFormulaVar(funcName,funcName,
                              formula,
                              ROOT.RooArgList(xvar))


#----------------------------------------------------------------------

def getObj(ws, name):

    retval = ws.obj(name)

    if retval == None:
        print >> sys.stderr,"could not get object '%s' from workspace '%s', exiting" % (name, ws.GetName())
        sys.exit(1)

    return retval

#----------------------------------------------------------------------

def getCatEntries(catvar):
    # catvar should e.g. be a RooCategory object

    retval = []

    oldIndex = catvar.getIndex()

    for index in range(catvar.numTypes()):
        catvar.setIndex(index)
        retval.append(catvar.getLabel())

    catvar.setIndex(oldIndex)

    return retval

#----------------------------------------------------------------------

def expandContinuedFraction(fvalues):
    # 'expands' a continued fraction: given n values in the range 0..1
    # returns n+1 values in the range 0..1 which sum to one

    retval = []
    accumulatedFactor = 1.0

    for fval in fvalues:
        retval.append(fval * accumulatedFactor)

        accumulatedFactor *= (1 - fval)

    retval.append(accumulatedFactor)

    return retval

#----------------------------------------------------------------------

def collapseContinuedFraction(fvalues):
    # 'de-expands' a continued fraction: given n values in the range 0..1
    # which sum to 1, returns n-1 values in the range 0..1 which represent
    # the same values as continued fraction. This is the counterpart to
    # expandContinuedFraction(..)

    assert len(fvalues) >= 1

    retval = []
    accumulatedFactor = 1.0

    # we can ignore the last value, assuming it is
    # the complement of the sum of the previous values
    # to one

    for fval in fvalues[:-1]:
        retval.append(fval / accumulatedFactor)

        accumulatedFactor *= (1 - retval[-1])

    return retval

#----------------------------------------------------------------------
