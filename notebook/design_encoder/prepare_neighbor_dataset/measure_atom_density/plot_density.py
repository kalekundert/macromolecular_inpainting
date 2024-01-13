import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from atompaint.datasets.transform_pred.neighbor_count import load_origins
from scipy.stats import gaussian_kde
from collections import Counter
from pathlib import Path

df = load_origins(Path('origins'))

print(df.describe())

#kde = gaussian_kde(df['weight'])

#x = np.linspace(df['weight'].min(), df['weight'].max(), 500)

#y = kde(x)

#plt.plot(x, y)
#plt.show()

w = df['weight'].round().astype(int)
c = Counter(w)

x = sorted(c.keys())
y = [c[k] for k in x]

# Could also make a CDF, then take numeric derivative to get PDF...
# Avoid needing to round everything.
#
# - pd.sort
# - pd.cumsum
# - numeric derivative...

#sns.swarmplot(data=df, x='weight', size=0.5)

plt.plot(x, y)
plt.show()

