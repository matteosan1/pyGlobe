#!/bin/bash

# stop script on first error
set -e

# step 1 would be:
# fill the MC and data datasets
# ./pyGlobe.py -i ../data/emu_merged_v8.root -o emu_output_v5.root --wsout workspace-raw-unblinded.root

# build the signal model
./fitSignal.py --simultaneous --scalesig 0.01 workspace-raw-unblinded.root /tmp/ws2.root

# fix the signal model
./fixSignalModel.py /tmp/ws2.root /tmp/ws3.root 

# build the background model (needs RooPower from CMSSW, so done as last step)
./fitBackground.py parameters/bgfunc.py /tmp/ws3.root workspace-nominal-nonblind.root

