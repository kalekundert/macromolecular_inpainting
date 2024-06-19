#!/usr/bin/env python3

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from atom3d.datasets import LMDBDataset
from atom3d.util.voxelize import get_center
from atom3d_menagerie.data.smp import get_default_smp_data_dir
from tqdm import tqdm
from joblib import Memory
from pathlib import Path

memory = Memory('cache')

@memory.cache
def find_smp_max_dists():
    data = LMDBDataset(get_default_smp_data_dir() / 'train')
    max_dists = []

    for item in tqdm(data):
        atoms = item['atoms']

        xyz = atoms[['x', 'y', 'z']]
        xyz = xyz - get_center(xyz)

        dists = np.linalg.norm(xyz, ord=2, axis=1)
        max_dists.append(np.max(dists))

    return max_dists

max_dists = find_smp_max_dists()

d = max(max_dists)
print('maximum distance from center to atom:', d)

sns.kdeplot(max_dists)
plt.axvline(d, color='darkgray', ls='--')
plt.savefig(Path(__file__).with_suffix('.svg'))
plt.show()
