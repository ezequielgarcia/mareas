"""The tide-generating potential, and the equilibrium tide it implies.

The key idea, and the one that trips everyone up: tides are NOT caused by the
Moon's gravity. They are caused by the *difference* between the Moon's pull on
a patch of ocean and its pull on the Earth as a whole. The Earth is in free
fall toward the Moon; only the residual matters.

Write the Moon's potential at a station r (measured from Earth's centre) with
the Moon at d (also from Earth's centre):

    Phi(r) = -GM / |d - r|

Subtract the two pieces that produce no tide:

  * -GM/|d| is uniform across the Earth -- a constant, so no force at all.
  * the term linear in r is the uniform acceleration of the whole Earth toward
    the Moon. We sit in the geocentric free-falling frame, so it cancels.

What is left is the tide-generating potential:

    V(r) = GM * ( 1/|d - r|  -  1/|d|  -  (r . d)/|d|^3 )

which is exact -- no series truncation. Expanding it for r << d gives the
familiar quadrupole form

    V ~= (GM r^2 / 2 d^3) * (3 cos^2(psi) - 1)

with psi the angle between station and Moon. That (3cos^2 - 1) is why there are
*two* bulges: it is positive both under the Moon (psi = 0) and on the far side
(psi = 180 deg). Two bulges per rotation is why the dominant tide is
semidiurnal.

Note the d^-3: the tide-raising strength falls off as the *cube* of distance,
not the square. That is why the Sun -- 27 million times more massive than the
Moon but 390 times further away -- raises a tide only about half as large.
"""

import numpy as np

from .constants import G_SURFACE, LOVE_FACTOR, OBLIQUITY, OMEGA_EARTH, R_EARTH


def station_position(lat_deg, lon_deg, t):
    """Geocentric position of a point on Earth's surface, in the ecliptic frame.

    Two rotations are involved:

      1. spin the Earth-fixed vector by the rotation angle omega*t, taking it
         into an inertial frame whose z axis is Earth's spin axis;
      2. tilt by the obliquity, taking that into the ecliptic frame the orbits
         live in.

    Parameters
    ----------
    lat_deg, lon_deg : scalars or arrays -- geographic latitude and longitude
    t : scalar or (M,) array -- time, s

    Returns
    -------
    (..., 3) array of positions, m. Shapes broadcast: a scalar station with a
    time series gives (M, 3); a lat/lon grid at one instant gives that grid's
    shape plus a trailing 3.
    """
    phi = np.radians(lat_deg)
    lam = np.radians(lon_deg)

    # Earth-fixed frame: z along the spin axis, x through the prime meridian.
    x0 = R_EARTH * np.cos(phi) * np.cos(lam)
    y0 = R_EARTH * np.cos(phi) * np.sin(lam)
    z0 = R_EARTH * np.sin(phi) * np.ones_like(x0)

    # 1. Earth's rotation, about z.
    theta = OMEGA_EARTH * np.asarray(t, dtype=float)
    x1 = x0 * np.cos(theta) - y0 * np.sin(theta)
    y1 = x0 * np.sin(theta) + y0 * np.cos(theta)
    z1 = z0 + np.zeros_like(theta)

    # 2. Obliquity, about x: equatorial frame -> ecliptic frame.
    ce, se = np.cos(OBLIQUITY), np.sin(OBLIQUITY)
    return np.stack([x1, y1 * ce + z1 * se, -y1 * se + z1 * ce], axis=-1)


def tide_generating_potential(r_station, r_body, gm):
    """Exact tide-generating potential, J/kg (= m^2/s^2).

    Parameters
    ----------
    r_station : (..., 3) geocentric station position, m
    r_body    : (..., 3) geocentric position of the tide-raising body, m
    gm        : that body's GM, m^3/s^2
    """
    d = np.linalg.norm(r_body, axis=-1)
    sep = np.linalg.norm(r_body - r_station, axis=-1)
    r_dot_d = np.sum(r_station * r_body, axis=-1)
    return gm * (1.0 / sep - 1.0 / d - r_dot_d / d**3)


def quadrupole_potential(r_station, r_body, gm):
    """The (3 cos^2 psi - 1) approximation, for comparison with the exact form."""
    r = np.linalg.norm(r_station, axis=-1)
    d = np.linalg.norm(r_body, axis=-1)
    cos_psi = np.sum(r_station * r_body, axis=-1) / (r * d)
    return gm * r**2 / (2.0 * d**3) * (3.0 * cos_psi**2 - 1.0)


def equilibrium_height(r_station, bodies, love_factor=LOVE_FACTOR):
    """Equilibrium tide height, m.

    The equilibrium (or "static") tide is the water surface you get by assuming
    the ocean has time to settle into an equipotential surface:

        eta = gamma_2 * V / g

    This is the honest limit of an ab initio calculation. It gets every period
    right and gives amplitudes of order 0.2-0.5 m. It cannot give you real
    coastal tides -- those are a resonant, friction-damped response of ocean
    basins to this forcing, which needs the Laplace tidal equations and real
    bathymetry.

    Parameters
    ----------
    r_station : (..., 3) geocentric station position, m
    bodies : iterable of (r_body, gm) pairs, r_body geocentric and broadcastable
             against r_station
    love_factor : set to 1.0 for the rigid-Earth tide
    """
    v_total = sum(
        tide_generating_potential(r_station, r_body, gm) for r_body, gm in bodies
    )
    return love_factor * v_total / G_SURFACE
