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

paths = tqdm(PDB_REDO.glob('**/*_final.cif'), total=N)
#paths = tqdm([PDB_REDO / 'dz/4dzz/4dzz_final.cif'])
#cif_path = PDB_REDO / 'dz/4dzz/4dzz_final.cif'

def find_covering_assemblies(assembly_subchain):
    # Sometimes, multimeric structures specify separate biological assemblies 
    # for the whole multimer and the individual monomers.  I want to minimize 
    # the number of redundant chains to deal with, so to handle cases like 
    # these, I choose the minimum number of assemblies necessary to include 
    # every chain.  This is called the set-cover problem.  In general this is a 
    # difficult problem to solve, but all the examples in the PDB are quite 
    # simple.

    assembly_i = (
            pl.DataFrame(
                assembly_subchain['assembly_id']
                .unique()
                .sort()
            )
            .select(
                pl.int_range(pl.len()).alias('i'),
                pl.col('assembly_id'),
            )
    )

    subchain_i = (
            pl.DataFrame(
                assembly_subchain['subchain_id']
                .unique()
                .sort()
            )
            .select(
                pl.int_range(pl.len()).alias('i'),
                pl.col('subchain_id'),
            )
    )

    assembly_subchain_i = (
            assembly_subchain
            .join(assembly_i, on='assembly_id')
            .rename({'i': 'assembly_i'})
            .join(subchain_i, on='subchain_id')
            .rename({'i': 'subchain_i'})
            .select('assembly_i', 'subchain_i')
    )

    # row: subchain
    # col: assembly
    # 1 if assembly in subchain, 0 otherwise
    A = np.zeros((len(subchain_i), len(assembly_i)))
    i = assembly_subchain_i.to_numpy()
    A[i[:,1], i[:,0]] = 1

    res = milp(
            c=np.ones(len(assembly_i)),
            integrality=np.ones(len(assembly_i)),
            bounds=Bounds(lb=0, ub=1),
            constraints=LinearConstraint(A, lb=1),
    )

    covering_assembly = (
            assembly_i
            .join(
                pl.DataFrame(dict(
                    i=np.arange(len(assembly_i)),
                    select=res.x.astype(int),
                )),
                on='i',
            )
            .filter(
                pl.col('select') != 0
            )
            .select('assembly_id')
    )

    return covering_assembly

many_to_many = []

try:
    for cif_path in paths:
        cif = read_cif(str(cif_path)).sole_block()

        struct_assembly_gen = cif.get_mmcif_category('_pdbx_struct_assembly_gen.')
        if not struct_assembly_gen:
            continue

        assembly_subchain = (
                pl.DataFrame(struct_assembly_gen)
                .select(
                    'assembly_id',
                    subchain_id=pl.col('asym_id_list').str.split(','),
                )
                .explode('subchain_id')
        )
        covering_assembly_subchain = (
                find_covering_assemblies(assembly_subchain)
                .join(
                    assembly_subchain,
                    on='assembly_id',
                )
        )

        if any(duplicates(covering_assembly_subchain['subchain_id'])):
            many_to_many.append(cif.name)

        paths.set_description(f'hits: {many_to_many[:5]} + {len(many_to_many[5:])} more')

except KeyboardInterrupt:
    pass

debug(many_to_many)
