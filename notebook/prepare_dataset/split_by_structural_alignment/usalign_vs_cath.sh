#!/usr/bin/env bash
set -euo pipefail

# Takes 10 min to run on my laptop.

/home/kale/research/software/forks/USalign/USalign \
  1wka.cif \
  -dir2 ~/research/databases/cath_sandbox/dompdb \
  ~/research/databases/cath_sandbox/dompdb.list \
  -outfmt 2 -mm 0 -ter 1
