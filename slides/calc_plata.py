"""Numbers behind the Rio de la Plata slides in charla.md.

Run from the repository root (~20 s, it integrates one nodal cycle):

    uv run python slides/calc_plata.py

Prints the equilibrium-tide amplitudes of the eight main constituents at
Buenos Aires (34.6 S), the form factor F = (K1+O1)/(M2+S2), and L/lambda for
the estuary at a few depths. The observed values used on the slide (M2 0.27 m,
O1 0.15 m at Buenos Aires; estuary length ~320 km) are from Moreira & Simionato
(2019), not computed here. The mean depth is NOT measured: the slide uses a
5-15 m range, so L/lambda is an estimate and says so.

Code, identifiers and comments are English, like the rest of the software.
"""

import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tide.constants import G_SURFACE, GM_MOON, GM_SUN  # noqa: E402
from tide.harmonics import fit, period_hours  # noqa: E402
from tide.initial_conditions import EARTH, MOON, SUN, three_body_state  # noqa: E402
from tide.nbody import integrate  # noqa: E402
from tide.orbits import NODAL_PERIOD  # noqa: E402
from tide.potential import equilibrium_height, station_position  # noqa: E402

LAT, LON = -34.6, -58.4  # Buenos Aires; longitude only changes phases
CONSTITUENTS = ("M2", "S2", "N2", "K2", "K1", "O1", "P1", "Q1")
OBSERVED = {"M2": 0.27, "O1": 0.15}  # m, Buenos Aires
ESTUARY_LENGTH = 320e3  # m
DEPTHS = (5, 10, 15)  # m, assumed


def main():
    pos0, vel0, gm = three_body_state()
    t, pos, _ = integrate(pos0, vel0, gm, 600.0, int(NODAL_PERIOD / 600.0), sample_every=6)
    bodies = [(pos[:, MOON] - pos[:, EARTH], GM_MOON), (pos[:, SUN] - pos[:, EARTH], GM_SUN)]
    result = fit(t, equilibrium_height(station_position(LAT, LON, t), bodies))

    amp = {n: result[n]["amplitude"] for n in CONSTITUENTS}
    print(f"Equilibrium tide at {abs(LAT)} {'S' if LAT < 0 else 'N'}")
    for n in CONSTITUENTS:
        print(f"  {n}  {period_hours(n):7.3f} h  {amp[n] * 100:5.2f} cm  /M2 {amp[n] / amp['M2']:.3f}")
    print(f"  form factor F = {(amp['K1'] + amp['O1']) / (amp['M2'] + amp['S2']):.2f}")

    print("\nObserved / equilibrium (Buenos Aires)")
    for n, obs in OBSERVED.items():
        print(f"  {n}  {obs:.2f} m  gain x{obs / amp[n]:.1f}")
    print(f"  O1/M2  observed {OBSERVED['O1'] / OBSERVED['M2']:.2f}  equilibrium {amp['O1'] / amp['M2']:.2f}")

    print(f"\nEstuary L = {ESTUARY_LENGTH / 1e3:.0f} km; resonances at L/lambda = 1/4, 3/4, ...")
    for h in DEPTHS:
        c = math.sqrt(G_SURFACE * h)
        cells = "  ".join(
            f"{n} {ESTUARY_LENGTH / (c * period_hours(n) * 3600):.2f}" for n in ("M2", "O1", "K1")
        )
        print(f"  h = {h:2d} m  c = {c:4.1f} m/s  L/lambda: {cells}")


if __name__ == "__main__":
    main()
