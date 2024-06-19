import macromol_dataframe as mmdf
import numpy as np

from sklearn.neighbors import KDTree
from sklearn.decomposition import PCA
from itertools import product
from more_itertools import one
from math import pi, ceil

def make_kd_tree(atoms):
    return KDTree(mmdf.get_atom_coords(atoms))

def calc_zone_centers_A(atoms, spacing_A: float):
    """
    Choose coordinates for each zone.

    Small proteins are sensitive to this process, because only the most buried 
    regions will have enough atoms to satisfy the density requirements.  This 
    algorithm tries to maximize the chances of including these proteins in the 
    dataset by putting one zone in the exact center of the structure, and 
    aligning the rest to the principal components of the atom coordinates.
    """

    # The variable names in this function use suffixes to identify which frame 
    # coordinates belong to:
    #
    # - `_i`: The input coordinate frame, i.e. the coordinates that are present 
    #   in the input data frame.
    #
    # - `_p`: The coordinate frame defined by a principal components analysis 
    #   (PCA) of the input coordinates.  In this frame, the x-axis is the 
    #   direction of most variation.
    #
    # Note that all coordinates are in units of angstroms.  Normally this is 
    # indicated by the suffix `_A`, but here it's more important to use the 
    # suffix to keep track of the coordinate frame.

    coords_i = mmdf.get_atom_coords(atoms)

    pca = PCA()
    pca.fit(coords_i)
    frame_ip = pca.components_

    coords_p = coords_i @ frame_ip.T

    def get_axis_p(i):
        low_p = coords_p[:,i].min()
        mid_p = coords_p[:,i].mean()
        high_p = coords_p[:,i].max()

        # We can subtract half the spacing from either end because the 
        # coordinates we're calculating are the centers of the zones.  So any 
        # atoms within half the spacing of the last zone coordinate will still 
        # fall in that zone.
        span_high = high_p - mid_p - (spacing_A / 2)
        span_low =   mid_p - low_p - (spacing_A / 2)

        steps_high = int(ceil(span_high / spacing_A))
        steps_low = int(ceil(span_low / spacing_A))

        start_p = mid_p - (steps_low * spacing_A)

        for i in range(steps_low + steps_high + 1):
            yield start_p + i * spacing_A

    zones_p = np.vstack(
            list(product(
                get_axis_p(0),
                get_axis_p(1),
                get_axis_p(2),
            ))
    )

    return zones_p @ frame_ip
def calc_density_atoms_nm3(atoms, kd_tree, center_A, radius_A):
    atoms = select_nearby_atoms(
            atoms,
            kd_tree,
            center_A,
            radius_A,
    )
    volume_nm3 = calc_sphere_volume_nm3(radius_A)
    return atoms['occupancy'].sum() / volume_nm3

def calc_sphere_volume_nm3(radius_A):
    return 4/3 * pi * (radius_A / 10)**3
def select_nearby_atoms(atoms, kd_tree, center_A, radius_A):
    center_A = center_A.reshape(1, 3)
    i = one(kd_tree.query_radius(center_A, radius_A))
    return atoms[i]

