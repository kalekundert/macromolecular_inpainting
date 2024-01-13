#!/usr/bin/env python3

import torch
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from data.compare_radius import HPARAMS, make_escnn_model
from atom3d_menagerie.data.lba import get_default_lba_data_dir
from atom3d_menagerie.models.cnn import get_default_cnn
from atom3d.datasets import LMDBDataset
from atom3d.util.voxelize import get_center
from atompaint.datasets.voxelize import image_from_atoms, ImageParams, Grid
from atompaint.datasets.atoms import transform_atom_coords
from atompaint.datasets.coords import make_coord_frame
from math import pi, degrees, ceil, sqrt
from tqdm import tqdm
from more_itertools import last, take, one
from natsort import natsorted
from dataclasses import asdict
from joblib import Memory
from pathlib import Path

memory = Memory('cache')

# Generalize this script
# - Load everything into data frame
# - Cache
# - Plot with sns

@memory.cache
def load_invariance_checks(hparams, items, theta):
    models = load_models(hparams)
    img_params = load_img_params(hparams)

    dfs = []

    for k, hparam in tqdm(hparams.items()):
        f = models[k]

        for i, item in tqdm(enumerate(items)):
            x = torch.stack([
                    rotate_item(item, img_params[k], th)
                    for th in theta
            ])
            y = item['scores']['neglog_aff']
            y_hat = f(x).detach().flatten().numpy()

            df = pd.DataFrame({
                'name': k,
                **asdict(hparam),
                'x': i,
                'theta': theta,
                'y': y,
                'y_hat': y_hat,
            })
            dfs.append(df)

    return pd.concat(dfs)

def load_models(hparams):
    models = {}

    for k in hparams:
        version_paths = (Path('data') / k).glob('version_*')
        ckpt_path = last(natsorted(version_paths)) / 'checkpoints/epoch=49-step=11000.ckpt'
        models[k] = load_ckpt(ckpt_path)

    return models

def load_ckpt(ckpt_path):
    if 'escnn' in str(ckpt_path):
        model = make_escnn_model()
    else:
        model = get_default_cnn(
                in_channels=5,
                spatial_size=21,
        )

    ckpt = torch.load(
            ckpt_path,
            map_location=torch.device('cpu'),
    )
    ckpt = {
            k[len('model.'):]: v
            for k, v in ckpt['state_dict'].items()
    }
    
    model.train()
    model.load_state_dict(ckpt)
    model.eval()

    return model

def load_img_params(hparams):
    return {
            k: ImageParams(
                grid=Grid(
                    length_voxels=21,
                    resolution_A=1.0,
                ),
                channels=['H', 'C', 'O', 'N', '.*'],
                element_radii_A=hparam.element_radius_A,
            )
            for k, hparam in hparams.items()

    }

def rotate_item(item, img_params, theta):
    ligand_xyz_i = item['atoms_ligand'][['x', 'y', 'z']].astype(np.float32)
    ligand_center_i = get_center(ligand_xyz_i)

    rot_z = np.array([0, 0, theta])
    frame_ix = make_coord_frame(ligand_center_i, rot_z)

    # I can't find the definition of the pocket, so I'm not 100% convinced 
    # that it really contains all the atoms in the vicinity of the ligand.  
    # But the example code uses the pocket atoms after a random rotation 
    # around the ligand center, so I'll just do the same.

    atoms_i = pd.concat([item['atoms_pocket'], item['atoms_ligand']])
    atoms_x = transform_atom_coords(atoms_i, frame_ix)

    img = image_from_atoms(atoms_x, img_params)
    img = torch.from_numpy(img).float()

    return img


HPARAMS = {k: v for k, v in HPARAMS.items() if v.dataset == 'lba'}
data = LMDBDataset(get_default_lba_data_dir() / 'test')
theta = np.linspace(0, 2*pi)

n = 4
df = load_invariance_checks(HPARAMS, take(n, data), theta)

fg = sns.relplot(
        df, 
        x='theta',
        y='y_hat',
        hue='name',
        #hue='element_radius_A',
        #hue='model_type',
        col='x',
        col_wrap=int(ceil(sqrt(n))),
        kind='line',
        estimator=None,
        units='name',
)

g = df.groupby('x')

for k, ax in fg.axes_dict.items():
    y = one(g.get_group(k)['y'].unique())
    ax.axhline(y, linestyle='--', color='darkgray')

plt.xlim(0, 2*pi)
plt.xticks(np.array([0, 1/2, 1, 3/2, 2]) * pi, ['0', r'$\frac{\pi}{2}$', r'$\pi$', r'$\frac{3\pi}{2}$', r'$2\pi$'])
plt.savefig(Path(__file__).with_suffix('.svg'))
plt.show()

# Animation:
# - Rotate input
# - Render in headless pymol
# - Plot in matplotlib
# - Combine with Cairo, maybe
# - Make movie using PIL or imageio
#   - gif or mpeg output formats





