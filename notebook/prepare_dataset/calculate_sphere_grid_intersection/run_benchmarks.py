#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from intersect_utils import *
from equivariant_nn import *

rng = np.random.default_rng(0)
grid = Grid(1)
ref = estimate_true_intersections(rng, grid)

model = SphereCubeModel()
dataset = SphereCubeDataset(rng, grid, epoch_size=1000)
trainer = pl.Trainer(max_epochs=100)
model = train_equivariant_nn(model, dataset, trainer)

benchmarks = {
        'analytical': run_benchmark(
            ref,
            predict_analytical_strobl,
        ),
        'gaussian': run_benchmark(
            ref,
            predict_gaussian_std,
            predict_kwargs=partial(
                fit_gaussian_std,
                loss=dirichlet_log_p_loss,
            ),
        ),
        'equivariant': run_benchmark(
            ref, 
            predict_equivariant_nn,
            predict_kwargs=dict(model=model),
        ),
}

df = benchmarks['gaussian']
df['std / radius'] = df['std'] / df['radius']

plot_benchmark(benchmarks, extra_cols=['std / radius'], absolute_scale=True)
plt.savefig('run_benchmarks.svg')
plt.show()


