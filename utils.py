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
