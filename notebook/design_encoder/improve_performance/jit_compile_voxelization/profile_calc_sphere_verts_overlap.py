#!/usr/bin/env python3

# I noticed that the actual overlap calculation itself was only accounting for 
# about a third of the time spent in this function.  I expected it to take 
# almost all the time, so I wanted to figure out what else was taking an 
# appreciable amount of time.
#
# Ultimately I found that constructing the Sphere and Hexahedron object are 
# also relatively expensive.  Looking at the code, this is likely because they 
# precalculate a bunch of areas upon initialization, although it's possible 
# that heap allocations are also taking some time.  The sanity check doesn't 
# use a significant amount of time.  I don't think there's anything I can do to 
# speed up this function further.

import atompaint.datasets.voxelize as ap
import overlap
import numpy as np
import timerit

coord = np.array([0., 0., 0.])
verts = ap._get_cgns_cube_verts(ap.Cube(coord, 1))
sphere = ap.Sphere(coord, 1)

for _ in timerit(label='cube'):
    cube_ = overlap.Hexahedron(verts)

for _ in timerit(label='sphere'):
    sphere_ = overlap.Sphere(sphere.center_A, sphere.radius_A)

for _ in timerit(label='overlap'):
    overlap_A3 = overlap.overlap(sphere_, cube_)

for _ in timerit(label='sanity check'):
    fudge_factor = 1 + 1e-6
    if not (0 <= overlap_A3 <= sphere.volume_A3 * fudge_factor):
        raise RuntimeError(f"numerical instability in overlap: overlap volume ({overlap_A3} Å³) exceeds sphere volume ({sphere.volume_A3} Å³)")

