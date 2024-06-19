#!/usr/bin/env python3

import os
import polars as pl

from pathlib import Path
from tqdm import tqdm
from macromol_dataframe import read_mmcif_asymmetric_unit

PDB = Path(os.environ['PDB_MMCIF'])

paths = PDB.glob('**/*.cif.gz')
progress_bar = tqdm(paths, total=217153)

counts = pl.DataFrame([], {'element': str, 'len': int})

try:
    for cif_path in progress_bar:
        progress_bar.set_description(cif_path.stem)

        counts_i = (
                read_mmcif_asymmetric_unit(cif_path)
                .group_by('element')
                .len()
        )

        counts = (
                counts
                .join(counts_i, on='element', how='outer_coalesce')
                .fill_null(0)
                .select(
                    pl.col('element'),
                    pl.col('len') + pl.col('len_right'),
                )
        )

except KeyboardInterrupt:
    pass

counts = counts.sort('len', descending=True)

counts.write_csv('element_counts.csv')
print(counts)
