#!/usr/bin/env python3

import polars as pl
import duckdb
import macromol_dataframe as mmdf
import os

from pathlib import Path
from tqdm import tqdm

db = duckdb.connect('atom_density.duckdb')
db.sql('''\
        CREATE TABLE IF NOT EXISTS density (
            pdb_id STRING,
            atoms_per_nm3 FLOAT,
        )
''')

already_seen = set(
        db.sql('SELECT DISTINCT pdb_id FROM density')
        .pl()['pdb_id'],
)

def get_pdb_id(p):
    return p.name[:4].lower()

cif_paths = [
        p
        for p in Path(os.environ['PDB_MMCIF']).glob('**/*.cif.gz')
        if get_pdb_id(p) not in already_seen
]

bin_size_A = 10
bin_size_nm = bin_size_A / 10

for cif_path in tqdm(cif_paths):
    atoms = mmdf.read_asymmetric_unit(cif_path)
    atoms = mmdf.select_model(atoms, '1')
    atoms = mmdf.prune_hydrogen(atoms)

    bins = (
            atoms
            .with_columns(
                (pl.col('x', 'y', 'z') // bin_size_A).cast(int).name.suffix('_bin')
            )
            .group_by(['x_bin', 'y_bin', 'z_bin'])
            .agg(
                (pl.col('occupancy').sum() / bin_size_nm**3)
                .alias('atoms_per_nm3')
            )
    )

    db.sql(
            '''\
            INSERT INTO density (pdb_id, atoms_per_nm3)
            SELECT ?, atoms_per_nm3 FROM bins
            ''',
            params=[get_pdb_id(cif_path)],
    )


