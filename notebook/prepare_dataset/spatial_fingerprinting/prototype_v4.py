import numpy as np
import polars as pl
import networkx as nx
import matplotlib.pyplot as plt

from macromol_census import read_cif, extract_dataframe
from sklearn.neighbors import KDTree
from dataclasses import dataclass
from collections import defaultdict
from more_itertools import one, flatten, pairwise
from tqdm import tqdm
from math import pi

ALPHABETS = {
    'gbmr4': {
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
    },
    'liang2022': {
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
    },
    'raacbook_polarity': {
            'ASP': 'rpL',
            'GLU': 'rpL',
            'ARG': 'rpL',
            'LYS': 'rpL',
            'ASN': 'rpL',
            'GLN': 'rpL',
            'HIS': 'rpL',


            'PRO': 'rpM',
            'ALA': 'rpM',
            'SER': 'rpM',
            'THR': 'rpM',
            'GLY': 'rpM',


            'LEU': 'rpS',
            'ILE': 'rpS',
            'VAL': 'rpS',
            'TYR': 'rpS',
            'PHE': 'rpS',
            'MET': 'rpS',
            'CYS': 'rpS',
            'TRP': 'rpS',
    },
    'raacbook_charge': {
            'ASP': '+',
            'GLU': '+',

            'ARG': '-',
            'LYS': '-',

            'SER': '=',
            'THR': '=',
            'PHE': '=',
            'TYR': '=',
            'ILE': '=',
            'VAL': '=',
            'ALA': '=',
            'ASN': '=',
            'GLN': '=',
            'LEU': '=',
            'MET': '=',
            'CYS': '=',
            'TRP': '=',
            'HIS': '=',
            'GLY': '=',
            'PRO': '=',
    },
    'raacbook_ss': {
            'ALA': 'ALPHA',
            'GLU': 'ALPHA',
            'LEU': 'ALPHA',
            'MET': 'ALPHA',
            'GLN': 'ALPHA',
            'ARG': 'ALPHA',
            'LYS': 'ALPHA',
            'HIS': 'ALPHA',

            'ILE': 'BETA',
            'VAL': 'BETA',
            'TYR': 'BETA',
            'CYS': 'BETA',
            'TRP': 'BETA',
            'PHE': 'BETA',
            'THR': 'BETA',

            'GLY': 'LOOP',
            'ASN': 'LOOP',
            'PRO': 'LOOP',
            'SER': 'LOOP',
            'ASP': 'LOOP',
    },
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
                *[
                    pl.col('resn').replace(v).alias(f'resn_{k}')
                    for k, v in ALPHABETS.items()
                ],
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

def make_fingerprint_database(atoms, p, subset, rng, offset=0):
    print(atoms)
    kd = make_kd_tree(atoms)
    df = calc_resi_overlaps(atoms, kd, p.overlap_radius_A)

    hashes = defaultdict(set)

    for alphabet in ALPHABETS.keys():
        for i in range(20):
            g = make_overlap_graph(df, p, rng)
            hashes_i = nx.weisfeiler_lehman_subgraph_hashes(
                    g,
                    node_attr=f'resn_{alphabet}',
                    iterations=p.subgraph_depth,
            )

            for k in hashes_i:
                hashes[k].add(hashes_i[k][-1])

    rows = []

    for atom in atoms.filter(subset).iter_rows(named=True):
        c = np.array([atom['x'], atom['y'], atom['z']]) + offset
        resis = find_resis_near_point(atoms, kd, c, p.graph_radius_A)
        hs_i = {i: hashes[i] for i in resis}
        fp = make_fingerprint(p.fingerprint_size, hs_i)

        #debug(c, i, hs_i, fp)

        rows.append({
            'resi': atom['resi'],
            'name': atom['name'],
            'fingerprint': fp,
            'fingerprint_density': calc_fingerprint_density(fp),
        })

    return pl.DataFrame(rows)

def make_kd_tree(atoms):
    x = atoms.select('x', 'y', 'z').to_numpy()
    return KDTree(x)

def calc_resi_overlaps(atoms, kd, r):
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
            .group_by('resi_i', 'resi_j')
            .agg(pl.col('overlap').sum(), pl.col('distance').min())
            .collect()
    )

