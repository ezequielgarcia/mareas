"""Newtonian N-body gravity with a velocity-Verlet (leapfrog) integrator.

Velocity Verlet is chosen over anything fancier because it is symplectic: the
energy error stays bounded and oscillatory instead of growing without limit, so
a year-long integration does not slowly spiral. It is only second order, but
with a 10-minute step that is far more accuracy than the tidal signal needs.
"""

import numpy as np


def accelerations(pos, gm):
    """Gravitational acceleration on each body.

    Parameters
    ----------
    pos : (N, 3) array, m
    gm  : (N,)   array, m^3/s^2

    Returns
    -------
    (N, 3) array, m/s^2
    """
    # sep[i, j] is the vector pointing from body i to body j.
    sep = pos[np.newaxis, :, :] - pos[:, np.newaxis, :]
    dist2 = np.sum(sep**2, axis=-1)
    np.fill_diagonal(dist2, np.inf)  # no body pulls on itself
    inv_dist3 = dist2**-1.5

    # a_i = sum_j GM_j * (r_j - r_i) / |r_j - r_i|^3
    return np.einsum("j,ij,ijk->ik", gm, inv_dist3, sep)


def total_energy(pos, vel, gm):
    """Total energy, in units where G = 1 and GM plays the role of mass.

    Only the *fractional drift* of this number is meaningful -- it is a check
    that the integrator is behaving, not a physical energy.
    """
    kinetic = 0.5 * np.sum(gm * np.sum(vel**2, axis=-1))

    sep = pos[np.newaxis, :, :] - pos[:, np.newaxis, :]
    dist = np.sqrt(np.sum(sep**2, axis=-1))
    i, j = np.triu_indices(len(gm), k=1)  # each pair once
    potential = -np.sum(gm[i] * gm[j] / dist[i, j])

    return kinetic + potential


def integrate(pos, vel, gm, dt, n_steps, sample_every=1):
    """Integrate the system and record the trajectory.

    Parameters
    ----------
    pos, vel : (N, 3) arrays -- initial state, modified only internally
    gm       : (N,) array
    dt       : timestep, s
    n_steps  : number of steps to take
    sample_every : store every k-th step

    Returns
    -------
    t         : (M,) array of times, s, starting at 0
    positions : (M, N, 3) array, m
    velocities: (M, N, 3) array, m/s -- synchronised with the positions, which
                is a convenience of velocity Verlet (unlike plain leapfrog,
                where velocities sit half a step out)
    """
    pos = np.array(pos, dtype=float)
    vel = np.array(vel, dtype=float)

    n_samples = 1 + n_steps // sample_every
    t = np.empty(n_samples)
    positions = np.empty((n_samples, *pos.shape))
    velocities = np.empty((n_samples, *pos.shape))
    t[0], positions[0], velocities[0] = 0.0, pos, vel

    accel = accelerations(pos, gm)
    stored = 1

    for step in range(1, n_steps + 1):
        # Kick-drift-kick. The acceleration from the end of one step is reused
        # as the start of the next, so this costs one force evaluation.
        vel += 0.5 * dt * accel
        pos += dt * vel
        accel = accelerations(pos, gm)
        vel += 0.5 * dt * accel

        if step % sample_every == 0 and stored < n_samples:
            t[stored], positions[stored], velocities[stored] = step * dt, pos, vel
            stored += 1

    return t[:stored], positions[:stored], velocities[:stored]
