#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from scipy.spatial.transform import Rotation, Slerp
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from color_me import ucsf
from itertools import chain
from math import *

phi = (1 + sqrt(5)) / 2
t = 150

def plot_icosahedron(ax, radius=1, facecolors=ucsf.blue[0], rotation=None):
    # Copied vertex info from:
    # https://github.com/anishagartia/Icosahedron_OpenGL

    # I'm sure there's a way to figure this out algorithmically, but for now 
    # this is easier.

    a = radius / sin(2 * pi / 5)
    b = a * phi

    verts = np.array([
        [-a,  0,  b],
        [ a,  0,  b],
        [-a,  0, -b],
        [ a,  0, -b],

        [ 0,  b,  a],
        [ 0,  b, -a],
        [ 0, -b,  a],
        [ 0, -b, -a],

        [ b,  a,  0],
        [-b,  a,  0],
        [ b, -a,  0],
        [-b, -a,  0],
    ])
    faces = np.array([
        [4, 1, 0],
        [1, 0, 6],
        [6, 0, 11],
        [0, 11, 9],
        [0, 9, 4],

        [9, 5, 4],
        [4, 5, 8],
        [4, 8, 1],
        [8, 10, 1],
        [6, 1, 10],
        [7, 6, 10],
        [7, 11, 6],
        [7, 2, 11],
        [9, 11, 2],
        [9, 2, 5],

        [5, 2, 3],
        [5, 3, 8],
        [8, 3, 10],
        [7, 10, 3],
        [2, 7, 3],
     ])

    polys = verts[faces]

    if rotation is not None:
        polys = polys.reshape(-1, 3)
        polys = rotation.apply(polys)
        polys = polys.reshape(-1, 3, 3)

    artist = Poly3DCollection(
            polys,
            facecolors=facecolors,
            shade=True,
    )
    ax.add_collection3d(artist)

    return artist

def plot_cube(ax, length=3, facecolors=ucsf.blue[0], rotation=None):
    x = length / 2

    verts = np.array([
        [ x,  x,  x],
        [ x,  x, -x],
        [ x, -x, -x],
        [ x, -x,  x],

        [-x, -x,  x],
        [-x,  x,  x],
        [-x,  x, -x],
        [-x, -x, -x],
    ])
    faces = np.array([
        [0, 1, 2, 3],
        [0, 1, 6, 5],
        [1, 2, 7, 6],
        [2, 3, 4, 7],
        [0, 3, 4, 5],
        [4, 5, 6, 7],
    ])

    polys = verts[faces]

    # debug(polys)
    # raise SystemExit

    if rotation is not None:
        polys = polys.reshape(-1, 3)
        polys = rotation.apply(polys)
        polys = polys.reshape(-1, 4, 3)

    artist = Poly3DCollection(
            polys,
            facecolors=facecolors,
            shade=True,
    )
    ax.add_collection3d(artist)

    return artist


fig = plt.figure()
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax2 = fig.add_subplot(1, 2, 2, projection='3d')

ax1.set_title('exact')
ax2.set_title('interpolated')

for ax in [ax1, ax2]:
    ax.set_xlim(-2, 2);  ax.set_xticks([])
    ax.set_ylim(-2, 2);  ax.set_yticks([])
    ax.set_zlim(-2, 2);  ax.set_zticks([])

r0 = Rotation.from_quat([1, 0, 0, 0])
r1_exact = Rotation.from_quat([-0.5, -0.5, -0.5,  0.5])
r1_interp = Rotation.from_quat([-0.5, -0.30901699, -0.80901699, -0.0])

slerp_exact = Slerp(
        np.linspace(0, t, 5, dtype=int),
        Rotation.concatenate([r0, r1_exact, r1_exact, r0, r0]),
)
slerp_interp = Slerp(
        np.linspace(0, t, 5, dtype=int),
        Rotation.concatenate([r0, r1_interp, r1_interp, r0, r0]),
)

# "Artist" animations are less efficient that "function" animations, but 
# there's a bug in `Poly3DCollection` that prevents the shading from being 
# applied after the vertices are updated, so this is the only approach that 
# works.
artists = [
        [
            plot_cube(ax1, rotation=slerp_exact(i)),
            plot_cube(ax2, rotation=slerp_interp(i)),
        ]
        for i in range(t)
]

anim = animation.ArtistAnimation(fig=fig, artists=artists, interval=30)

anim.save('plots/ico_rotation.gif')

plt.show()