def calc_sphere_overlap(r, d):
    return (pi / 12) * (4 * r + d) * (2 * r - d)**2

def make_overlap_graph(overlaps, p, rng):
    overlaps = (
            overlaps
            .with_columns(
                random=rng.random(overlaps.height),
                boltzmann=((pl.lit(4) - pl.col('distance')) / pl.lit(1.0)).exp(),
            )
    )

    g = nx.Graph()
    g.add_edges_from(
            overlaps
            .filter(
                pl.col('boltzmann') > pl.col('random')
            )
            .select('resi_i', 'resi_j')
            .iter_rows()
    )

    for alphabet in ALPHABETS:
        node_col = f'resn_{alphabet}'
        node_attrs_df = (
                atoms
                .group_by('resi')
                .agg(pl.col(node_col).first())
        )
        node_attrs = {
                k: v
                for k, v in node_attrs_df.iter_rows()
                if k in g.nodes
        }
        nx.set_node_attributes(g, node_attrs, node_col)

    return g

def find_resis_near_point(atoms, kd, c, r):
    i = one(kd.query_radius(c.reshape(-1, 3), r))
    return atoms['resi', i].unique()

def make_fingerprint(n, subgraph_hashes):
    fp = np.zeros(n, dtype=bool)

    for h in flatten(subgraph_hashes.values()):
    # for hs in subgraph_hashes.values():
    #     h = hs[-1]
        i = int(h, base=16) % n
        fp[i] = True

    return np.packbits(fp)

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

def select_ca(atoms):
    return atoms.filter(pl.col('name') == 'CA')
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

@dataclass
class Params:
    graph_radius_A: float
    overlap_radius_A: float
    overlap_threshold_A3: float
    distance_threshold_A: float
    edge_expr: object
    node_cols: list[str]
    subgraph_depth: int
    fingerprint_size: int

if __name__ == '__main__':

    rng = np.random.default_rng()

    # Chose overlap parameters by looking for flat areas in the CDF.
    p = Params(
            graph_radius_A = 8,
            overlap_radius_A = 4,
            overlap_threshold_A3 = 750,
            distance_threshold_A = 3,
            edge_expr = pl.col('overlap') > 750,
            #edge_expr = pl.col('distance') < 4,
            node_cols = ['resn_liang2022', 'resn_gbmr4'],
            subgraph_depth = 1,
            fingerprint_size = 1024,
    )

    atoms = load_atoms('1n5d.cif.gz')
    db1 = make_fingerprint_database(
            atoms, p,
            #(pl.col('name') == 'CA') & (pl.col('resi').is_in([130, 131])),
            pl.col('name') == 'CA',
            rng,
    )


    atoms = load_atoms('1wma.cif.gz')
    db2 = make_fingerprint_database(
            atoms, p,
            pl.col('name') == 'CA', 
            rng,
            offset=0,
    )

    # d = {}

    # for a, b in pairwise(db1.iter_rows(named=True)):
    #     k = a['resi'], b['resi']
    #     v = calc_tanimoto_similarity(a['fingerprint'], b['fingerprint'])
    #     d[k] = v

    # debug(d)

    plt.subplot(1, 2, 1)

    x = np.zeros((db1.height, db1.height))

    for i, fp_i in enumerate(db1['fingerprint']):
        for j, fp_j in enumerate(db1['fingerprint']):
            x[i,j] = calc_tanimoto_similarity(fp_i, fp_j)

    plt.imshow(x, vmin=0, vmax=1)
    plt.ylabel('1n5d')
    plt.xlabel('1n5d')

    plt.subplot(1, 2, 2)

    x = np.zeros((db1.height, db2.height))

    for i, fp_i in enumerate(db1['fingerprint']):
        for j, fp_j in enumerate(db2['fingerprint']):
            x[i,j] = calc_tanimoto_similarity(fp_i, fp_j)

    plt.imshow(x, vmin=0, vmax=1)
    plt.ylabel('1n5d')
    plt.xlabel('1wma')

    plt.show()

    # debug(fp1, fp2, calc_tanimoto_similarity(fp1, fp2))

    # plt.subplot(1, 2, 1)
    # nx.draw(g1, with_labels=True, labels=resn_map1)
    # plt.subplot(1, 2, 2)
    # nx.draw(g2, with_labels=True, labels=resn_map2)
    # plt.show()


