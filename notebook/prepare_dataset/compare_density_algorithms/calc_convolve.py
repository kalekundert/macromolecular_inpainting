import macromol_dataframe as mmdf
import macromol_voxelize as mmvox
import polars as pl
import numpy as np
import timerit
import seaborn as sns
import matplotlib.pyplot as plt

from utils import *
from scipy.interpolate import RegularGridInterpolator
from scipy.signal import convolve
from tqdm import tqdm
from more_itertools import one, unique_everseen as unique
from pipeline_func import f

def make_sphere_mask(voxel_size_A, radius_A):

    # Force the kernel to have an odd number of voxels on each side, so that 
    # the center of the sphere is in the center of a voxel.  There's got to be 
    # a better way to do this, but this works for now.
    length_voxels = int(ceil(2 * radius_A / voxel_size_A))
    if length_voxels % 2 == 0:
        length_voxels += 1

    img_params = mmvox.ImageParams(
            channels=1,
            grid=mmvox.Grid(
                length_voxels=length_voxels,
                resolution_A=voxel_size_A,
                center_A=[0, 0, 0],
            ),
    )
    sphere = pl.DataFrame([
            dict(x=0, y=0, z=0, radius_A=radius_A, occupancy=1, channels=[0]),
    ])
    kernel = mmvox.image_from_atoms(sphere, img_params)[0]

    assert all(x % 2 == 1 for x in kernel.shape)

    return kernel

#cif = mmdf.read_mmcif('4w4g.cif.gz')
#cif = mmdf.read_mmcif('7y7a.cif.gz')
#cif = mmdf.read_mmcif('7bw6.cif.gz')
cif = mmdf.read_mmcif('6ncl.cif.gz')
#cif = mmdf.read_mmcif('5zz8.cif.gz')
print(cif.id)

atoms = mmdf.make_biological_assembly(
        cif.asym_atoms,
        cif.assembly_gen,
        cif.oper_map,
        assembly_id='1',
)

print(f"atoms: {atoms.height / 1e6:.1f} M")
kd_tree = make_kd_tree(atoms)

voxel_size_A = 2
print(f"voxel size: {voxel_size_A} Å")

kernel = make_sphere_mask(voxel_size_A, 15)

###

for _ in timerit:
    volume_nm3 = (voxel_size_A / 10)**3

    df = (
            atoms
            .with_columns(
                (pl.col('x', 'y', 'z') / voxel_size_A)
                .floor()
                .cast(int)
            )
            .group_by(['x', 'y', 'z'])
            .agg(
                atoms_per_nm3=pl.col('occupancy').sum() / volume_nm3
            )
    )

    voxels = df.select('x', 'y', 'z').to_numpy()
    min_corner = np.min(voxels, axis=0)
    max_corner = np.max(voxels, axis=0)

    img_shape = max_corner - min_corner + 1
    img = np.zeros(img_shape)
    img[*(voxels - min_corner).T] = df['atoms_per_nm3']

    pad = (one(unique(kernel.shape)) - 1) // 2

    a = min_corner - pad
    b = max_corner + pad

    points = [
            voxel_size_A * (np.arange(a[i], b[i] + 1) + 0.5)
            for i in range(3)
    ]

    ###

    out = convolve(img, kernel)
    interp = RegularGridInterpolator(
                points=points,
                values=out,
                bounds_error=False,
                fill_value=0,
        )

    ###

print()
print(f'voxels: {img.nbytes / 1e6} MB')
print(f'kernel: {kernel.nbytes / 1e6} MB')
print(f'conv: {out.nbytes / 1e6} MB')
print()

coords_A = calc_zone_centers_A(atoms, 10)

for _ in timerit:
    x = interp(coords_A)

print()
raise SystemExit

y = np.zeros(len(coords_A))
for i, coord_A in enumerate(tqdm(coords_A)):
    y[i] = calc_density_atoms_nm3(atoms, kd_tree, coord_A, 15)

i = y > 0
z = y[i] - x[i]

print('mean:', np.mean(z))
print('std:', np.std(z))
print('min:', np.min(z))
print('max:', np.max(z))
print()

for i in range(11):
    print(f'{10*i}%: {np.quantile(z, i/10)}')

# sns.displot(z)
# plt.show()



