import torch
import polars as pl
import numpy as np
import os

from atompaint.metrics.neighbor_loc import NeighborLocAccuracy
from macromol_gym_unsupervised import ImageParams, image_from_atoms
from macromol_gym_unsupervised.torch import MacromolDataset
from macromol_dataframe import transform_atom_coords
from macromol_voxelize import Grid
from torch.utils.data import DataLoader
from more_itertools import first, take
from tqdm import tqdm
from math import sqrt

class NoisyMacromolDataset(MacromolDataset):

    def __init__(
            self,
            *,
            atom_noise_A: float = 0,
            voxel_noise: float = 0,
    ):
        super().__init__(
                db_path='mmt_pdb.sqlite',
                split='val',
        )
        self.img_params = ImageParams(
                grid=Grid(
                    length_voxels=33,
                    resolution_A=1,
                ),
                atom_radius_A=0.5,
                element_channels=[['C'], ['N'], ['O'], ['P'], ['S','SE'], ['*']],
        )
        self.atom_noise_A = atom_noise_A
        self.voxel_noise = voxel_noise

    def __getitem__(self, i):
        x = super().__getitem__(i)

        atoms_a = transform_atom_coords(x['atoms_i'], x['frame_ia'])

        if self.atom_noise_A:
            noise = x['rng'].normal(
                    scale=self.atom_noise_A,
                    size=(3, atoms_a.height),
            )
            atoms_a = (
                    atoms_a
                    .with_columns(
                        x=pl.col('x') + noise[0],
                        y=pl.col('y') + noise[1],
                        z=pl.col('z') + noise[2],
                    )
            )

        img = image_from_atoms(atoms_a, self.img_params)

        if self.voxel_noise:
            noise = x['rng'].normal(
                    scale=self.voxel_noise,
                    size=img.shape,
            )

            # Add the noise to the image in such a way that the variance of the 
            # original image is preserved.
            var_img = np.var(img)
            var_noise = self.voxel_noise**2
            scale_factor = sqrt(var_img / (var_img + var_noise))
            img = scale_factor * (img + noise)

        img = torch.from_numpy(img).float()

        return img

metric = NeighborLocAccuracy().to('cuda')
rows = []

data_kwargs = [dict()]
data_kwargs += [dict(atom_noise_A=x) for x in np.arange(0, 2, 0.2) + 0.2]
data_kwargs += [dict(voxel_noise=x) for x in np.logspace(-3, 0, 10)]

for kwargs in tqdm(data_kwargs):
    data = NoisyMacromolDataset(**kwargs)
    data_loader = DataLoader(
            dataset=data,
            batch_size=12,
            pin_memory=True,
            num_workers=os.cpu_count(),
            drop_last=True,
    )
    for x in tqdm(data_loader):
        x = x.to('cuda')
        metric.update(x)

    row = dict(
            atom_noise_A=data.atom_noise_A,
            voxel_noise=data.voxel_noise,
            accuracy=metric.compute(),
    )
    rows.append(row)

    metric.reset()

df = pl.DataFrame(rows)
df.write_parquet('accuracies.parquet')
print(df)

