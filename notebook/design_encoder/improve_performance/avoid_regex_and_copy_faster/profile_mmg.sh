#!/usr/bin/env sh

set -x

./profile_mmg.py advanced 16A 2> advanced.mmvox-numpy.16A.prof
./profile_mmg.py advanced 24A 2> advanced.mmvox-numpy.24A.prof
./profile_mmg.py simple 16A 2> simple.mmvox-numpy.16A.prof
./profile_mmg.py simple 24A 2> simple.mmvox-numpy.24A.prof
