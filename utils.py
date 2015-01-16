#!/usr/bin/env python

#----------------------------------------------------------------------
def makeGaussianVarname(varname, proc, mhyp, catname, gaussIndex):
    # produces a variable name related to a Gaussian pdf
    # which includes the process, mass hypothesis, category
    # and index of the Gaussian
    #
    # put into one function to have consistent naming across tools

    return "_".join([
        varname,
        "g%d" % gaussIndex,
        proc,
        str(mhyp),
        catname,
        ])
    

#----------------------------------------------------------------------
