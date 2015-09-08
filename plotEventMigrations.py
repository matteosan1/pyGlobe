#!/usr/bin/env python

import sys

# compare two CSV files and plot migrations of event (weights) between them

#----------------------------------------------------------------------

# if True, print / plot numbers relative to number of events
# before migration
printRelative = True

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

ARGV = sys.argv[1:]

assert len(ARGV) == 3

# -225 for 125 GeV ggh
# -325 for 125 VBF
itype = int(ARGV.pop(0))

datas = [ readFile(fname) for fname in ARGV ]

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
# print results
#----------

print "category migrations",fname,"->",fname


parts = [ "in" ] + [ "%8s" % ("cat%d" % cat) for cat in allCats ] + [ "out", "total change" ]
print "dest:    | " + " | ".join([ "%8s" % part for part in parts])

print "src cat"

for srcCat in allCats:

    print "%8s |" % ("cat%d" % srcCat),

    if printRelative:
        parts = [ "%.1f%%" % (comingIn[srcCat] / numEventsBefore[srcCat] * 100) ]
    else:
        parts = [ "%.2f" % comingIn[srcCat] ]

    for destCat in allCats:
        if printRelative:
            parts.append("%.1f%%" % (migrationMatrix[srcCat][destCat] / numEventsBefore[srcCat] * 100))
        else:
            parts.append("%.2f" % migrationMatrix[srcCat][destCat])

    # change in number of events
    totalChange = numEventsAfter[srcCat] - numEventsBefore[srcCat]

    if printRelative:
        parts.append("%.1f%%" % (goingOut[srcCat] / numEventsBefore[srcCat] * 100))
        parts.append("%+.1f%%" % (totalChange / numEventsBefore[srcCat] * 100))
    else:
        parts.append("%.2f" % goingOut[srcCat])
        parts.append("%+.2f" % totalChange)
        
    print " | ".join([ "%8s" % part for part in parts])


