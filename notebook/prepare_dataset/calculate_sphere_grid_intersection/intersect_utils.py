#!/usr/bin/env python3

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import overlap

from math import ceil, sqrt, pi
from numpy.typing import NDArray, ArrayLike
from scipy.stats import norm as gaussian, dirichlet
from scipy.optimize import minimize_scalar
from scipy.spatial.distance import mahalanobis
from matplotlib.colors import Normalize
from dataclasses import dataclass
from more_itertools import one, zip_broadcast
from natsort import natsort_key
from functools import partial
from tqdm import tqdm
from typing import TypeAlias
from joblib import Memory
from pathlib import Path

memo = Memory('cache', verbose=False)

Coords: TypeAlias = NDArray[float]
Indices: TypeAlias = NDArray[int]

@dataclass
class Grid:
    # The origin is always a grid point.
    cell_size: float

@dataclass
class Cells:
    grid: Grid
    indices: Indices

    def __len__(self):
        return self.indices.shape[0]

    @property
    def size(self) -> float:
        return self.grid.cell_size

    @property
    def coords(self) -> Coords:
        return self.indices * self.grid.cell_size

@dataclass
class Sphere:
    center: ArrayLike
    radius: float

class MonteCarloResult:

    def __init__(self, cells, sphere, counts):
        self.cells = cells
        self.sphere = sphere
        self.counts = counts

        # Uniform prior: α=1
        #
        # I wanted to use a Jeffreys prior (α=0.5), but this requires that at 
        # least one count is observed for every bin, which isn't the case here.
        prior_pseudocounts = 1

        self.dirichlet = dirichlet(counts + prior_pseudocounts)

    @property
    def normalized_counts(self):
        return self.counts / np.sum(self.counts)

    def pdf(self, p):
        assert p.shape == self.counts.shape
        return self.dirichlet.pdf(p)

    def logpdf(self, p):
        assert p.shape == self.counts.shape
        return self.dirichlet.logpdf(p)

    def mahalanobis(self, p):
        """
        Calculate how many "standard deviations" away from the mean the given 
        hit probabilities are.
        """
        assert p.shape == self.counts.shape

        # Use the Moore-Penrose pseudo-inverse of the covariance matrix, rather 
        # than the true inverse, for the Mahalanobis distance calculation.  The 
        # reason is that the covariance matrix is singular, because the last 
        # Bernoulli parameter is completely determined by its peers, so it 
        # doesn't have an inverse.  However, using the pseudo-inverse is 
        # equivalent to transforming the data into a non-singular subspace.
        # 
        # More info:
        # https://stats.stackexchange.com/questions/37743/singular-covariance-matrix-in-mahalanobis-distance-in-matlab

        mu = self.dirichlet.mean()
        cov = dirichlet_covariance(self.dirichlet.alpha)
        return mahalanobis(p, mu, np.linalg.pinv(cov))

def run_benchmark(known_results, predict_func, *, predict_kwargs={}):
    rows = []

    for result in known_results:
        cells = result.cells
        sphere = result.sphere

        # If `predict_kwargs` is a function, call it with the known results.  
        # This allows "cheating", since we can tune the parameters to the known 
        # right answers.  The purpose of this is to evaluate the best-case 
        # scenario for an algorithm (specifically the Gaussian algorithm).
        if callable(predict_kwargs):
            kwargs = predict_kwargs(result)
        else:
            kwargs = predict_kwargs

        prediction = predict_func(cells, sphere, **kwargs)
        overlap = -sum_min_loss(result, prediction)

        rows.append({
            'x': sphere.center[0],
            'y': sphere.center[1],
            'z': sphere.center[2],
            'radius': sphere.radius,
            'overlap': overlap,
            **kwargs,
        })

    return pd.DataFrame(rows)

def fit_gaussian_std(expected, loss):

    def objective(std):
        pred = predict_gaussian_std(expected.cells, expected.sphere, std)
        return loss(expected, pred)

    r = expected.sphere.radius
    fit = minimize_scalar(objective, bounds=(r/10, 2*r), method='bounded')

    return {'std': fit.x}

def predict_gaussian_std(cells, sphere, std):
    dist = np.linalg.norm(cells.coords - sphere.center, axis=1)
    x = gaussian.pdf(dist, loc=0, scale=std)
    return clip_nonintersecting_cells(x, cells, sphere, dist=dist)

