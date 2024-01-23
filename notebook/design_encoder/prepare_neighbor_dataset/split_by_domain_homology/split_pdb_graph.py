#!/usr/bin/env python3

import pickle
import networkx as nx
import random
import matplotlib.pyplot as plt

from dataclasses import dataclass, field
from more_itertools import one
from tqdm import tqdm

@dataclass
class Components:
    node_map: dict = field(default_factory=dict)
    nodes: dict[int, set] = field(default_factory=dict)

def add_nodes(g, c, nodes, max_len, fill=False):
    assert len(c.node_map) + len(nodes) == len(g)

    skipped = []

    for cursor, k1 in tqdm(list(enumerate(nodes))):
        membership = set()

        for k2 in g.neighbors(k1):

            try:
                i = c.node_map[k2]
            except KeyError:
                continue

            membership.add(i)

        if sum(len(c.nodes[i]) for i in membership) + 1 > max_len:
            skipped.append(k1)
            continue

        elif len(membership) == 0:
            i = max(c.nodes, default=0) + 1
            c.node_map[k1] = i
            c.nodes[i] = {k1}

        elif len(membership) == 1:
            i = one(membership)
            c.node_map[k1] = i
            c.nodes[i].add(k1)

        else:
            membership = sorted(membership)
            i = membership[0]
            c.node_map[k1] = i
            c.nodes[i].add(k1)

            for j in membership[1:]:
                nodes_j = c.nodes.pop(j)
                c.nodes[i] |= nodes_j
                for k in nodes_j:
                    c.node_map[k] = i

    return c, skipped

def pop_biggest_component(c):
    i_max = max(c.nodes, key=lambda k: len(c.nodes[k]))
    nodes = c.nodes.pop(i_max)

    for k in nodes:
        del c.node_map[k]

    return nodes

def pop_until_n_remain(c, n):
    nodes = []
    while (not nodes) or len(c.node_map) > n:
        nodes += pop_biggest_component(c)
    return nodes


if __name__ == '__main__':
    with open('h.pkl', 'rb') as f:
        h = pickle.load(f)

    c = Components()
    n = 100
    traj = []

    nodes = list(h.nodes)

    for i in tqdm(list(range(n))):

        random.shuffle(nodes)

        c, nodes_skipped = add_nodes(h, c, nodes, max_len=0.6 * len(h))

        traj.append(len(c.node_map))

        pop_limit = len(h) * 0.5 * (n - i) / n
        nodes_popped = pop_until_n_remain(c, pop_limit)

        nodes = nodes_skipped + nodes_popped

    plt.plot(range(n), traj)
    plt.axhline(len(h), ls='--', color='k')
    plt.ylim(0, 1.1 * len(h))
    plt.ylabel('nodes kept')
    plt.xlabel('annealing step')

    plt.savefig('split_pdb_graph.svg')
    plt.show()
