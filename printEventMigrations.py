#!/usr/bin/env python

# prints number of events which are different in a given itype and category for the two given input files

import plotEventMigrations

#----------------------------------------------------------------------
# main
#----------------------------------------------------------------------

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser("""

      usage: %prog [options] itype cat before.csv after.csv

      plots category migration when changing from before.csv to after.csv

    """
    )

    (options, ARGV) = parser.parse_args()

    #----------------------------------------

    assert len(ARGV) == 4

    itype = int(ARGV.pop(0))
    sourceCat = int(ARGV.pop(0))

    # procName = itypeToProcName.get(itype,"itype=" + str(itype))

    fnames = ARGV

    datas = [ plotEventMigrations.readFile(fname) for fname in fnames ]

    for data, fname in zip(datas, ARGV):
        if not data.has_key(itype):
            print >> sys.stderr,"no events for itype=",itype,"found in",fname
            sys.exit(1)

    # select itype
    datas = [ data[itype] for data in datas ]

    for fname, data in zip(fnames, datas):
        events = [ line for line in data.values() if line['cat'] == sourceCat ] 
        print "%.1f (%d MC) events in %s" % (
            sum([ line['weight'] for line in events ]),
            len(events),
            fname)

    print
    
    # select by category: find those events which were or will be in sourceCat
    ### datas = [
    ###     dict([ (key,line) for key,line in data.items() if line['cat'] == cat ])
    ###     for data in datas ]

    keys = [ set(data.keys()) for data in datas ]

    # get a list of all categories
    allCats = sorted(set( [ line['cat'] for line in data.values() for data in datas ]))

    #----------
    # find events common to both (category migration or stayed within category)
    #----------

    commonKeys = sorted(keys[0].intersection(keys[1]))

    # first key is original category, second key is destination
    # category when going from 1 -> 2
    # value is the (run,lumisection,event) tuple
    migrationMatrix = dict( [ (srcCat,
                               dict([ (destCat, []) for destCat in allCats ]))
                              for srcCat in allCats ])

    for key in commonKeys:
        srcCat  = datas[0][key]['cat']
        destCat = datas[1][key]['cat']

        migrationMatrix[srcCat][destCat].append(key)

    print "common events:"

    #----------
    # print the full matrix, including events moving into the category
    #----------
    def printMigration(srcCat, destCat):
        # sourceCat is the category specified by on the command line

        if destCat == srcCat:
            print "  events remaining in cat",srcCat,
        else:
            print "  events moving from cat", srcCat, "in", fnames[0], "to cat", destCat, "in", fnames[1],

        # take weights from the first file
        events = [ datas[0][key] for key in migrationMatrix[srcCat][destCat] ]
        print "(%.1f, %d MC):" % (sum([line['weight'] for line in events]), len(events))

        for key in migrationMatrix[srcCat][destCat]:
            print "   ",key

        print


    #----------
    # first print events going out of the specified category
    #----------

    print "  migrating out of cat",sourceCat
    print
    for destCat in allCats:
        if destCat != sourceCat:
            printMigration(sourceCat, destCat)

    printMigration(sourceCat, sourceCat)

    print "  migrating out of cat",sourceCat
    print

    for srcCat in allCats:
        if srcCat != sourceCat:
            printMigration(srcCat, sourceCat)

    #----------
    # find keys only one of the two (these dropped out / came in; no category migration)
    #----------
    keysOnlyIn = [ keys[0] - keys[1], keys[1] - keys[0] ]

    for fileIndex, (fname, keys) in enumerate(zip(fnames, keysOnlyIn)):

        #----------

        sumWeights = 0.
        thisKeys = []
        for key in keys:

            line = datas[fileIndex][key]

            cat = line['cat']

            if cat == sourceCat:
                thisKeys.append(key)

                sumWeights += line['weight']

        thisKeys.sort()

        #----------

        print "events only in",fname,

        if fileIndex == 0:
            print "(going out)",
        else:
            print "(coming in)",

        print "(%.1f, %d MC):" % (sumWeights, len(thisKeys))

        #----------
        for key in thisKeys:

            print "   ",key
    
