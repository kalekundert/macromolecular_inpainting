#!/usr/bin/env python3

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os

from prody import parsePDB
from pathlib import Path
from tqdm import tqdm

TERM_DIR = Path(os.environ['TERM_DIR'])

def get_bounding_box_dims(xyz):
    return np.max(xyz, axis=0) - np.min(xyz, axis=0)

bboxes = []

for pdb_path in tqdm(list(TERM_DIR.glob('TERMs/000/*.pdb'))):
    atoms = parsePDB(str(pdb_path))
    xyz = atoms.getCoords()
    bbox = get_bounding_box_dims(xyz)
    bboxes.append(bbox)

bboxes = np.array(bboxes)

debug(
        len(bboxes),
        np.median(bboxes),
        np.mean(bboxes),
)

sns.kdeplot(bboxes.flatten())

plt.savefig('get_term_bbox_dims.svg')
plt.show()
