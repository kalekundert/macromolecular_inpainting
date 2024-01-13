#!/usr/bin/env python3

# As a baseline for other comparisons, see how long a handful of 
# unlikely-to-be-optimized data loader steps take.

import numpy as np
import timerit

from atompaint.datasets.atoms import atoms_from_mmcif
from atompaint.datasets.voxelize import ImageParams, Grid, image_from_atoms
from pathlib import Path

cif_path = Path('2gd5_final.cif')
for _ in timerit:
    # Didn't pick this structure for any reason, but I did check and see that 
    # it's a pretty normal-size protein.
    atoms = atoms_from_mmcif(cif_path)

img_params = ImageParams(
        grid=Grid(
            length_voxels=21,
            resolution_A=0.75,
            # Chose a center by looking at the structure and choosing a 
            # relatively central Cα (N85).
            center_A=np.array([13.540, 23.857, 74.976]),
        ),
        channels=['C', 'N', 'O', '.*'],
        element_radii_A=0.375,
)

for _ in timerit:
    image_from_atoms(atoms, img_params)
