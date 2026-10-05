"""Find the osculating lunar elements that reproduce the observed mean orbit.

Run this once; paste the result into tide/constants.py as A_MOON_EPOCH and
E_MOON_EPOCH. It is separated out from the numbered programs because it is a
setup step, not part of the physics story -- but it is worth reading, because
the reason it is necessary is an instructive gotcha. See the module
docstring in tide/orbits.py.

Run:  python calibrate.py
"""

from tide.constants import DAY
from tide.orbits import MEAN_ECCENTRICITY, SIDEREAL_MONTH, calibrate_lunar_orbit

if __name__ == "__main__":
    print("Targets:")
    print(f"  sidereal month            {SIDEREAL_MONTH / DAY:.6f} d")
    print(f"  mean osculating eccentricity  {MEAN_ECCENTRICITY:.5f}")
    print()

    a, e = calibrate_lunar_orbit()

    print()
    print("Paste into tide/constants.py:")
    print(f"  A_MOON_EPOCH = {a:.6e}  # m")
    print(f"  E_MOON_EPOCH = {e:.6f}")
