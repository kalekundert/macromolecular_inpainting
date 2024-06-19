#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from atom3d_menagerie.data.smp import QUANTUM_PROPS
from joblib import Memory
from pathlib import Path

memory = Memory('cache')

@memory.cache
def load_smp_data():
    from atom3d.datasets import LMDBDataset
    from atom3d_menagerie.data.smp import QUANTUM_PROPS
    from pathlib import Path
    from tqdm import tqdm

    db_path = Path('/home/kale/research/databases/atom3d_smp/data_5A')

    data = LMDBDataset(db_path / 'val')

    rows = []

    for item in tqdm(data):
        row = {
                k: item['labels'][i]
                for k, i in QUANTUM_PROPS.items()
        }
        row['num_atoms'] = len(item['atoms'])
        rows.append(row)

    return pd.DataFrame(rows)


df = load_smp_data()

plt.figure(figsize=(12, 12))

for i, k in enumerate(QUANTUM_PROPS, start=1):
    plt.subplot(5, 4, i)
    plt.title(k)
    sns.scatterplot(df, x='num_atoms', y=k)

plt.tight_layout()
plt.savefig(Path(__file__).with_suffix('.svg'))
plt.show()
