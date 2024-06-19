# - Load atoms into dataframe
# - Make KD tree for all atoms
# - Find atoms within ≈10Å of query
# - Find indices/distances of atoms within contact distance of above selection
#   - sklearn.KDTree.query_radius() provides this info
# - Join atoms, indices, and distances into dataframe
# - Calculate sphere overlap
# - Sum over each residue pair.
# - Filter on some threshold
# - Add remaining pairs to graph.
#
#
# Alternatively:
# - Sample a bunch of query points.
# - For each query, calculate sphere overlaps as above
# - Plot histogram

import numpy as np
import polars as pl
import networkx as nx
import seaborn as sns
import matplotlib.pyplot as plt

from prototype_v1 import load_atoms, get_ca_coord
from macromol_census import read_cif, extract_dataframe
from sklearn.neighbors import KDTree
from more_itertools import one
from tqdm import tqdm
from math import pi

def make_kd_tree(atoms):
    x = atoms.select('x', 'y', 'z').to_numpy()
    return KDTree(x)

def calc_sphere_overlap(r, d):
    return (pi / 12) * (4 * r + d) * (2 * r - d)**2

def make_query(atoms, kd, center, r):
    i = kd.query_radius(center.reshape(1, -1), r)
    return one(i)

def calc_resi_overlaps(query_i, atoms, kd, r):
    query_atoms = atoms[query_i]
    query_resis = query_atoms.lazy().select('i', 'resi')
    query_xyz = query_atoms.select('x', 'y', 'z').to_numpy()

    neighbors, distances = kd.query_radius(
            query_xyz,
            2 * r,
            return_distance=True,
    )
    return (
            pl.DataFrame(
                data={
                    'atom_i': query_i,
                    'atom_j': neighbors.tolist(),
                    'distance': distances.tolist(),
                },
            )
            .lazy()
            .explode(['atom_j', 'distance'])
            .with_columns(
                overlap=calc_sphere_overlap(r, pl.col('distance'))
            )
            .join(query_resis, left_on='atom_i', right_on='i')
            .join(query_resis, left_on='atom_j', right_on='i')
            .select(
                resi_i='resi',
                resi_j='resi_right',
                overlap='overlap',
            )
            .group_by('resi_i', 'resi_j')
            .sum()
            .filter(
                pl.col('resi_i') != pl.col('resi_j'),
            )
            .collect()
    )

def make_overlap_graph(overlaps):
    g = nx.Graph()
    g.add_edges_from(
            overlaps
            .filter(pl.col('overlap') > overlap_threshold_A3)
            .select('resi_i', 'resi_j')
            .iter_rows()
    )
    resns = atoms.group_by('resi').agg(pl.col('resn_gbmr4').first())
    resn_map = {k: v for k, v in resns.iter_rows() if k in g.nodes}
    nx.set_node_attributes(g, resn_map, 'resn')

if __name__ == '__main__':
    atoms = load_atoms('1n5d.cif.gz')
    #atoms = load_atoms('1wma.cif.gz')
    kd = make_kd_tree(atoms)

    # results = []
    # q = np.arange(atoms.height)

    # for r in tqdm(np.linspace(3, 6, 15)):
    #     results.append(
    #             calc_resi_overlaps(q, atoms, kd, r)
    #             .with_columns(
    #                 r=r,
    #                 adj=(pl.col('resi_i') - pl.col('resi_j')).abs() == 1,
    #             )
    #     )

    # # If I could quantify bimodality, I could optimize r...

    # df = pl.concat(results)

    # sns.displot(
    #         df,
    #         x='overlap',
    #         hue='adj',
    #         col='r',
    #         col_wrap=5,
    #         kind='ecdf',
    # )
    # plt.savefig('sphere_overlap_dist.svg')
    # plt.show()

    ###

    r = 6
    c1 = get_ca_coord(atoms, 57)
    c2 = get_ca_coord(atoms, 152)

    # Chose these by looking for flat areas in the CDF.
    overlap_radius_A = 4
    overlap_threshold_A3 = 750

    rows = []

    for t in np.linspace(0, 1, 500):
        c = (c1 * (1 - t)) + (c2 * t)
        d = np.linalg.norm(c - c1)
        q = make_query(atoms, kd, c, r)

        df = calc_resi_overlaps(q, atoms, kd, overlap_radius_A)

        g = nx.Graph()
        g.add_edges_from(
                df
                .filter(pl.col('overlap') > overlap_threshold_A3)
                .select('resi_i', 'resi_j')
                .iter_rows()
        )
        resns = atoms.group_by('resi').agg(pl.col('resn_reduced').first())
        resn_map = {k: v for k, v in resns.iter_rows() if k in g.nodes}
        nx.set_node_attributes(g, resn_map, 'resn')

        h = nx.weisfeiler_lehman_graph_hash(g, node_attr='resn')
        rows.append(dict(d=d, hash=h))

    df = pl.DataFrame(rows)
    print(df)
    print(df.group_by('hash').agg(pl.col('d').max() - pl.col('d').min()).mean())

    #nx.draw(g, with_labels=True, labels=resn_map)
    #plt.show()
