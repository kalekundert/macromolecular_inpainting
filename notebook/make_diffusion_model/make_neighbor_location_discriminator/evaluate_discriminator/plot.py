#!/usr/bin/env python3

import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

df = pl.read_parquet('accuracies.parquet')

fig, axes = plt.subplots(
        figsize=(8,4),
        nrows=1,
        ncols=2,
        sharey=True,
        layout='constrained',
)

sns.lineplot(
        df.filter(voxel_noise=0),
        x='atom_noise_A',
        y='accuracy',
        ax=axes[0],
)
axes[0].set_xlabel('atom coordinate noise (Å)')

sns.lineplot(
        df.filter(atom_noise_A=0),
        x='voxel_noise',
        y='accuracy',
        ax=axes[1],
)
axes[1].set_xlabel('voxel noise')
axes[1].set_xscale('log')

plt.savefig('discriminator_noise.svg')
plt.show()

