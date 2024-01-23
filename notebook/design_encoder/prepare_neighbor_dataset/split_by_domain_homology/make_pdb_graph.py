#!/usr/bin/env python3

import pickle
import networkx as nx
from itertools import combinations

with open('pdb_interpro_mmseqs2_graph.pkl', 'rb') as f:
    g = pickle.load(f)

groups = list(nx.connected_components(g))
n_groups = len(groups)

for i, group in enumerate(groups):
    for node in group:
        g.nodes[node]['group'] = i

def count_pdb_nodes(g, nodes=None):
    return sum(g.nodes[k]['type'] == 'pdb' for k in nodes or g.nodes)

group_sizes = {
        i: count_pdb_nodes(g, nodes)
        for i, nodes in enumerate(groups)
}

h = nx.Graph()
for k in g.nodes:
    if g.nodes[k]['type'] == 'pdb':
        h.add_node(k)

    if g.nodes[k]['type'] in ('mmseqs2', 'interpro'):
        for k1, k2 in combinations(g.neighbors(k), 2):
            h.add_edge(k1, k2)

with open('pdb_graph.pkl', 'wb') as f:
    pickle.dump(h, f)
