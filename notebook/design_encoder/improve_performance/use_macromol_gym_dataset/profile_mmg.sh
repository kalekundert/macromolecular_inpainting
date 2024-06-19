#!/usr/bin/env sh

set -x

./profile_mmg.py advanced 16A 2> advanced.with-index.16A.prof
./profile_mmg.py advanced 24A 2> advanced.with-index.24A.prof
./profile_mmg.py simple 16A 2> simple.with-index.16A.prof
./profile_mmg.py simple 24A 2> simple.with-index.24A.prof
