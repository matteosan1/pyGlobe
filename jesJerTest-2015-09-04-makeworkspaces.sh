#!/bin/bash

# commands adapted from ../make-jes-jer-workspaces.sh

set -x

OUTDIR=2015-09-04-jes-jer-test

#----------
# JES: jet energies and MET shifted
#----------
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jec_up.root   -o emu_output_v5.root --blind --wsout $OUTDIR/jes-up.root    
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jec_down.root -o emu_output_v5.root --blind --wsout $OUTDIR/jes-down.root  
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jec_no.root -o emu_output_v5.root --blind --wsout   $OUTDIR/nominal.root

#----------
# JES: jet energies shifted but MET unshifted
#----------
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jec_up.root   -o emu_output_v5.root --blind --wsout $OUTDIR/jes-up-met-fixed.root    --metfile ../data/2015-07-01-hemu_jet_syst_jec_no.root
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jec_down.root -o emu_output_v5.root --blind --wsout $OUTDIR/jes-down-met-fixed.root  --metfile ../data/2015-07-01-hemu_jet_syst_jec_no.root

#----------
# JER: jet energies and MET shifted
#----------
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jer_up.root   -o emu_output_v5.root --blind --wsout $OUTDIR/jer-up.root
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jer_down.root -o emu_output_v5.root --blind --wsout $OUTDIR/jer-down.root

#----------
# JER: jet resolution shifted but MET unshifted
#----------

python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jer_up.root   -o emu_output_v5.root --blind --wsout $OUTDIR/jer-up-met-fixed.root    --metfile ../data/2015-07-01-hemu_jet_syst_jec_no.root
python pyGlobe.py -i ../data/2015-07-01-hemu_jet_syst_jer_down.root -o emu_output_v5.root --blind --wsout $OUTDIR/jer-down-met-fixed.root  --metfile ../data/2015-07-01-hemu_jet_syst_jec_no.root


