#!/usr/bin/env python3

import torch
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

from macromol_gym_pretrain.lightning import CnnNeighborDataModule
from pipeline_func import f, X
from tqdm import tqdm
from itertools import product
from more_itertools import first

CHANNELS = [
        [
            ['*']
        ],
        [
            ['C'],
            ['N'],
            ['O'],
            ['P'],
            ['S','SE'],
            ['*'],
        ],
]
ATOM_RADIUS_X = [0.5, 1.0, 1.5]
all_stats = []

for channels, atom_radius_x in tqdm(list(product(CHANNELS, ATOM_RADIUS_X))):
    data = CnnNeighborDataModule(
            db_path='mmt_pdb.sqlite',
            neighbor_padding_A=1,
            noise_max_distance_A=0,
            noise_max_angle_deg=0,
            grid_length_voxels=21,
            grid_resolution_A=0.75,
            atom_radius_A=0.75 * atom_radius_x,
            element_channels=channels,
            ligand_channel=False,
            batch_size=320,

            num_workers=0,
    )

    x, y = first(data.train_dataloader())
    x_flat = (
            x
            | f(torch.swapaxes, 0, 2)
            | f(torch.flatten, 1)
            | f(torch.swapaxes, 0, 1)
    )
    df = (
            pl.DataFrame(x_flat.numpy())
            .unpivot(variable_name='channel', value_name='value')
            .with_columns(
                pl.col('channel').replace_strict(
                    {
                        f'column_{i}': dict(i=i, name='|'.join(elems))
                        for i, elems in enumerate(channels)
                    },
                    return_dtype=pl.Struct(dict(i=pl.Int8, name=pl.String)),
                )
            )
    )

    stats = (
            df
            .group_by('channel').agg(
                pl.mean('value').alias('mean'),
                pl.std('value').alias('std'),
            )
            .unnest('channel')
            .sort('i')
            .select(
                atom_radius_x=atom_radius_x,
                num_channels=len(channels),
                channel_index='i',
                channel_elements='name',
                mean='mean',
                std='std',
            )
    )
    all_stats.append(stats)

df = pl.concat(all_stats).sort('atom_radius_x', 'num_channels', 'channel_index')
df.write_csv('calc_voxel_mean.csv')
debug(df)



