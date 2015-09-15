#!/bin/bash

# commands adapted from ../make-jes-jer-workspaces.sh

set -x

OUTDIR=2015-09-04-jes-jer-test

#----------
# JES: jet energies and MET shifted
#----------
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jec_up.root   -o emu_output_v5.root --blind --wsout $OUTDIR/jes-up.root    --eventlist $OUTDIR/jes-up.csv
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jec_down.root -o emu_output_v5.root --blind --wsout $OUTDIR/jes-down.root  --eventlist $OUTDIR/jes-down.csv
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jec_no.root -o emu_output_v5.root --blind --wsout   $OUTDIR/nominal.root   --eventlist $OUTDIR/nominal.csv

#----------
# JES: jet energies shifted but MET unshifted
#----------
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jec_up.root   -o emu_output_v5.root --blind --wsout $OUTDIR/jes-up-met-fixed.root    --metfile ../data/2015-07-01-hemu_jet_syst_jec_no.root --eventlist $OUTDIR/jes-up-met-fixed.csv
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jec_down.root -o emu_output_v5.root --blind --wsout $OUTDIR/jes-down-met-fixed.root  --metfile ../data/2015-07-01-hemu_jet_syst_jec_no.root --eventlist $OUTDIR/jes-down-met-fixed.csv

#----------
# JER: jet resolution and MET shifted
#----------
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jer_up.root   -o emu_output_v5.root --blind --wsout $OUTDIR/jer-up.root    --eventlist $OUTDIR/jer-up.csv 
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jer_down.root -o emu_output_v5.root --blind --wsout $OUTDIR/jer-down.root  --eventlist $OUTDIR/jer-down.csv 

#----------
# JER: jet resolution shifted but MET unshifted
#----------

python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jer_up.root   -o emu_output_v5.root --blind --wsout $OUTDIR/jer-up-met-fixed.root    --metfile ../data/2015-07-01-hemu_jet_syst_jec_no.root --eventlist $OUTDIR/jer-up-met-fixed.csv 
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jer_down.root -o emu_output_v5.root --blind --wsout $OUTDIR/jer-down-met-fixed.root  --metfile ../data/2015-07-01-hemu_jet_syst_jec_no.root --eventlist $OUTDIR/jer-down-met-fixed.csv 


