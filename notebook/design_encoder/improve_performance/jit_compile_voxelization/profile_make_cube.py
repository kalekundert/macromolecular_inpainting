#!/usr/bin/env python3

# I want to see if it saves any  time to calculate vertices directly from the 
# voxel, versus going through a cube intermediate (which I feel makes the code 
# more modular).

# It's about twice as fast to cut out the intermediate object.  This probably 
# doesn't make much of a difference in the grand scheme of things, but it's 
# enough to make this step faster than ``overlap.overlap()``, and 
# psychologically I like seeing all of my code below the ``overlap`` library on 
# the cumulative time list.

import numpy as np
import atompaint.datasets.voxelize as ap
import timerit

grid = ap.Grid(
        length_voxels=3,
        resolution_A=1,
)
voxel = np.array([0, 0, 0], dtype=int)

# Make sure everything is compiled.  For some reason, the cache for 
# `_make_cube()` doesn't seem to work...

cube = ap._make_cube(grid, voxel)
verts = ap._get_cgns_cube_verts_jit(cube.center_A, cube.length_A)
verts = ap._get_cgns_voxel_verts_jit(
        grid.length_voxels,
        grid.resolution_A,
        grid.center_A,
        voxel,
)

for _ in timerit(label='cube'):
    cube = ap._make_cube(grid, voxel)
    verts = ap._get_cgns_cube_verts_jit(cube.center_A, cube.length_A)

for _ in timerit(label='verts'):
    verts = ap._get_cgns_voxel_verts_jit(
            grid.length_voxels,
            grid.resolution_A,
            grid.center_A,
            voxel,
    )

print()

# Are `slots=True` dataclasses any faster to instantiate?

# Yes, but only slightly.  Note that the time to instantiate the cube (1.5 µs) 
# doesn't account for all the difference between the two-step and one-step 
# vertex calculations (4 µs).  Presumably the rest of the difference is 
# accounted for by more efficient JIT compilation.

from dataclasses import dataclass
from numpy.typing import NDArray

@dataclass(frozen=True)
class Cube:
    center_A: NDArray
    length_A: float

@dataclass(frozen=True, slots=True)
class CubeSlots:
    center_A: NDArray
    length_A: float

center = np.array([0., 0., 0.], dtype=float)

for _ in timerit(label='no slots'):
    Cube(center, 1)

for _ in timerit(label='slots'):
    CubeSlots(center, 1)
