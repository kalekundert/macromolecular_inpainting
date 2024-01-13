import pytest
import parametrize_from_file as pff

from pytest import approx
from intersect_utils import *
from itertools import product
from io import StringIO

with_math = pff.Namespace('from math import *')

def grid(g):
    cell_size = float(g)
    return Grid(cell_size)

def sphere(d):
    center = coord(d['center'])
    radius = with_math.eval(d['radius'])
    return Sphere(center, radius)

def coord(s):
    return coords(s)

def coords(s):
    io = StringIO(s)
    return np.loadtxt(io)

def index(s):
    return indices(s)

def indices(s):
    io = StringIO(s)
    return np.loadtxt(io, dtype=int)

def prob_matrix(d):
    index_value_pairs = [
            (index(k), with_math.eval(v))
            for k, v in d.items()
    ]
    indices = np.vstack([ijk for ijk, _ in index_value_pairs])
    min_index = np.min(indices, axis=0)
    max_index = np.max(indices, axis=0)
    shape = max_index - min_index + 1

    prob_matrix = np.zeros(shape)

    for ijk, p in index_value_pairs:
        prob_matrix[tuple(ijk)] = p

    return prob_matrix

def known_probs(d, cells):
    probs = pd_series_from_cells(cells)

    for k_str, v_str in d.items():
        k = tuple(index(k_str))
        v = with_math.eval(v_str)
        probs[k] = v

    return probs


def test_find_cells_containing_points():
    grid = Grid(1)
    points = np.array([
        [0.00, 0, 0],
        [0.49, 0, 0],
        [0.51, 0, 0],
        [1.00, 0, 0],

        [0, 0.00, 0],
        [0, 0.49, 0],
        [0, 0.51, 0],
        [0, 1.00, 0],

        [0, 0, 0.00],
        [0, 0, 0.49],
        [0, 0, 0.51],
        [0, 0, 1.00],
    ])
    expected = np.array([
        [0, 0, 0],
        [0, 0, 0],
        [1, 0, 0],
        [1, 0, 0],

        [0, 0, 0],
        [0, 0, 0],
        [0, 1, 0],
        [0, 1, 0],

        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 1],
        [0, 0, 1],
    ])

    assert (find_cells_containing_points(grid, points) == expected).all()

@pff.parametrize(
        schema=[
            pff.cast(
                grid=grid,
                sphere=sphere,
                margin=float,
                expected=pff.cast(
                    min_index=index,
                    max_index=index,
                ),
            ),
            pff.defaults(
                margin=0,
            ),
        ],
)
def test_find_possibly_overlapping_cells(grid, sphere, margin, expected):
    cells = find_possibly_overlapping_cells(grid, sphere, margin)
    indices = {
            tuple(x)
            for x in cells.indices
    }
    axes = [
            range(expected['min_index'][i], expected['max_index'][i] + 1)
            for i in range(3)
    ]
    expected = {
            (i, j, k)
            for i, j, k in product(*axes)
    }
    assert indices >= expected

def test_sample_within_unit_sphere():
    rng = np.random.default_rng(0)
    samples = sample_within_unit_sphere(rng, 1000)
    norm = np.linalg.norm(samples, axis=1)
    assert (norm <= 1.0).all()
    assert (norm >= 0.9).any()

@pff.parametrize(
        schema=[
            pff.cast(
                grid=grid,
                sphere=sphere,
            ),
        ],
)
def test_estimate_true_intersection(grid, sphere, expected):
    rng = np.random.default_rng(0)
    cells = find_possibly_overlapping_cells(grid, sphere)
    result = estimate_true_intersection(rng, cells, sphere)
    expected = known_probs(expected, cells)

    # Mahalanobis distance is the multivariate equivalent of standard 
    # deviation, so I assume that the threshold of 2 should include the true 
    # mean 95% of the time.  I'm not actually sure that this interpretation of 
    # standard deviations holds for Mahalanobis distances, but empirically, it 
    # seems to work.
    #
    # Note that each test still has a 5% chance of failure.  With the random 
    # seed I've chosen, the tests I've written so far all pass.  But if I were 
    # to add new tests, they might not pass, and I'd have to investigate the 
    # failures to make sure they're just due to random chance.

    assert result.mahalanobis(expected) < 2

def test_dirichlet_covariance():
    # https://github.com/scipy/scipy/pull/18664
    alpha = np.array([1., 0.8, 0.2])
    expected_cov = pytest.approx(np.array([
            [ 1. / 12, -1. / 15, -1. / 60],
            [-1. / 15,  2. / 25, -1. / 75],
            [-1. / 60, -1. / 75,  3. / 100],
    ]))
    assert dirichlet_covariance(alpha) == expected_cov
