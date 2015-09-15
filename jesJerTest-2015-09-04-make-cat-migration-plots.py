#!/usr/bin/env python

import sys, os

scriptDir = os.path.abspath(os.path.dirname(__file__))

# jet energy scale
# ../data/2015-07-01-hemu_jet_syst_jec_up.root   $OUTDIR/jes-up.root   
# ../data/2015-07-01-hemu_jet_syst_jec_down.root $OUTDIR/jes-down.root 
# ../data/2015-07-01-hemu_jet_syst_jec_no.root   $OUTDIR/nominal.root  

for itype in (
    -225,
    # -325
    ):

    for mode in [ 'jes', 'jer']:

        for src, dest in (
            [ 'nominal', mode + '-up-met-fixed' ],
            [ mode + '-up-met-fixed',  mode + '-up'],
            ):
            

            cmdParts = [
                os.path.join(scriptDir,"plotEventMigrations.py"),
                '-o "' + "-".join([
                'cat-migration',
                mode,
                src,
                "to",
                dest
                ]) + 'cat{cat}-{proc}.png"',
                '--',
                str(itype),
                src + '.csv',
                dest + '.csv',
                ]

            cmd = " ".join(cmdParts)
            
            print "cmd=",cmd
            res = os.system(cmd)
            
            assert res == 0
        
