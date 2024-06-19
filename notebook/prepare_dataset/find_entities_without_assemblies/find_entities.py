#!/usr/bin/env python3

import duckdb

db = duckdb.connect('mmc_pdb.duckdb')

db.sql('''\
        SELECT
            structure.pdb_id,
            list(entity.pdb_id)
        FROM entity
        ANTI JOIN subchain ON entity.id = subchain.entity_id
        JOIN structure on structure.id = entity.struct_id
        GROUP BY structure.pdb_id
''').show(max_rows=50)

