import numpy as np
import polars as pl
import networkx as nx
import matplotlib.pyplot as plt

from macromol_census import read_cif, extract_dataframe
from sklearn.neighbors import KDTree
from dataclasses import dataclass
from more_itertools import one, flatten
from tqdm import tqdm
from math import pi

gbmr4_alphabet = {
        'ALA': 'POL',
        'ASP': 'POL',
        'LYS': 'POL',
        'GLU': 'POL',
        'ARG': 'POL',
        'ASN': 'POL',
        'THR': 'POL',
        'SER': 'POL',
        'GLN': 'POL',

        'TYR': 'HYP',
        'PHE': 'HYP',
        'LEU': 'HYP',
        'ILE': 'HYP',
        'VAL': 'HYP',
        'MET': 'HYP',
        'CYS': 'HYP',
        'TRP': 'HYP',
        'HIS': 'HYP',

        'GLY': 'GLY',

        'PRO': 'PRO',
}
liang2022_alphabet = {
        'ASP': 'DE',
        'GLU': 'DE',

        'SER': 'ST',
        'THR': 'ST',

        'ARG': 'RK',
        'LYS': 'RK',

        'PHE': 'FY',
        'TYR': 'FY',

        'ILE': 'IV',
        'VAL': 'IV',

        'ALA': 'A',
        'ASN': 'N',
        'GLN': 'Q',
        'LEU': 'L',
        'MET': 'M',
        'CYS': 'C',
        'TRP': 'W',
        'HIS': 'H',
        'GLY': 'G',
        'PRO': 'P',
}

def load_atoms(path):
    cif = read_cif(path)
    return (
            extract_dataframe(
                cif, 'atom_site',
                required_cols=[
                    'label_seq_id',
                    'label_comp_id',
                    'label_atom_id',
                    'Cartn_x',
                    'Cartn_y',
                    'Cartn_z',
                ],
            )
            .rename({
                'label_seq_id': 'resi',
                'label_comp_id': 'resn',
                'label_atom_id': 'name',
                'Cartn_x': 'x',
                'Cartn_y': 'y',
                'Cartn_z': 'z',
            })
            .with_columns(
                pl.int_range(pl.len()).alias('i'),
                pl.col('resi').cast(int),
                pl.col('resn').replace(gbmr4_alphabet).alias('resn_gbmr4'),
                pl.col('resn').replace(liang2022_alphabet).alias('resn_liang2022'),
                pl.col('x', 'y', 'z').cast(float),
            )
            .drop_nulls('resi')

            # This filter doesn't do anything, because none of these ligands 
            # have residue numbers, so they're removed by the above 
            # `drop_nulls()`.  But for future reference, I'll want something 
            # like this.
            .filter(
                ~pl.col('resn').is_in(['PE5', 'AB3', 'SO4', 'HOH', 'P33'])
            )
    )

def get_ca_coord(atoms, resi):
    return (
            atoms
            .filter(
                (pl.col('resi') == resi) & (pl.col('name') == 'CA')
            )
            .select(
                pl.concat_list('x', 'y', 'z')
            )
            .item()
            .to_numpy()
    )

def make_kd_tree(atoms):
    x = atoms.select('x', 'y', 'z').to_numpy()
    return KDTree(x)

def calc_sphere_overlap(r, d):
    return (pi / 12) * (4 * r + d) * (2 * r - d)**2

def calc_atom_overlaps(atoms, kd, r):
    neighbors, distances = kd.query_radius(
            kd.data,
            2 * r,
            return_distance=True,
    )
    return (
            pl.DataFrame(
                data={
                    'atom_i': atoms['i'],
                    'resi_i': atoms['resi'],
                    'atom_j': neighbors.tolist(),
                    'distance': distances.tolist(),
                },
            )
            .lazy()
            .explode(['atom_j', 'distance'])
            .join(
                atoms.lazy().select(atom_j='i', resi_j='resi'),
                on='atom_j',
            )
            .filter(
                pl.col('resi_i') != pl.col('resi_j'),
            )
            .with_columns(
                overlap=calc_sphere_overlap(r, pl.col('distance'))
            )
            .collect()
    )

def calc_resi_overlaps(overlaps, kd, center, r):
    atom_i = one(kd.query_radius(center.reshape(1, -1), r))
    atom_i = pl.from_numpy(atom_i, schema=['atom_i'])
    return (
            overlaps
            #.filter(pl.col('atom_i').is_in(atom_i))
            .join(atom_i, on='atom_i')
            .group_by('resi_i', 'resi_j')
            .agg(pl.col('overlap').sum(), pl.col('distance').min())
    )

def make_overlap_graph(overlaps, p):
    g = nx.Graph()
    g.add_edges_from(
            overlaps
            .filter(p.edge_expr)
            #.filter(pl.col('overlap') > p.overlap_threshold_A3)
            #.filter(pl.col('distance') < p.distance_threshold_A)
            .select('resi_i', 'resi_j')
            .iter_rows()
    )
    resns = atoms.group_by('resi').agg(p.node_expr.first())
    resn_map = {k: v for k, v in resns.iter_rows() if k in g.nodes}
    nx.set_node_attributes(g, resn_map, 'resn')
    return g, resn_map

def make_fingerprint(n, subgraph_hashes):
    fp = np.zeros(n, dtype=bool)

    #for h in flatten(subgraph_hashes.values()):
    for hs in subgraph_hashes.values():
        h = hs[-1]
        i = int(h, base=16) % n
        fp[i] = True

    return np.packbits(fp)

