#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import lightning.pytorch as pl
from intersect_utils import *
from equivariant_nn import *

rng = np.random.default_rng(0)
grid = Grid(1)

# sphere = Sphere([0, 0, 0], 1)
# cells = find_possibly_overlapping_cells(grid, sphere)
# x = enn.make_equivariant_nn_inputs(cells, sphere)

model = SphereCubeModel()
# debug(
#         model.linear_1.weights,
#         model.linear_1.bias,
#         model.linear_2.weights,
#         model.linear_2.bias,
#         x,
#         model(x),
# )

dataset = SphereCubeDataset(rng, grid, epoch_size=10)
trainer = pl.Trainer(max_epochs=100)

model = train_equivariant_nn(model, dataset, trainer)

df = run_benchmark(
        ref,
        predict_equivariant_nn,
        predict_kwargs=dict(model=model),
)

plot_benchmark({'equivariant': df})
plt.show()
