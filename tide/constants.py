"""Physical constants and orbital elements. Everything is SI.

Gravitational parameters are quoted as GM rather than as masses, because GM is
measured far more precisely than G and M separately -- and GM is all the
dynamics ever needs.
"""

import math

# --- Gravitational parameters, m^3 s^-2 (IAU 2015 / JPL DE440) ---
GM_SUN = 1.32712440018e20
GM_EARTH = 3.986004418e14
GM_MOON = 4.9048695e12

# --- Earth figure and rotation ---
R_EARTH = 6.371008e6  # volumetric mean radius, m
G_SURFACE = 9.80665  # standard gravity, m s^-2
OBLIQUITY = math.radians(23.4392911)  # tilt of the spin axis from the ecliptic normal
SIDEREAL_DAY = 86164.0905  # s -- one rotation with respect to the stars
OMEGA_EARTH = 2.0 * math.pi / SIDEREAL_DAY  # rad s^-1

# Elastic response of the solid Earth.
#
# A tide gauge measures the sea surface relative to the crust -- but the crust
# is deforming too, and Earth's own tidal bulge adds to the potential. Both
# effects are folded into the "diminishing factor"
#
#     gamma_2 = 1 + k_2 - h_2
#
# with Love numbers k_2 = 0.302 (extra potential from Earth's bulge) and
# h_2 = 0.609 (radial displacement of the crust).
#
# Set this to 1.0 to recover the textbook rigid-Earth equilibrium tide.
LOVE_FACTOR = 1.0 + 0.302 - 0.609  # ~= 0.693

# --- Orbital elements, used only to build the initial conditions ---
# Earth-Moon barycentre about the Sun:
A_EMB = 1.495978707e11  # semi-major axis, m (= 1 au)
E_EMB = 0.0167086  # eccentricity

# Moon about the Earth:
A_MOON = 3.84399e8  # semi-major axis, m -- tabulated MEAN element
E_MOON = 0.0549  # eccentricity -- tabulated MEAN element
I_MOON = math.radians(5.145)  # inclination to the ecliptic

# Osculating lunar elements at our epoch.
#
# Feeding the mean elements above straight into a two-body initial condition
# gives an orbit whose mean semi-major axis ends up ~0.8% too small, because the
# Sun's perturbation (~1.1%) makes the osculating elements oscillate about a
# different centre. That yields a lunar month ~0.8% fast, which shifts M2 by
# 0.24 deg/hour -- fatal, since M2 and S2 are only 1.016 deg/hour apart.
#
# These values come from `python calibrate.py`, which iterates until the
# simulated sidereal month is 27.321661 d and the mean osculating eccentricity
# is 0.0549. See tide/orbits.py for the full explanation.
# The epoch eccentricity is well above the mean because we start at perigee AND
# at syzygy, where the Sun stretches the orbit hardest. The real Moon's
# osculating eccentricity ranges over roughly 0.026-0.077, so this sits at the
# top of the physical range rather than outside it.
A_MOON_EPOCH = 3.863029e8  # m
E_MOON_EPOCH = 0.076224

# --- Convenience ---
DAY = 86400.0
YEAR = 365.25 * DAY
