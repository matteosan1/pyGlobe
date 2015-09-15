#!/usr/bin/env python

import sys, os

scriptDir = os.path.abspath(os.path.dirname(__file__))

# jet energy scale
# ../data/2015-07-01-hemu_jet_syst_jec_up.root   $OUTDIR/jes-up.root   
# ../data/2015-07-01-hemu_jet_syst_jec_down.root $OUTDIR/jes-down.root 
# ../data/2015-07-01-hemu_jet_syst_jec_no.root   $OUTDIR/nominal.root  

for itype, cats in (
    [-225, [0,1,2,3,4,5,6,7,8 ]],
    [-325, [9,10]]):

    for mode in [ 'jec', 'jer']:
        cmdParts = [
            "../compareJetEnergies.py",
            '-o "jet-energies-' + mode + '-cat{cat}-{proc}.png"',
            "--cats " + ",".join([ str(x) for x in cats]),
            '--',
            str(itype),
            'nominal.csv',
            os.path.join(scriptDir, '../data/2015-07-01-hemu_jet_syst_jec_no.root'),
            os.path.join(scriptDir, '../data/2015-07-01-hemu_jet_syst_%s_up.root' % mode),
            ]

        cmd = " ".join(cmdParts)

        print "cmd=",cmd
        res = os.system(cmd)

        assert res == 0
        