def predict_analytical_strobl(cells, sphere):
    # Coordinates based on CGNS conventions, but really just copied from the 
    # examples provided by the `overlap` library:
    # https://github.com/severinstrobl/overlap
    # https://cgns.github.io/CGNS_docs_current/sids/conv.html#unst_hexa
    x = cells.size / 2
    origin_cube = np.array([
        [-x, -x, -x],
        [ x, -x, -x],
        [ x,  x, -x],
        [-x,  x, -x],
        [-x, -x,  x],
        [ x, -x,  x],
        [ x,  x,  x],
        [-x,  x,  x],
    ])

    volumes = np.zeros(len(cells))
    volume_sphere = 4 / 3 * pi * sphere.radius**3

    for i in range(len(cells)):
        cube = overlap.Hexahedron(origin_cube + cells.coords[i])
        sphere_ = overlap.Sphere(sphere.center, sphere.radius)
        volumes[i] = overlap.overlap(sphere_, cube)

    # The `voxelize` package makes this check, so it's probably prudent to do 
    # the same.
    if (volumes > volume_sphere).any():
        raise RuntimeError("numerical instability in overlap")

    return volumes / volume_sphere

def predict_equivariant_nn(cells, sphere, model):
    import equivariant_nn as enn
    x = enn.make_equivariant_nn_inputs(cells, sphere)
    y = model(x).detach().numpy().reshape(-1)
    return clip_nonintersecting_cells(y, cells, sphere)

def train_equivariant_nn(model, dataset, trainer):
    import equivariant_nn as enn
    task = enn.SphereCubeTask(model)
    trainer.fit(model=task, train_dataloaders=dataset)
    return model.eval()

def load_equivariant_nn(path=None):
    import equivariant_nn as enn

    if path is None:
        logs = Path(__file__).parent / 'lightning_logs'
        version = max(
                logs.glob('version_*'),
                key=lambda x: natsort_key(x.name),
        )
        path = one(version.glob('checkpoints/*.ckpt'))

    task = enn.SphereCubeTask.load_from_checkpoint(
            path,
            model=enn.SphereCubeModel(),
    )
    task.eval()

    return task.model

    # checkpoint = torch.load(path)
    # debug(path, checkpoint)
    # model = enn.SphereCubeModel()
    # model.load_state_dict(checkpoint['model'])
    # model.eval()

    # return model

def dirichlet_log_p_loss(expected, predicted):
    return -expected.logpdf(predicted)

def dot_product_loss(expected, predicted):
    # This doesn't work quite like I was thinking.  The components of each 
    # vector sum to one, but neither vector is normalized.  So the magnitude of 
    # the dot product isn't really meaningful.  I could normalize both vectors 
    # before doing the dot product, but that doesn't feel right.

    # See `sum_min_loss()` for what I think is a better alternative.
    return -np.inner(expected.dirichlet.mean(), predicted)

def sum_min_loss(expected, predicted):
    # Note that this loss function only works if both inputs are constrained to 
    # sum to one; otherwise you could minimizing it by just predicting a large 
    # value everywhere.
    cmp = np.vstack((expected.normalized_counts, predicted))
    return -np.sum(np.min(cmp, axis=0))

@memo.cache
def estimate_true_intersections(rng, grid, n_estimates=1000, n_samples=10000, center_bounds=None, radius_bounds=None, cell_margin=1):
    results = []

    for i in tqdm(range(n_estimates)):
        sphere = sample_sphere(rng, grid, center_bounds, radius_bounds)
        cells = find_possibly_overlapping_cells(grid, sphere, margin=cell_margin)
        result = estimate_true_intersection(rng, cells, sphere)
        results.append(result)

    return results

