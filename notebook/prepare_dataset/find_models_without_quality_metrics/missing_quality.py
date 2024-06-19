#!/usr/bin/env python3

import os
import numpy as np
import polars as pl

from gemmi.cif import read_file as read_cif
from scipy.optimize import milp, Bounds, LinearConstraint
from more_itertools import duplicates_everseen as duplicates
from pathlib import Path
from tqdm import tqdm

PDB_REDO = Path(os.environ['PDB_REDO'])
N = 170915

model_dirs = tqdm(PDB_REDO.glob('??/????'), total=N)

rows = []

try:
    for model_dir in model_dirs:
        pdb_id = model_dir.name
        row = dict(
                pdb_id=pdb_id,
                has_mmcif=(model_dir / f'{pdb_id}_final.cif').exists(),
                has_quality=(model_dir / 'data.json').exists(),
        )
        rows.append(row)

except KeyboardInterrupt:
    pass

df = (
        pl.DataFrame(rows)
        .filter(
            pl.col('has_mmcif') ^ pl.col('has_quality')
        )
)

df.write_csv('missing_quality.csv')
print(df)
