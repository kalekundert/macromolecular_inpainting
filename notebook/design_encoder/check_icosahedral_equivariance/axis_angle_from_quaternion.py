#!/usr/bin/env python3

import numpy as np
import math

# https://en.wikipedia.org/wiki/Quaternions_and_spatial_rotation#Recovering_the_axis-angle_representation

q_exact = np.array([-0.5, -0.5, -0.5,  0.5])
q_interp = np.array([-0.5, -0.30901699, -0.80901699, -0.0])

def axis_angle(q):
    m = np.sqrt(np.sum(q[1:]**2))
    v = q[1:] / m
    th = 2 * math.atan2(m, q[0])
    return v, math.degrees(th)

debug(
        axis_angle(q_exact),
        axis_angle(q_interp),
)
