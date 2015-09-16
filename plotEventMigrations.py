#!/usr/bin/env python

import sys, os

# compare two CSV files and plot migrations of event (weights) between them

#----------------------------------------------------------------------

# if True, print / plot numbers relative to number of events
# before migration
printRelative = True

#----------------------------------------------------------------------

itypeToProcName = {
    -225:  "125 GeV ggh",
    -325:  "125 GeV vbf",
    }

itypeToShortProcName = {
    -225:  "ggh",
    -325:  "vbf",
    }

#----------------------------------------------------------------------

def readFile(fname):
    import csv

    if fname.endswith(".gz"):
        import gzip
        fin = gzip.open(fname)
    else:
        fin = open(fname)

    reader = csv.DictReader(fin)

    # first key is itype,
    # second key is (run,lumi,event)
    # value is the entire line
    retval = {}

    for line in reader:

        for name in ['itype', 'run', 'lumisection', 'event', 'cat']:
            line[name]= int(line[name])

        for name in [ 'weight']:
            line[name] = float(line[name])

        itype = int(line['itype'])
        
        key = (line['run'], line['lumisection'], line['event'])

        if not retval.has_key(itype):
            retval[itype] = {}

        assert not retval[itype].has_key(key)

        retval[itype][key] = line

    return retval


#----------------------------------------------------------------------

