"""Osculating orbital elements, and why the initial conditions need calibrating.

This module exists because of a subtlety that bites every from-scratch
Solar System simulation, and it is worth understanding before trusting any
tidal period that comes out of one.

The numbers you look up -- "the Moon's semi-major axis is 384,399 km,
eccentricity 0.0549" -- are MEAN elements. They describe the average of an orbit
that is constantly being deformed by the Sun. At any single instant the
*osculating* elements (the ellipse the Moon would follow if every other body
vanished right now) differ from the mean ones by of order the perturbation
strength, which for the Sun acting on the Earth-Moon pair is

    2 * (GM_sun / d_sun^3) * r_moon^3 / GM_earth  ~=  1.1 %

So if you set the osculating semi-major axis to 384,399 km at some arbitrary
epoch, the orbit oscillates *around a different mean*, and the resulting lunar
month can easily be ~1% wrong. A 1% error in the lunar mean motion moves M2 by
0.24 deg/hour -- catastrophic, given that M2 and S2 are only 1.016 deg/hour
apart. Harmonic analysis would be meaningless.

The fix is to do what ephemeris fitting does: choose the osculating elements at
our epoch so that the *mean* behaviour matches the tabulated mean elements.
`calibrate_lunar_orbit` below does that with a few iterations.
"""

import numpy as np

from .constants import DAY, GM_EARTH, GM_MOON, GM_SUN, YEAR

# Observed values we are trying to reproduce.
SIDEREAL_MONTH = 27.321661 * DAY  # s, Moon's orbital period against the stars
MEAN_ECCENTRICITY = 0.0549

# Two slow cycles of the lunar orbit, both driven purely by the Sun's
# perturbation -- so a three-body simulation reproduces them without being told.
# They set the record length needed for honest harmonic analysis.
NODAL_PERIOD = 18.6129 * YEAR  # regression of the line of nodes (retrograde)
APSIDAL_PERIOD = 8.8504 * YEAR  # advance of the line of apsides


def osculating_elements(r, v, mu):
    """Osculating semi-major axis and eccentricity of a relative orbit.

    Parameters
    ----------
    r, v : (..., 3) relative position (m) and velocity (m/s)
    mu   : GM of the two-body system, m^3/s^2

    Returns
    -------
    (a, e) arrays -- semi-major axis in m, eccentricity dimensionless
    """
    r_mag = np.linalg.norm(r, axis=-1)
    v2 = np.sum(v * v, axis=-1)

    # Vis-viva: the specific orbital energy fixes a.
    a = 1.0 / (2.0 / r_mag - v2 / mu)

    # e from the eccentricity vector, e_vec = (v x h)/mu - r_hat.
    h = np.cross(r, v)
    e_vec = np.cross(v, h) / mu - r / r_mag[..., None]
    return a, np.linalg.norm(e_vec, axis=-1)


def orbit_normal(r, v):
    """Unit vector along the orbital angular momentum, i.e. the orbit's pole."""
    h = np.cross(r, v)
    return h / np.linalg.norm(h, axis=-1)[..., None]


def node_longitude(r, v):
    """Unwrapped ecliptic longitude of the ascending node, rad.

    The node line points along z_hat x h_hat = (-h_y, h_x, 0).
    """
    h = orbit_normal(r, v)
    return np.unwrap(np.arctan2(h[..., 0], -h[..., 1]))


def perigee_longitude(r, v, mu):
    """Unwrapped ecliptic longitude of perigee, rad."""
    h = np.cross(r, v)
    e_vec = np.cross(v, h) / mu - r / np.linalg.norm(r, axis=-1)[..., None]
    return np.unwrap(np.arctan2(e_vec[..., 1], e_vec[..., 0]))


def precession_period(t, angle):
    """Period of a slowly precessing angle, s. Negative means retrograde."""
    return 2.0 * np.pi / np.polyfit(t, angle, 1)[0]


def mean_motion_period(t, r):
    """Orbital period from a whole number of revolutions, s.

    Averaging over complete cycles is what makes this robust: a least-squares
    line through the longitude would be biased by wherever the periodic
    perturbations happen to sit at the two ends of the record.
    """
    lon = np.unwrap(np.arctan2(r[:, 1], r[:, 0]))
    # Times at which the longitude passes each multiple of 2*pi.
    turns = np.arange(np.ceil(lon.min() / (2 * np.pi)),
                      np.floor(lon.max() / (2 * np.pi)) + 1) * 2 * np.pi
    if len(turns) < 2:
        return np.nan
    crossings = np.interp(turns, lon, t)
    return (crossings[-1] - crossings[0]) / (len(crossings) - 1)


def measure_lunar_orbit(a_epoch, e_epoch, dt=900.0, duration=4.0 * YEAR):
    """Simulate the three bodies and report the Moon's mean behaviour.

    Returns (sidereal_period_seconds, mean_osculating_eccentricity).
    """
    from .initial_conditions import EARTH, MOON, three_body_state
    from .nbody import integrate

    pos0, vel0, gm = three_body_state(a_moon=a_epoch, e_moon=e_epoch)
    t, pos, vel = integrate(pos0, vel0, gm, dt, int(duration / dt))

    r = pos[:, MOON] - pos[:, EARTH]
    v = vel[:, MOON] - vel[:, EARTH]
    _, e = osculating_elements(r, v, GM_EARTH + GM_MOON)

    return mean_motion_period(t, r), e.mean()


def calibrate_lunar_orbit(iterations=6, verbose=True):
    """Solve for the osculating (a, e) at epoch that reproduce the mean orbit.

    Two targets, two unknowns. The updates use the Keplerian scalings as
    approximate derivatives -- P ~ a^(3/2), and eccentricity roughly
    proportional to itself -- which converges in a handful of steps because the
    corrections are only of order a percent.
    """
    from .constants import A_MOON, E_MOON

    a, e = A_MOON, E_MOON
    if verbose:
        print(f"{'iter':>4} {'a_epoch (km)':>14} {'e_epoch':>9} "
              f"{'sidereal (d)':>13} {'mean e':>9}")

    for i in range(iterations):
        period, e_mean = measure_lunar_orbit(a, e)
        if verbose:
            print(f"{i:>4} {a / 1e3:>14,.1f} {e:>9.5f} "
                  f"{period / DAY:>13.6f} {e_mean:>9.5f}")
        if (abs(period - SIDEREAL_MONTH) < 1e-4 * DAY
                and abs(e_mean - MEAN_ECCENTRICITY) < 1e-5):
            break
        a *= (SIDEREAL_MONTH / period) ** (2.0 / 3.0)
        e *= MEAN_ECCENTRICITY / e_mean

    return a, e
