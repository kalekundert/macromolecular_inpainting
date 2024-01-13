#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from intersect_utils import *

rng = np.random.default_rng(0)
grid = Grid(1)
sphere = Sphere([0, 0, 0], 1)
cells = find_possibly_overlapping_cells(grid, sphere)

ref = estimate_true_intersection(rng, cells, sphere)
pred = predict_analytical_strobl(cells, sphere)

debug(
        ref.normalized_counts,
        pred,
        np.sum(ref.normalized_counts),
        np.sum(pred),
)

plot_prediction(ref, pred)
plt.show()