def countEventsPerCat(allCats, data):
    numEvents = dict( [ (cat, 0.) for cat in allCats ])

    for line in data.values():
        numEvents[line['cat']] += line['weight']

    return numEvents
    

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser("""

      usage: %prog [options] itype before.csv after.csv

      plots category migration when changing from before.csv to after.csv

    """
    )

    parser.add_option("-o",
                      dest = "outputFile",
                      type = str,
                      default = None,
                      help="file where the save the plot to",
                      )

    (options, ARGV) = parser.parse_args()

    #----------------------------------------

    assert len(ARGV) == 3

    itype = int(ARGV.pop(0))

    procName = itypeToProcName.get(itype,"itype=" + str(itype))

    fnames = ARGV

    datas = [ readFile(fname) for fname in fnames ]

    for data, fname in zip(datas, ARGV):
        if not data.has_key(itype):
            print >> sys.stderr,"no events for itype=",itype,"found in",fname
            sys.exit(1)

    datas = [ data[itype] for data in datas ]

    keys = [ set(data.keys()) for data in datas ]

    # get a list of all categories
    allCats = sorted(set( [ line['cat'] for line in data.values() for data in datas ]))

    #----------
    # count number of events (per category) before
    #----------

    numEventsBefore = countEventsPerCat(allCats, datas[0])
    numEventsAfter  = countEventsPerCat(allCats, datas[1])

    #----------
    # find events common to both (category migration or stayed within category)
    #----------
    if True:
        commonKeys = keys[0].intersection(keys[1])

        # first key is original category, second key is destination
        # category when going from 1 -> 2
        migrationMatrix = dict( [ (srcCat,
                                   dict([ (destCat, 0.) for destCat in allCats ]))
                                  for srcCat in allCats ])

        for key in commonKeys:
            srcCat  = datas[0][key]['cat']
            destCat = datas[1][key]['cat']

            srcWeight = datas[0][key]['weight']
            destWeight = datas[1][key]['weight']

            if srcWeight != destWeight:
                print >> sys.stderr,"warning: srcWeight=%f destWeight=%f (%+.1f%%)" % (srcWeight, destWeight, (destWeight - srcWeight) / srcWeight * 100)

            migrationMatrix[srcCat][destCat] += 0.5 * (srcWeight + destWeight)

    #----------
    # find keys only one of the two (these dropped out / came in; no category migration)
    #----------
    if True:
        keysOnlyIn = [ keys[0] - keys[1], keys[1] - keys[0] ]

        # sum of weights going to 'from nowhere' when going from 1 -> 2    
        # key is the category
        goingOut = dict([ (cat, 0.0) for cat in allCats ])

        for key in keysOnlyIn[0]:
            cat    = datas[0][key]['cat']        
            weight = datas[0][key]['weight']

            goingOut[cat] += weight

        # sum of weights coming in 'from nowhere' when going from 1 -> 2    
        # key is the category
        comingIn = dict([ (cat, 0.0) for cat in allCats ])

        for key in keysOnlyIn[1]:
            cat    = datas[1][key]['cat']        
            weight = datas[1][key]['weight']

            comingIn[cat] += weight


    #----------
    # calculate and print results
    #----------
    import numpy

    # matrix to plot 
    matrixToPlot = numpy.zeros((len(allCats), len(allCats) + 3))

    print "category migrations",fname,"->",fname


    parts = [ "in" ] + [ "%8s" % ("cat%d" % cat) for cat in allCats ] + [ "out", "total change" ]
    print "dest:    | " + " | ".join([ "%8s" % part for part in parts])

    print "src cat"

    for srcCatIndex, srcCat in enumerate(allCats):

        print "%8s |" % ("cat%d" % srcCat),

        if printRelative:
            value = comingIn[srcCat] / numEventsBefore[srcCat] * 100
            parts = [ "%.1f%%" % value ]
        else:
            value = comingIn[srcCat]
            parts = [ "%.2f" %  value ]

        matrixToPlot[srcCatIndex, 0] = value

        for destCatIndex, destCat in enumerate(allCats):
            # the category X to category Y matrix

            if printRelative:
                if srcCat == destCat:
                    # diagonal: how many events stay in the same category
                    value = migrationMatrix[srcCat][destCat] / numEventsBefore[srcCat] * 100
                else:
                    # off-diagonal

                    netChange = sum([
                        # going out of this category
                        - migrationMatrix[srcCat][destCat],

                        # coming in from another category
                        + migrationMatrix[destCat][srcCat]

                        ])
                    value = netChange / numEventsBefore[srcCat] * 100


                # print the net relative change and also put it into the matrix
                # (for the color plot)

                parts.append("%.1f%%" % value)


            else:
                value = migrationMatrix[srcCat][destCat]
                parts.append("%.2f" % value)

            matrixToPlot[srcCatIndex, 1 + destCatIndex] = value

        # change in number of events
        totalChange = numEventsAfter[srcCat] - numEventsBefore[srcCat]

        if printRelative:
            value1 = goingOut[srcCat] / numEventsBefore[srcCat] * 100
            parts.append("%.1f%%" % value1)

            value2 = (totalChange / numEventsBefore[srcCat] * 100)
            parts.append("%+.1f%%" % value2)
        else:
            value1 = goingOut[srcCat]
            parts.append("%.2f" % value1)

            value2 = totalChange
            parts.append("%+.2f" % value2)

        matrixToPlot[srcCatIndex, 1 + len(allCats)] = value1
        matrixToPlot[srcCatIndex, 2 + len(allCats)] = value2

        print " | ".join([ "%8s" % part for part in parts])

    #----------
    # plot
    #----------

    import pylab
    pylab.figure(facecolor='white', figsize=(13,10))
    pylab.imshow(matrixToPlot, 
                 cmap=pylab.cm.Blues,
                 interpolation='nearest',
                 )

    # print the numbers on the plot
    assert len(allCats) == matrixToPlot.shape[0]
    for i,srcCat in zip(range(matrixToPlot.shape[0]), allCats):
        for j in xrange(matrixToPlot.shape[1]):

            if j >= 1 and j < 1 + len(allCats):
                destCat = j - 1
            else:
                destCat = None


            # special labels for relative mode
            if printRelative:
                if j == i + 1:
                    # the 'diagonal'
                    # what fraction of events stay in this category
                    text = "%.1f%%" % matrixToPlot[i][j]
                elif j == 0 or j == 1 + len(allCats):
                    # the 'in' or 'out' columns
                    text = "%.1f%%" % matrixToPlot[i][j]

                elif j == 2 + len(allCats):
                    # the 'change' column
                    text = "%+.1f%%" % matrixToPlot[i][j]

                else:
                    # a 'catX vs. catY' block
                    # what fraction goes out of this category
                    text = "%.1f%% out" % (migrationMatrix[srcCat][destCat] / numEventsBefore[srcCat] * 100)

                    # what fraction (relative to the original
                    # number of events in srcCat)
                    if destCat != None:
                        text += "\n%.1f%% in" % (migrationMatrix[destCat][srcCat] / numEventsBefore[srcCat] * 100)


            else:
                # absolute number of events
                text = "%.1f" % matrixToPlot[i][j]

            pylab.gca().annotate(text,

                                 xy=(j, i), 
                                 horizontalalignment='center',
                                 verticalalignment='center',
                                 fontsize = 10,
                                 )

    pylab.yticks(range(len(allCats)), [ 'cat%d' % cat for cat in allCats])

    xlabels = [ "in" ] + [ 'cat%d' % cat for cat in allCats] + [ "out", "change" ]
    pylab.xticks(range(len(xlabels)), xlabels)

    pylab.ylabel('category before')
    # pylab.xlabel('category after')
    pylab.title("%s -> %s (%s)" % tuple([os.path.splitext(fname)[0] for fname in fnames] + [ procName ]))


    if options.outputFile != None:
        pylab.savefig(options.outputFile)
    else:
        # assume we run interactively
        pylab.show()
