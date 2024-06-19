#!/usr/bin/env python3

import duckdb
import polars as pl

db = duckdb.connect('mmc_pdb.duckdb', read_only=True)

entity_type = db.sql('''\
        SELECT
            entity.id AS entity_id,
            coalesce(
                entity_polymer.type == 'polypeptide(L)',
                FALSE
            ) AS is_protein,
        FROM entity
        LEFT JOIN entity_polymer ON entity.id = entity_polymer.entity_id
        ANTI JOIN entity_ignore ON entity.id = entity_ignore.entity_id
''')

struct_join = db.sql('''\
        SELECT
            structure.id AS struct_id,
            assembly.id AS assembly_id,
            subchain.id AS subchain_id,
            entity_type.entity_id AS entity_id,
            is_protein
        FROM structure
        JOIN assembly ON structure.id = assembly.struct_id
        JOIN assembly_subchain ON assembly.id = assembly_subchain.assembly_id
        JOIN subchain ON subchain.id = assembly_subchain.subchain_id
        JOIN entity_type USING (entity_id)
''').pl()

df = (
        struct_join
        .group_by('assembly_id')
        .agg(
            pl.col('is_protein').all().alias('all_protein'),
            pl.col('is_protein').any().alias('any_protein'),
        )
        .with_columns(
            (pl.col('any_protein') & ~pl.col('all_protein')).alias('protein_and_nonprotein')
        )
)

print(df)

print(df.mean())
