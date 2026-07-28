"""Ab initio tides from Newtonian gravity.

Shared physics for the numbered programs in the project root. Read them in
order -- each adds exactly one idea:

    01_two_body.py     gravity and the integrator, checked against Kepler
    02_three_body.py   add the Moon
    03_tidal_bulge.py  the differential force, and why there are two bulges
    04_tides.py        spin the Earth: a tide time series at a station
    05_constituents.py harmonic analysis: periods and amplitudes
"""

from . import constants, harmonics, initial_conditions, nbody, potential

__all__ = ["constants", "harmonics", "initial_conditions", "nbody", "potential"]
