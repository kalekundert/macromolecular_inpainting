#!/usr/bin/env python3

from atom3d.datasets import LMDBDataset
from pathlib import Path
from tqdm import tqdm

from make_5A_smp_dataset import calc_max_dist

db_path = Path('/home/kale/research/databases/atom3d_smp/data_5A')
splits = ['train', 'val', 'test']

for split in splits:
    print(db_path / split)

    data = LMDBDataset(db_path / split)

    for item in tqdm(data):
        assert item is not None
        assert calc_max_dist(item['atoms']) <= 5

