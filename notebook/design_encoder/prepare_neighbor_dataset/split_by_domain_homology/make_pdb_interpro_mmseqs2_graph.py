#!/usr/bin/env python

import requests
import networkx as nx
import matplotlib.pyplot as plt
import json
import re
import pickle

from pisces import load_pisces
from requests_cache import CachedSession
from pathlib import Path
from tqdm import tqdm
from colorcet import m_rainbow
from matplotlib.colors import Normalize, to_hex
from matplotlib.cm import ScalarMappable
from more_itertools import ilen
from wellmap.plot import choose_foreground_color

PISCES = Path('/home/kale/research/databases/pisces_2023_05_08')

df = load_pisces(PISCES / 'cullpdb_pc70.0_res0.0-3.0_len40-10000_R0.3_Xray_d2023_05_08_chains37529')

g = nx.Graph()

session = CachedSession('interpro')

n_skipped = 0
n_no_cluster = 0

def get_pdb_id(id_str):
    id_fields = id_str.split('_')
    if len(id_fields[0]) == 4:
        return id_fields[0]
    else:
        return None

pdb_clusters = {}

with open('clusters-by-entity-30.txt') as f:
    for i, cluster in enumerate(f):
        for member in cluster.split():
            pdb_id = get_pdb_id(member)

            if not pdb_id:
                continue

            pdb_clusters[pdb_id] = i

try:
    for i, row in tqdm(list(df.iterrows())):
        pdb_chain = row['PDBchain']
        pdb = pdb_chain[0:4]
        chain = pdb_chain[4:]

        url = f'https://www.ebi.ac.uk/interpro/api/entry/interpro/structure/pdb/{pdb}'
        interpro_response = session.get(url)

        if interpro_response.status_code == 204:
            n_skipped += 1
            continue

        g.add_node(pdb, type='pdb')

        try:
            cluster_id = pdb_clusters[pdb]
        except KeyError:
            n_no_cluster += 1
        else:
            g.add_node(cluster_id, type='mmseqs2')
            g.add_edge(pdb, cluster_id)

        payload = interpro_response.json()

        for entry in payload['results']:
            interpro_id = entry['metadata']['accession']
            g.add_node(interpro_id, type='interpro')
            g.add_edge(pdb, interpro_id)

except KeyboardInterrupt:
    pass

with open('pdb_interpro_mmseqs2_graph.pkl', 'wb') as f:
    pickle.dump(g, f)
