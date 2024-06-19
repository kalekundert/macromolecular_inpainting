#!/usr/bin/env python3

import duckdb
import seaborn as sns
import matplotlib.pyplot as plt

db = duckdb.connect('atom_density.duckdb', read_only=True)
df = db.sql('SELECT atoms_per_nm3 FROM density').pl()
del db

sns.displot(
        df,
        x='atoms_per_nm3',
        binwidth=1,
        #kind='ecdf',
)

plt.savefig('atom_density.svg')
#plt.savefig('atom_density_cdf.svg')
plt.show()

