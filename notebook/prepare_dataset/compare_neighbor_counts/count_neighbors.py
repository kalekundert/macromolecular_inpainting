#!/usr/bin/env python3

import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import joblib

from macromol_training import open_db

cache = joblib.Memory('.cache').cache

@cache
def get_neighbor_counts():
    db = open_db('mmt_pdb.sqlite')
    cur = db.execute('SELECT zone_id, neighbor_id FROM zone_neighbor')
    rows = cur.fetchall()
    return pl.DataFrame(rows, ['zone_id', 'neighbor_id'], orient='row')

df = (
        get_neighbor_counts()
        .group_by('zone_id')
        .len()
        .rename({'len': 'neighbor_count'})
        .group_by('neighbor_count')
        .len()
        .rename({'len': 'zones'})
        .sort('neighbor_count')
        .with_columns(
            zone_neighbor_pairs=pl.col('zones') * pl.col('neighbor_count'),
        )
        .melt('neighbor_count')
)

epochs = (
        df
        .group_by('variable')
        .agg(pl.col('value').sum().alias('total_count'))
        .with_columns(
            epochs_for_32M_its=pl.lit(32_000_000) / pl.col('total_count'),
        )
)
debug(epochs)
epochs.write_excel('count_neighbors.xlsx')

sns.relplot(
        df,
        x='neighbor_count',
        y='value',
        hue='variable',
)
plt.savefig('count_neighbors.svg')
plt.show()


