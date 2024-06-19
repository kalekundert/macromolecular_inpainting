#!/usr/bin/env python3

import macromol_voxelize as mmvox
import macromol_dataframe as mmdf
import macromol_training as mmt
import matplotlib.pyplot as plt
import numpy as np
import timerit

from sklearn.neighbors import KDTree
from scipy.spatial.transform import Rotation
from scipy.spatial import distance_matrix
from itertools import product, combinations, permutations
from functools import partial
from pipeline_func import f

# For comparison, benchmark the time it takes to voxelize a region of protein.  
# This is the slowest data loading step, so as long as we're faster than this, 
# we're good.

db = mmt.open_db('mmt_pdb.sqlite')

# atoms = (
#         mmdf.read_asymmetric_unit('171l.cif.gz')
#         | f(mmvox.set_atom_channels_by_element, channels)
#         | f(mmvox.set_atom_radius_A, 1)
# )
# center_A = np.array([6.394, 49.242, 9.187])

# debug(
#         mmt.select_zone_pdb_ids(db, 1)
# )

for _ in timerit:
    center_A, atoms = mmt.select_zone_atoms(db, 1)
    atoms = mmvox.set_atom_radius_A(atoms, 1)

channels = ['C', 'N', 'O', 'S', '.*']
img_params = mmvox.ImageParams(
        channels=len(channels),
        grid=mmvox.Grid(length_voxels=24, resolution_A=1, center_A=center_A),
        assign_channels=partial(
            mmvox.set_atom_channels_by_element,
            channels=channels,
        )
)

#atoms = (
#        atoms
#         | f(mmdf.prune_water)
#         | f(mmdf.prune_hydrogen)
#         #| f(mmvox.set_atom_channels_by_element, channels)
#         | f(mmvox.set_atom_radius_A, 1)
#)
#for _ in timerit:
#    atoms = (
#            atoms
#             #| f(mmdf.prune_water)
#             #| f(mmdf.prune_hydrogen)
#             #| f(mmvox.set_atom_channels_by_element, channels)
#             #| f(mmvox.set_atom_radius_A, 1)
#    )

for _ in timerit:
    mmvox.image_from_atoms(atoms, img_params)

def sample_neighbor_dist_matrix(rng, neighbors, valid_i):
    valid_i = set(valid_i)

    for x in iter_random_coords():
        D = distance_matrix(neighbors, x[:10])
        nearest_i = set(np.argmin(D, axis=0))

        if hits := (nearest_i & valid_i):
            return rng.choice(sorted(hits))

def sample_neighbor_kd_tree(rng, neighbors, valid_i):
    valid_i = set(valid_i)

    for x in iter_random_coords():
        nearest_i = kd_tree.query(x, return_distance=False)
        nearest_i = set(nearest_i.flat)

        #D = distance_matrix(neighbors, x)
        #plt.matshow(D)

        ##plt.subplot(1, 2, 2, projection='3d')
        #fig = plt.figure()
        #ax = fig.add_subplot(projection='3d')

        #ax.scatter(neighbors[:,0], neighbors[:,1], neighbors[:,2])
        #ax.scatter(x[:,0], x[:,1], x[:,2])

        #plt.show()

        if hits := (nearest_i & valid_i):
            return rng.choice(sorted(hits))

def sample_neighbor_rot_precalc(rng, neighbors, valid_i):
    x = rng.normal(size=3)
    x /= np.linalg.norm(x)

    # Also tried doing this with kd_tree; slower.
    d = np.linalg.norm(neighbors - x, axis=1)
    i = np.argmin(d)

    # debug(x, d, i)

    j = rng.integers(len(neighbors))

    Rx = R[i,j] @ x
    
    # if i == j:
    #     return x

    #neighbor = neighbors[j]
    #neighbor = rng.choice(neighbors)


    #R, *err = Rotation.align_vectors(neighbor, neighbors[i])
    #Rx = R.apply(x)

    # https://stackoverflow.com/questions/45142959/calculate-rotation-matrix-to-align-two-vectors-in-3d-space
    # a = neighbors[i]
    # b = neighbor
    # v = np.cross(a, b)
    # c = np.dot(a, b)
    # s = np.linalg.norm(v)
    # kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    # R = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))

    # Rx = R @ x

    #debug(i, j)

    ## Cyan: chosen neighbor
    ## Green: neighbor closest to random point
    ## Grey: all other neighbors
    ##
    ## Orange: random point
    ## Purple: random point moved to desired neighbor
    #fig = plt.figure()
    #ax = fig.add_subplot(aspect='equal', projection='3d')

    #c = {
    #        i: 'tab:green',
    #        j: 'tab:cyan',
    #}

    #ax.scatter(
    #        neighbors[:,0], neighbors[:,1], neighbors[:,2],
    #        c=[c.get(k, 'tab:grey') for k in range(len(neighbors))],
    #)
    #ax.scatter(
    #        x[0], x[1], x[2],
    #        c='tab:orange',
    #)
    #ax.scatter(
    #        Rx[0], Rx[1], Rx[2],
    #        c='tab:purple',
    #)
    #ax.set_xlabel('x')
    #ax.set_ylabel('y')
    #ax.set_zlabel('z')

    #plt.show()

    return Rx

def sample_neighbor_rot(rng, neighbors, valid_i):
    x = rng.normal(size=3)
    x /= np.linalg.norm(x)

    d = np.linalg.norm(neighbors - x, axis=1)
    i = np.argmin(d)

    j = rng.integers(len(neighbors))

    R, *_ = Rotation.align_vectors(neighbors[j], neighbors[i])
    Rx = R.as_matrix() @ x
    
    return Rx

def iter_random_coords():
    while True:
        x = rng.normal(size=(20,3))
        d = np.linalg.norm(x, axis=1)
        x /= d.reshape(-1, 1)

        yield x

        # It might save some time to yield all possible 90° rotations of the 
        # normalized random vectors here...

rng = np.random.default_rng()
#neighbors = mmt.cube_faces()
neighbors = mmt.icosahedron_faces()
valid_i = [3,4]

n = len(neighbors)
R = np.zeros((n,n,3,3))
kd_tree = KDTree(neighbors)

for i, j in product(range(n), repeat=2):
    Rij, *_ = Rotation.align_vectors(neighbors[j], neighbors[i])
    R[i,j] = Rij.as_matrix()

for _ in timerit:
    sample_neighbor_rot_precalc(rng, neighbors, valid_i)

for _ in timerit:
    sample_neighbor_rot(rng, neighbors, valid_i)

for _ in timerit:
    sample_neighbor_kd_tree(rng, neighbors, valid_i)

for _ in timerit:
    sample_neighbor_dist_matrix(rng, neighbors, valid_i)

