#!/usr/bin/env python3

import pickle
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations

with open('pdb_graph.pkl', 'rb') as f:
    h = pickle.load(f)

groups = list(nx.connected_components(h))
n_groups = len(groups)

x = list(range(n_groups))
y = sorted(len(x) for x in groups)[::-1]

debug(len(h), len(groups), y[:20])

plt.plot(x, y)
plt.xlabel('component')
plt.ylabel('size')

ax = plt.gca().inset_axes(
        [0.25, 0.25, 0.72, 0.72],
        xlim=(0, 250), ylim=(0, 100),
)
ax.plot(x, y)

df = pd.DataFrame({'group': x, 'size': y})
df['size_percent'] = 100 * df['size'] / len(h)
df.head().to_excel('pdb_graph_component_sizes.xlsx', index=False)

plt.savefig('pdb_graph_component_sizes.svg')
plt.show()

# ag = nx.nx_agraph.to_agraph(g)

# norm = Normalize(0, n_groups)
# sm = ScalarMappable(norm=norm, cmap=m_rainbow)

# for node in ag.nodes():
#     if node.attr['type'] == 'pdb':
#         node.attr['shape'] = 'box'

#         c = sm.to_rgba(float(node.attr['group']))
#         node.attr['style'] = 'filled'
#         node.attr['fillcolor'] = to_hex(c)
#         node.attr['fontcolor'] = choose_foreground_color(c)

#     if node.attr['type'] == 'interpro':
#         node.attr['label'] = ''
#         node.attr['shape'] = 'circle'
#         node.attr['width'] = 0.1

# ag.layout(prog='fdp')
# ag.draw('g.png')



