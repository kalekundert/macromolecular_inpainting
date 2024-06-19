#!/usr/bin/env python3

import duckdb
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

db = duckdb.connect('mmc_pdb.duckdb')

df = db.sql('''\
        SELECT
            model.id AS id,
            first(model.pdb_id) AS pdb_id,
            first(model.exptl_methods) AS exptl_methods,
            coalesce(
                min(quality_xtal.resolution_A),
                min(quality_em.resolution_A)
            ) AS resolution_A
        FROM model
        LEFT JOIN quality_xtal ON model.id = quality_xtal.model_id
        LEFT JOIN quality_em ON model.id = quality_em.model_id
        GROUP BY model.id
        ORDER BY resolution_A
''').pl()

df = (
        df
        .drop_nulls('resolution_A')
        .explode('exptl_methods')
)

print(
        df
        .group_by('exptl_methods')
        .len()
)

sns.displot(
        df.filter(
            pl.col('exptl_methods').is_in([
                'X-RAY DIFFRACTION',
                'ELECTRON MICROSCOPY',
            ]),
        ),
        x='resolution_A',
        hue='exptl_methods',
        kind='ecdf',
)
plt.axvline(4, ls='--', color='gray')
plt.xlim(0, 10)
plt.savefig('resolution_cdf.svg')
plt.show()


