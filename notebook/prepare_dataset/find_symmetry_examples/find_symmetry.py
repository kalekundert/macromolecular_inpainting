#!/usr/bin/env python3

import os
import polars as pl

from pathlib import Path
from tqdm import tqdm
from macromol_census import read_cif, extract_dataframe

PDB = Path(os.environ['PDB_MMCIF'])

paths = PDB.glob('**/*.cif.gz')
progress_bar = tqdm(paths, total=217153)

try:
    for cif_path in progress_bar:
        cif = read_cif(cif_path)
        pdb_id = cif.name.lower()

        progress_bar.set_description(pdb_id)

        struct_assembly_gen = (
                extract_dataframe(
                    cif, 'pdbx_struct_assembly_gen',
                    required_cols=[
                        'assembly_id',
                        'asym_id_list',
                        'oper_expression',
                    ],
                )
                .with_columns(
                    pl.col('asym_id_list').str.split(','),
                    pl.col('oper_expression').str.split(','),
                )
                .explode('oper_expression')
                .explode('asym_id_list')
                .group_by(['assembly_id'])
                .agg(pl.len().alias('n'))
                .filter(pl.col('n') == 1)
        )

        if struct_assembly_gen.height == 2:
            print(struct_assembly_gen)

except KeyboardInterrupt:
    pass