def estimate_true_intersection(rng, cells, sphere, n_samples=10000):
    """
    Estimate what fraction of the sphere lies in each of the given grid cells.

    We make these estimates using a Monte Carlo simulation.  Specifically, we 
    draw uniform samples from within the sphere and observe which grid cell  
    they fall in.  From these samples, we can't exactly calculate how much of 
    the sphere overlaps with each grid cell, but we can find the probability 
    distribution for these values.

    We can calculate this distribution using Bayesian inference.  Our 
    likelihood is multinomial, because each sample must land in exactly one 
    cell.  The conjugate prior for the multinomial distribution is the 
    Dirichlet distribution.  We will specifically use the uniform prior, 
    which is $\alpha_i = 1$ for the Dirichlet distribution.

    Note that the given cells must include every cell that intersects with the 
    sphere, otherwise a `KeyError` will be raised.
    """

    # It turns out to be much faster to accumulate all the results in an array 
    # and to copy them into a series afterwards.  Presumably this is because 
    # `pd.MultiIndex` does a lot behind the scenes.

    samples = sample_within_sphere(rng, sphere, n_samples)
    hit_indices = find_cells_containing_points(cells.grid, samples)
    hit_array, dijk = np_array_from_cells(cells)

    # Feels like there should be a vectorized way to do this, but I can't 
    # figure it out.
    for ijk in hit_indices:
        hit_array[tuple(ijk - dijk)] += 1

    hit_series = pd_series_from_cells(cells)
    
    for ijk in hit_series.index:
        hit_series[ijk] = hit_array[tuple(ijk - dijk)]

    return MonteCarloResult(cells, sphere, hit_series)

def sample_sphere(rng, grid=None, center_bounds=None, radius_bounds=None):
    if not center_bounds:
        center_bounds = -0.5 * grid.cell_size, 0.5 * grid.cell_size
    if not radius_bounds:
        radius_bounds = 0.5 * grid.cell_size, 1.5 * grid.cell_size

    center = rng.uniform(*center_bounds, 3)
    radius = rng.uniform(*radius_bounds)
    return Sphere(center, radius)

def sample_within_sphere(rng, sphere, n_samples) -> Coords:
    u = sample_within_unit_sphere(rng, n_samples)
    return sphere.center + u * sphere.radius

def sample_within_unit_sphere(rng, n_samples) -> Coords:
    # The easiest way to uniformly sample points within a sphere is to 
    # uniformly sample points within a cube, then to discard any points that 
    # fall outside of the sphere.  Note that only about 
    # 
    # https://stats.stackexchange.com/questions/8021/how-to-generate-uniformly-distributed-points-in-the-3-d-unit-ball

    samples = np.zeros((0, 3))

    while len(samples) < n_samples:
        # Make double the number of samples that we need, because only about 
        # $\frac{4}{3} \pi \frac{1}{2}^3 = 52.3%$ of the samples will be within 
        # the sphere.
        n = 2 * (n_samples - len(samples))
        candidates = rng.uniform(-1, 1, size=(n, 3))
        dist2 = np.sum(candidates**2, axis=1)
        samples = np.vstack([samples, candidates[dist2 <= 1]])

    return samples[:n_samples]

def find_possibly_overlapping_cells(grid, sphere, margin=0) -> Cells:
    # Note that this function returns a cubical region of the grid, so not all 
    # of the returned cells (i.e. those in the corners) are necessarily 
    # intersecting the sphere.

    probes = np.array([
        [ 1,  0,  0],
        [-1,  0,  0],
        [ 0,  1,  0],
        [ 0, -1,  0],
        [ 0,  0,  1],
        [ 0,  0, -1],
    ])
    probes = sphere.center + probes * sphere.radius
    probe_hits = find_cells_containing_points(grid, probes)

    min_index = np.min(probe_hits, axis=0) - margin
    max_index = np.max(probe_hits, axis=0) + margin

    axes = [
            np.arange(min_index[i], max_index[i] + 1)
            for i in range(3)
    ]
    mesh = np.meshgrid(*axes)
    indices = np.vstack([x.flat for x in mesh]).T
    return Cells(grid, indices)

def find_cells_containing_points(grid, points) -> Indices:
    # Consider each grid coordinate to be the center of the cell.
    return np.rint(points / grid.cell_size).astype(int)

def clip_nonintersecting_cells(x, cells, sphere, dist=None):
    if dist is None:
        dist = np.linalg.norm(cells.coords - sphere.center, axis=1)

    cell_radius = sqrt(3) * cells.size / 2
    x[dist > sphere.radius + cell_radius] = 0
    sum = np.sum(x)

    return x / np.sum(x) if sum else x

