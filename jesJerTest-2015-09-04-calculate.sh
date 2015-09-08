#!/bin/bash
# set -x
INPUTDIR=2015-09-04-jes-jer-test


OPTIONS=""
# OPTIONS="--format csv-numevents"
OPTIONS="--format csv-numentries --unbinned"


#----------
echo JES: jet energies and MET shifted
#----------
./calcJESJERsystematics.py $OPTIONS $INPUTDIR/nominal.root \
                           $INPUTDIR/jes-up.root   \
                           $INPUTDIR/jes-down.root  

echo
#----------
echo JES: jet energies shifted but MET unshifted
#----------
./calcJESJERsystematics.py $OPTIONS $INPUTDIR/nominal.root \
                           $INPUTDIR/jes-up-met-fixed.root   \
                           $INPUTDIR/jes-down-met-fixed.root


echo
#----------
echo JER: jet energies and MET shifted
#----------
./calcJESJERsystematics.py $OPTIONS $INPUTDIR/nominal.root \
                           $INPUTDIR/jer-up.root \
                           $INPUTDIR/jer-down.root

echo
#----------
echo JER: jet resolution shifted but MET unshifted
#----------
./calcJESJERsystematics.py $OPTIONS $INPUTDIR/nominal.root \
                           $INPUTDIR/jer-up-met-fixed.root \
                           $INPUTDIR/jer-down-met-fixed.root
