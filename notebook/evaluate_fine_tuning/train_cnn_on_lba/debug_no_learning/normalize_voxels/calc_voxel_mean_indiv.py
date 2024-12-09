#!/usr/bin/env python3

# This script is for calculating the normalization parameters for a specific 
# set of dataset parameters.

import torch
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

from atompaint.diffusion.data import MacromolImageDiffusionData
from einops import rearrange
from pipeline_func import f, X
from tqdm import tqdm
from itertools import product
from more_itertools import first

data = MacromolImageDiffusionData(
        db_path='mmt_pdb.sqlite',
        grid_length_voxels=33,
        grid_resolution_A=1,
        atom_radius_A=0.5,
        element_channels=[
            ['C'],
            ['N'],
            ['O'],
            ['P'],
            ['S','SE'],
            ['*'],
        ],
        #normalize_std=0.05,
        batch_size=320,
        num_workers=0,
)
dataloader = data.train_dataloader()
channels = dataloader.dataset.dataset.img_params.element_channels

x, _1, _2 = first(dataloader)
x_flat = rearrange(x, 'b c w h d -> (b w h d) c')
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
        .select(
            pl.mean('value').alias('mean'),
            pl.std('value').alias('std'),
        )
)
debug(stats)

stats = (
        df
        .group_by('channel').agg(
            pl.mean('value').alias('mean'),
            pl.std('value').alias('std'),
        )
        .unnest('channel')
        .sort('i')
        .select(
            channel_index='i',
            channel_elements='name',
            mean='mean',
            std='std',
        )
)

df = stats.sort('channel_index')
debug(df)



