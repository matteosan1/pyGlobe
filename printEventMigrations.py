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

    for destCat in allCats:
        if destCat == sourceCat:
            print "  events remaining in cat",sourceCat,":"
        else:
            print "  events moving from", sourceCat, "in", fnames[0], "to", destCat, "in", fnames[1], ":"

        for key in migrationMatrix[sourceCat][destCat]:
            print "   ",key

        print
    
    #----------
    # find keys only one of the two (these dropped out / came in; no category migration)
    #----------
    keysOnlyIn = [ keys[0] - keys[1], keys[1] - keys[0] ]

    for fileIndex, (fname, keys) in enumerate(zip(fnames, keysOnlyIn)):

        print "events only in",fname,

        if fileIndex == 0:
            print "(going out)"
        else:
            print "(coming in)"

        keys = sorted(keys)

        for key in keys:

            cat = datas[fileIndex][key]['cat']

            if cat == sourceCat:
                print "   ",key
    
