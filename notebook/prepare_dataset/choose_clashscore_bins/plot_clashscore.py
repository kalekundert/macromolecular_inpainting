#!/usr/bin/env python3

import sys
import duckdb
import seaborn as sns
import matplotlib.pyplot as plt

db = duckdb.connect('mmc_pdb.duckdb')

df = db.sql('SELECT * from quality_clashscore').pl()

kind = sys.argv[1]
sns.displot(
        df,
        x='clashscore',
        kind=kind,
)
plt.xlim(0, 100)
plt.savefig(f'clashscore_{kind}.svg')
plt.show()
