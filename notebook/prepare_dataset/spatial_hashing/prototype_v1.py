import numpy as np
import polars as pl
import networkx as nx
import matplotlib.pyplot as plt

from macromol_census import read_cif, extract_dataframe
from scipy.spatial import KDTree

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
                pl.col('x', 'y', 'z').cast(float),
            )
            .drop_nulls('resi')
    )

def get_ca_coord(df, resi):
    return (
            df
            .filter(
                (pl.col('resi') == resi) & (pl.col('name') == 'CA')
            )
            .select(
                pl.concat_list('x', 'y', 'z')
            )
            .item()
            .to_numpy()
    )

def make_resi_graph(df_xyz, center, radius=8, neighbor_dist=4):
    df_dist = (
            df_xyz
            .with_columns(
                d=(
                    (pl.col('x') - center[0])**2 + 
                    (pl.col('y') - center[1])**2 + 
                    (pl.col('z') - center[2])**2
                ).sqrt()
            )
            .filter(
                pl.col('d') < radius
            )
            .filter(
                (pl.len() >= 4).over('resi')
            )
            .sort('resi')
    )

    x = df_dist.select('x', 'y', 'z').to_numpy()

    kd = KDTree(x)

    g = nx.Graph()

    def resi_pairs(ij):
        for i, j in ij:
            yield df_dist.item(i, 'resi'), df_dist.item(j, 'resi')

    g.add_edges_from(
            (i, j)
            for i, j in resi_pairs(kd.query_pairs(r=neighbor_dist))
            if i != j
    )

    return g

if __name__ == '__main__':
    radius = 7
    #resi_center = 86  # beta sheet
    resi_center = 200  # alpha


    for nd in np.linspace(3, 5, 11):
        df1 = load_atoms('1n5d.cif.gz')
        c1 = get_ca_coord(df1, resi_center)
        g1 = make_resi_graph(df1, c1, radius=radius, neighbor_dist=nd)
        h1 = nx.weisfeiler_lehman_graph_hash(g1)

        df2 = load_atoms('1wma.cif.gz')
        c2 = get_ca_coord(df2, resi_center)
        g2 = make_resi_graph(df2, c2, radius=radius, neighbor_dist=nd)
        h2 = nx.weisfeiler_lehman_graph_hash(g2)

        iso = nx.is_isomorphic(g1, g2)

        debug(nd, h1, h2, iso)


    # TODO:
    # - Algorithm is too sensitive to small changes in position.  Maybe I can 
    #   improve by requiring multiple contacts below some distance threshold to 
    #   make edge.
    #
    # - Both 86 (beta) and 200 (alpha) work with neighbor distances > 4.6.  So 
    #   maybe I just need to pick the right distance.  I'd like to plot min 
    #   inter-residue distances, to see if there's a bimodal distribution.
    # 
    # - Relate distance cutoff to number of connected components.  I want the 
    #   smallest that mostly gives one component
    #



    nd = 3

    df1 = load_atoms('1n5d.cif.gz')
    c1 = get_ca_coord(df1, resi_center)
    g1 = make_resi_graph(df1, c1, radius=radius, neighbor_dist=nd)
    h1 = nx.weisfeiler_lehman_graph_hash(g1)

    df2 = load_atoms('1wma.cif.gz')
    c2 = get_ca_coord(df2, resi_center)
    g2 = make_resi_graph(df2, c2, radius=radius, neighbor_dist=nd)
    h2 = nx.weisfeiler_lehman_graph_hash(g2)

    plt.subplot(1, 2, 1)
    nx.draw(g1, with_labels=True)
    plt.subplot(1, 2, 2)
    nx.draw(g2, with_labels=True)
    plt.show()


