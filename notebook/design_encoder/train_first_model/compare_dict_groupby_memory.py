#!/usr/bin/env python3

# I can use either a dictionary or a groupby object to pre-sort the origins by 
# their tags.  A dictionary is slightly faster, but this script shows that it 
# requires substantially more memory.

from atompaint.transform_pred.datasets.neighbor_count import load_origins
from pympler.asizeof import asizeof
from pathlib import Path

df = load_origins(Path('origins'))
g = df.groupby('tag')
d = {k: v for k, v in g}

debug(
        asizeof(df),
        asizeof(df, g),
        asizeof(df, d),
)

# Output:
# asizeof(df): 3471939184 (int)
# asizeof(df, g): 3737796504 (int)
# asizeof(df, d): 8013642560 (int)
