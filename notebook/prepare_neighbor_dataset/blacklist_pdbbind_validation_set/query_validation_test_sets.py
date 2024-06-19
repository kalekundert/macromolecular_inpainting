#!/usr/bin/env python3

import os
import polars as pl

from atom3d.datasets import LMDBDataset
from pathlib import Path

LBA_DIR = Path(os.environ['ATOM3D_LBA_DATA_DIR'])

paths = {
        'val': LBA_DIR / 'val',
        'test': LBA_DIR / 'test',
}

for k, path in paths.items():
    dataset = LMDBDataset(path)
    pdb_ids = pl.DataFrame({'pdb_id': [x['id'] for x in dataset]}).unique()
    pdb_ids.write_csv(f'{k}.csv', include_header=False)