def make_grid(atoms, resolution_A):

    def get_span(max, min):
        r = resolution_A
        return r * ((pl.col(max) - pl.col(min)) / r).round()

    dim = (
            atoms
            .select(
                x_min=pl.col('x').min(),
                x_max=pl.col('x').max(),
                x_mean=pl.col('x').mean(),

                y_min=pl.col('y').min(),
                y_max=pl.col('y').max(),
                y_mean=pl.col('y').mean(),

                z_min=pl.col('z').min(),
                z_max=pl.col('z').max(),
                z_mean=pl.col('z').mean(),
            )
            .with_columns(
                x_span=get_span('x_max', 'x_min'),
                y_span=get_span('y_max', 'y_min'),
                z_span=get_span('z_max', 'z_min'),
            )
            .with_columns(
                x_start=(pl.col('x_mean') - pl.col('x_span')) / 2,
                x_stop=(pl.col('x_mean') + pl.col('x_span')) / 2,

                y_start=(pl.col('y_mean') - pl.col('y_span')) / 2,
                y_stop=(pl.col('y_mean') + pl.col('y_span')) / 2,

                z_start=(pl.col('z_mean') - pl.col('z_span')) / 2,
                z_stop=(pl.col('z_mean') + pl.col('z_span')) / 2,
            )
            .row(0, named=True)
    )

    x = np.arange(dim['x_start'], dim['x_stop'], resolution_A)
    y = np.arange(dim['y_start'], dim['y_stop'], resolution_A)
    z = np.arange(dim['z_start'], dim['z_stop'], resolution_A)

    gx, gy, gz = np.meshgrid(x, y, z)
    return np.column_stack([gx.flat, gy.flat, gz.flat])


def calc_tanimoto_similarity(fp1, fp2):
    a = np.bitwise_and(fp1, fp2)
    b = np.bitwise_or(fp1, fp2)

    # The `bitwise_count()` function will be added in the next version of 
    # numpy, see #21429.
    #a = np.bitwise_count(a).sum()
    #b = np.bitwise_count(b).sum()

    a = sum(map(lambda x: x.bit_count(), a))
    b = sum(map(lambda x: x.bit_count(), b))

    return a / b

def calc_fingerprint_density(fp):
    a = sum(map(lambda x: x.bit_count(), fp))
    return a / (len(fp) * fp.nbytes)

def make_fingerprint_database(atoms, p, subset, offset=0):
    kd = make_kd_tree(atoms)
    overlaps = calc_atom_overlaps(atoms, kd, p.overlap_radius_A)

    rows = []

    for atom in atoms.filter(subset).iter_rows(named=True):
        c = np.array([atom['x'], atom['y'], atom['z']]) + offset
        df = calc_resi_overlaps(overlaps, kd, c, p.graph_radius_A)
        g, resn_map = make_overlap_graph(df, p)
        hs = nx.weisfeiler_lehman_subgraph_hashes(
                g,
                node_attr='resn',
                iterations=p.subgraph_depth,
        )
        fp = make_fingerprint(p.fingerprint_size, hs)

        rows.append({
            'resi': atom['resi'],
            'name': atom['name'],
            'fingerprint': fp,
            'fingerprint_density': calc_fingerprint_density(fp),
            'edges/nodes': g.number_of_edges() / g.number_of_nodes(),
        })

    return pl.DataFrame(rows)

def select_ca(atoms):
    return atoms.filter(pl.col('name') == 'CA')

@dataclass
class Params:
    graph_radius_A: float
    overlap_radius_A: float
    overlap_threshold_A3: float
    distance_threshold_A: float
    edge_expr: object
    node_expr: object
    subgraph_depth: int
    fingerprint_size: int

if __name__ == '__main__':

    # Chose overlap parameters by looking for flat areas in the CDF.
    p = Params(
            graph_radius_A = 8,
            overlap_radius_A = 4,
            overlap_threshold_A3 = 750,
            distance_threshold_A = 3,
            edge_expr = pl.col('overlap') > 750,
            #edge_expr = pl.col('distance') < 4,
            node_expr = pl.col('resn_liang2022'),
            subgraph_depth = 1,
            fingerprint_size = 512,
    )

    atoms = load_atoms('1n5d.cif.gz')
    db1 = make_fingerprint_database(atoms, p, pl.col('name') == 'CA')

    atoms = load_atoms('1wma.cif.gz')
    db2 = make_fingerprint_database(atoms, p, pl.col('name') == 'CA', 1)

    print(db1)
    print(db2)

    grid = make_grid(atoms, 5)
    print(grid.shape)

    x = np.zeros((db1.height, db2.height))

    for i, fp_i in enumerate(db1['fingerprint']):
        for j, fp_j in enumerate(db2['fingerprint']):
            x[i,j] = calc_tanimoto_similarity(fp_i, fp_j)

    plt.matshow(x, vmin=0, vmax=1)
    plt.ylabel('1nd5')
    plt.xlabel('1wma')
    plt.show()

    # debug(fp1, fp2, calc_tanimoto_similarity(fp1, fp2))

    # plt.subplot(1, 2, 1)
    # nx.draw(g1, with_labels=True, labels=resn_map1)
    # plt.subplot(1, 2, 2)
    # nx.draw(g2, with_labels=True, labels=resn_map2)
    # plt.show()


