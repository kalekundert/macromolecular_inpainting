#!/usr/bin/env python3

import lmdb
import json
import io
import gzip
import pandas as pd
import numpy as np

from atom3d.datasets import LMDBDataset
from atom3d.util.voxelize import get_center
from pathlib import Path
from shutil import rmtree
from tqdm import tqdm

def make_pruned_dataset(in_path, out_path):
    print("input: ", in_path)
    print("output:", out_path)

    if out_path.is_dir():
        rmtree(out_path)

    env_in = lmdb.open(str(in_path), readonly=True)
    env_out = lmdb.open(str(out_path), map_size=int(1e11))

    with env_in.begin() as txn_in, env_out.begin(write=True) as txn_out:
        num_examples_in = int(txn_in.get(b'num_examples'))
        serialization_format = txn_in.get(b'serialization_format')
        assert serialization_format == b'json'

        num_examples_out = 0
        id_to_idx_out = {}
        idx_out = 0

        for idx_in in tqdm(range(num_examples_in)):
            key_in = str(idx_in).encode()
            value = txn_in.get(key_in)
            id, atoms = extract_id_atoms(value)

            if calc_max_dist(atoms) > 5:
                continue

            key_out = str(idx_out).encode()
            num_examples_out += 1
            id_to_idx_out[id] = idx_out
            idx_out += 1

            if not txn_out.put(key_out, value, overwrite=False):
                raise RuntimeError(f"failed to add {key_out!r} to {out_path}")

        num_discarded = num_examples_in - num_examples_out
        print(f"discarded {num_discarded} molecules ({100 * num_discarded / num_examples_in:.2f}%)")

        txn_out.put(b'num_examples', str(num_examples_out).encode())
        txn_out.put(b'serialization_format', serialization_format)
        txn_out.put(b'id_to_idx', json.dumps(id_to_idx_out).encode())



def extract_id_atoms(compressed):
    buf = io.BytesIO(compressed)

    with gzip.GzipFile(fileobj=buf, mode="rb") as f:
        serialized = f.read()

    item = json.loads(serialized)

    return item['id'], pd.DataFrame(**item['atoms'])

def calc_max_dist(atoms):
    xyz = atoms[['x', 'y', 'z']]
    xyz = xyz - get_center(xyz)

    dists = np.linalg.norm(xyz, ord=2, axis=1)
    return np.max(dists)


in_path = Path('/home/kale/research/databases/atom3d_smp/data')
out_path = Path('/home/kale/research/databases/atom3d_smp/data_5A')
splits = ['train', 'val', 'test']

if __name__ == '__main__':
    for split in splits:
        print(f"pruning the {split!r} split")
        make_pruned_dataset(in_path / split, out_path / split)
        print()
