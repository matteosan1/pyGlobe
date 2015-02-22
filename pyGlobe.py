#!/usr/bin/env python

import analysis
from optparse import OptionParser
import cProfile

def main(options):
    ana = analysis.Analysis(options)
    ana.Run()

if __name__ == "__main__":  
    parser = OptionParser()
    parser.add_option("-b", "--blind", default=False, action="store_true", help="Do not plot data")
    parser.add_option("-i", "--input", default="~/sslept_v3.root", help="Input filename")
    parser.add_option("-o", "--output", default="output_sslept.root", help="Output filename")
    parser.add_option("--wsout", default="workspace.root", help="Output filename for workspace file", dest = "wsoutFname")
    parser.add_option("-I", "--inputfile", default="inputfiles.dat", help="Original inputfiles.dat")
    parser.add_option("-P", "--plotvariables", default="plotvariables.dat", help="Plot definition file")
    parser.add_option("-t", "--treename", default="opttree", help="Name of the tree to process")
    parser.add_option("-m", "--mode", default="highestSumpt", help="Selection mode (highestSumpt, allPairs...)")
    parser.add_option("-d", "--debug", action="store_true", default=False, help="Activate profiling of the program.")
    parser.add_option("--jes", dest = "jesMode", choices = [ None, "up", "down"], default = None, help="run with shifted jet energy scale (for systematics)")
    parser.add_option("--sigonly", default = False, action="store_true", help="run only over signal events (useful for speeding up testing)")
    parser.add_option("--pdfindex",
                      default = 0,
                      type = int,
                      help="multiply the event weights by pdf_weights[i]/pdf_weights[0] where i is given by this option. Useful for determining PDF uncertainties")

    (options, arg) = parser.parse_args()
        
    if (options.debug):
        cProfile.run("main(options)")
    else:
        main(options)
