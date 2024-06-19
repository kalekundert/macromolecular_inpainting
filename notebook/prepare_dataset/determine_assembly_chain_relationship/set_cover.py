import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint


lu = Bounds(lb=0, ub=1)

A = np.array([
    [1, 0, 1],
    [0, 1, 1],
    [1, 0, 1],
    [1, 0, 1],
    [0, 1, 1],
    [0, 1, 1],
    [1, 0, 1],
    [1, 0, 1],
])

Alu = LinearConstraint(A, lb=1)

res = milp(
        c=np.ones(3),
        integrality=np.ones(3),
        bounds=lu,
        constraints=Alu,
)
debug(res)

