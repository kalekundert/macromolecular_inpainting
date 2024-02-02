#!/usr/bin/env bash
set -euo pipefail

rsync -av \
  o2-cp:research/projects/202305_macromol_inpaint/notebook/evaluate_fine_tuning/first_try/ \
  .