def pd_series_from_cells(cells, fill_value=0):
    # It's important to establish a single, canonical, 1D ordering of the cells 
    # being considered in all these calculations.  `pd.Series` make this easier 
    # to do, because they can be treated more like dictionaries.
    return pd.Series(
            fill_value,
            index=pd.MultiIndex.from_arrays(cells.indices.T),
    )

def np_array_from_cells(cells, fill_values=0):
    min_index = np.min(cells.indices, axis=0)
    max_index = np.max(cells.indices, axis=0)
    array = np.empty(max_index - min_index + 1)

    for k, v in zip_broadcast(cells.indices, fill_values, strict=True):
        array[tuple(k - min_index)] = v

    return array, min_index

def dirichlet_covariance(alpha):
    # The scipy implementation of the Dirichlet distribution doesn't provide a 
    # covariance matrix.  However, I need this information in order to 
    # calculate Mahalanobis distances (for my unit tests).
    alpha0 = np.sum(alpha)
    a = alpha / alpha0
    return (np.diag(a) - np.outer(a, a)) / (alpha0 + 1)


def plot_benchmark(dfs, extra_cols=[], absolute_scale=False):
    n_rows, n_cols = 1 + len(extra_cols), len(dfs)
    plt.figure(figsize=(3 * n_cols + 1, 3 * n_rows))

    if absolute_scale:
        z_min = min(
                df['overlap'].min()
                for df in dfs.values()
        )
        norm = Normalize(z_min, 1)
    else:
        norm = None

    for i, (title, df) in enumerate(dfs.items()):
        dist = np.sqrt(df['x']**2 + df['y']**2 + df['z']**2)

        plt.subplot(n_rows, n_cols, i + 1)
        plt.title(title)
        plt.scatter(dist, df['radius'], c=df['overlap'], norm=norm)
        plt.xlabel('distance')
        plt.ylabel('radius')
        plt.colorbar(label='overlap')

        for j, col in enumerate(extra_cols, 1):
            if col not in df.columns:
                continue

            plt.subplot(n_rows, n_cols, i + 1 + j * n_cols)
            plt.scatter(dist, df['radius'], c=df[col])
            plt.xlabel('distance')
            plt.ylabel('radius')
            plt.colorbar(label=col)

    plt.tight_layout()

def plot_prediction(expected, predicted):
    cells = expected.cells
    expected_img, _ = np_array_from_cells(cells, expected.normalized_counts)
    predicted_img, _ = np_array_from_cells(cells, predicted)

    n = len(expected_img)
    norm = Normalize(0, max(expected_img.max(), predicted_img.max()))

    plt.figure(figsize=(8, 5))

    for i in range(n):
        plt.subplot(2, n, i+1)
        plt.imshow(expected_img[i], norm=norm)

        plt.subplot(2, n, n+i+1)
        plt.imshow(predicted_img[i], norm=norm)

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    rng = np.random.default_rng(0)
    grid = Grid(1)

    #model = load_equivariant_nn()

    sphere = Sphere([0, 0, 0], 1)
    cells = find_possibly_overlapping_cells(grid, sphere)
    x = enn.make_equivariant_nn_inputs(cells, sphere)

    model = enn.SphereCubeModel()
    # debug(
    #         model.linear_1.weights,
    #         model.linear_1.bias,
    #         model.linear_2.weights,
    #         model.linear_2.bias,
    #         x,
    #         model(x),
    # )

    dataset = enn.SphereCubeDataset(rng, grid, epoch_size=10)
    trainer = pl.Trainer(max_epochs=100)

    model = train_equivariant_nn(model, dataset, trainer)
    # debug(
    #         model.linear_1.weights,
    #         model.linear_1.bias,
    #         model.linear_2.weights,
    #         model.linear_2.bias,
    #         model(x),
    # )

    # df = run_benchmark(
    #         rng,
    #         grid,
    #         predict_equivariant_nn,
    #         predict_kwargs=dict(model=model),
    # )

    # plot_benchmark({'equivariant nn': df})
    # plt.show()


    # fits = fit_gaussian_std_for_random_spheres(rng, grid, dirichlet_log_p_loss)
    # fits = fit_gaussian_std_for_random_spheres(rng, grid, sum_min_loss)

    # plot_optimal_gaussian_stds(fits)
    # plt.savefig('optimize_intersection.svg')
    # plt.show()
