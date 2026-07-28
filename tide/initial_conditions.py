"""Initial positions and velocities for the Sun-Earth-Moon system.

The frame is inertial with the ecliptic as the x-y plane. We do not use a real
ephemeris: instead we build a two-body Kepler state for the Earth-Moon
barycentre about the Sun, a second one for the Moon about the Earth, and
superpose them. That is enough to get every tidal *period* and *amplitude*
right, because those follow from the orbital elements. It does NOT correspond
to any real calendar date, so absolute tidal phases are meaningless here.
See README for the full list of what this approximation does and does not buy.
"""

import numpy as np

from .constants import (
    A_EMB,
    A_MOON_EPOCH,
    E_EMB,
    E_MOON_EPOCH,
    GM_EARTH,
    GM_MOON,
    GM_SUN,
    I_MOON,
)

# Row order used everywhere in this project.
BODY_NAMES = ("Sun", "Earth", "Moon")
SUN, EARTH, MOON = 0, 1, 2


def _kepler_perihelion(mu, a, e):
    """State of a two-body orbit at closest approach, in its own orbital plane.

    Returns (position, velocity) with the body on the +x axis moving toward +y.
    The speed follows from vis-viva at r = a(1 - e).
    """
    r = a * (1.0 - e)
    v = np.sqrt(mu * (1.0 + e) / (a * (1.0 - e)))
    return np.array([r, 0.0, 0.0]), np.array([0.0, v, 0.0])


def two_body_state():
    """Sun and Earth only -- the starting point for program 01.

    The Moon's mass is folded into the Earth so the orbit matches the
    three-body case as closely as a two-body model can.

    Returns (pos, vel, gm) with rows ordered (Sun, Earth).
    """
    gm = np.array([GM_SUN, GM_EARTH + GM_MOON])
    r, v = _kepler_perihelion(gm.sum(), A_EMB, E_EMB)

    pos = np.array([[0.0, 0.0, 0.0], r])
    vel = np.array([[0.0, 0.0, 0.0], v])

    total = gm.sum()
    pos -= (gm[:, None] * pos).sum(axis=0) / total
    vel -= (gm[:, None] * vel).sum(axis=0) / total

    return pos, vel, gm


def three_body_state(a_moon=A_MOON_EPOCH, e_moon=E_MOON_EPOCH):
    """Build the Sun-Earth-Moon initial condition.

    The lunar elements default to *osculating* values chosen so that the
    perturbed orbit has the right mean behaviour -- see tide/orbits.py for why
    that is not the same as the tabulated mean elements. Override them only if
    you are running the calibration itself.

    Returns
    -------
    pos : (3, 3) array, m -- one row per body, ordered (Sun, Earth, Moon)
    vel : (3, 3) array, m/s
    gm  : (3,)   array, m^3/s^2
    """
    gm = np.array([GM_SUN, GM_EARTH, GM_MOON])

    # 1. Earth-Moon barycentre about the Sun, starting at perihelion.
    #    The Sun feels all three bodies, so mu uses the total GM.
    r_emb, v_emb = _kepler_perihelion(GM_SUN + GM_EARTH + GM_MOON, A_EMB, E_EMB)

    # 2. Moon relative to Earth, starting at perigee. Tilting the orbit by the
    #    lunar inclination about the x axis leaves perigee in the ecliptic
    #    plane, i.e. we happen to start at the ascending node. The tilt shows
    #    up in the velocity as a z component, which is what drives the Moon's
    #    declination cycle -- and hence the diurnal tides.
    r_rel, v_rel = _kepler_perihelion(GM_EARTH + GM_MOON, a_moon, e_moon)
    ci, si = np.cos(I_MOON), np.sin(I_MOON)
    rot_x = np.array([[1.0, 0.0, 0.0], [0.0, ci, -si], [0.0, si, ci]])
    r_rel, v_rel = rot_x @ r_rel, rot_x @ v_rel

    # 3. Split the Earth-Moon pair about their common barycentre.
    f_moon = GM_MOON / (GM_EARTH + GM_MOON)
    f_earth = GM_EARTH / (GM_EARTH + GM_MOON)

    pos = np.array([
        [0.0, 0.0, 0.0],          # Sun
        r_emb - f_moon * r_rel,   # Earth
        r_emb + f_earth * r_rel,  # Moon
    ])
    vel = np.array([
        [0.0, 0.0, 0.0],
        v_emb - f_moon * v_rel,
        v_emb + f_earth * v_rel,
    ])

    # 4. Drop into the frame where the system barycentre is at rest at the
    #    origin. Without this the whole system drifts, which is harmless for
    #    tides but makes plots and energy checks confusing.
    total = gm.sum()
    pos -= (gm[:, None] * pos).sum(axis=0) / total
    vel -= (gm[:, None] * vel).sum(axis=0) / total

    return pos, vel, gm
