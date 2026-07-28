"""Program 03 -- Water: why there are two bulges, not one.

New idea: the tide-generating potential. No time evolution here at all -- we
freeze the system at one instant and map the potential over the whole globe, so
the geometry is the only thing on screen.

The thing to internalise: if tides were caused by the Moon simply pulling water
toward itself, there would be ONE high tide a day. There are two. The reason is
that the Earth is in free fall toward the Moon, so what matters is the
*difference* between the local pull and the pull on Earth's centre:

  * on the near side, the Moon pulls harder than average -> residual toward Moon
  * on the far side, the Moon pulls weaker than average -> residual away from Moon
  * on the flanks, the pull is angled inward -> residual squeezes downward

Two bulges, one under the Moon and one opposite. Earth rotates through both in a
day, which is why the dominant tide is semidiurnal.

This program also checks two quantitative claims:

  * the exact potential and the (3cos^2 psi - 1) quadrupole approximation agree
    to a fraction of a percent, because Earth's radius is only 1/60 of the
    Earth-Moon distance;
  * the Moon out-tides the Sun by about 2.2x, despite being vastly less massive,
    because tidal forcing falls off as 1/d^3 rather than 1/d^2.

Run:  python 03_tidal_bulge.py
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tide.constants import (
    A_EMB,
    A_MOON,
    GM_MOON,
    GM_SUN,
    G_SURFACE,
    LOVE_FACTOR,
    R_EARTH,
)
from tide.initial_conditions import EARTH, MOON, SUN, three_body_state
from tide.potential import (
    equilibrium_height,
    quadrupole_potential,
    station_position,
    tide_generating_potential,
)

FIGURES = "figures"


def main():
    # A single snapshot -- no integration needed. Positions seen from Earth.
    pos, _, _ = three_body_state()
    moon_geo = pos[MOON] - pos[EARTH]
    sun_geo = pos[SUN] - pos[EARTH]

    d_moon = np.linalg.norm(moon_geo)
    d_sun = np.linalg.norm(sun_geo)
    print("Snapshot geometry")
    print(f"  Earth-Moon  {d_moon / 1e3:>12,.0f} km  = {d_moon / R_EARTH:.1f} Earth radii")
    print(f"  Earth-Sun   {d_sun / 1e3:>12,.0f} km  = {d_sun / R_EARTH:.1f} Earth radii")

    # --- Why the Moon wins: tidal forcing goes as GM/d^3 ---
    print("\nTide-raising strength, GM/d^3")
    print(f"  Moon / Sun mass ratio      {GM_MOON / GM_SUN:.3e}  (Sun is far heavier)")
    print(f"  Moon / Sun distance ratio  {d_moon / d_sun:.3e}")
    print(f"  Moon / Sun TIDE ratio, at MEAN distances  "
          f"{(GM_MOON / A_MOON**3) / (GM_SUN / A_EMB**3):.3f}   (accepted 2.18)")
    print(f"  ... at this snapshot                      "
          f"{(GM_MOON / d_moon**3) / (GM_SUN / d_sun**3):.3f}")
    print("  The snapshot ratio is higher because we start with the Moon at")
    print("  perigee and the Earth at perihelion -- both at closest approach,")
    print("  but the Moon gains more since it is the nearer body.")

    # --- Map the equilibrium tide over the globe ---
    lat = np.linspace(-90.0, 90.0, 181)
    lon = np.linspace(0.0, 360.0, 361)
    lon_grid, lat_grid = np.meshgrid(lon, lat)

    r_station = station_position(lat_grid, lon_grid, 0.0)
    eta = equilibrium_height(
        r_station, [(moon_geo, GM_MOON), (sun_geo, GM_SUN)]
    )
    eta_moon = equilibrium_height(r_station, [(moon_geo, GM_MOON)])
    eta_sun = equilibrium_height(r_station, [(sun_geo, GM_SUN)])

    print("\nEquilibrium tide height (Love factor "
          f"gamma_2 = {LOVE_FACTOR:.3f})")
    for label, field in (("Moon", eta_moon), ("Sun", eta_sun), ("both", eta)):
        print(f"  {label:<5} min {field.min() * 100:>7.1f} cm   "
              f"max {field.max() * 100:>7.1f} cm   "
              f"range {(field.max() - field.min()) * 100:>7.1f} cm")

    # --- Exact potential vs the quadrupole approximation ---
    v_exact = tide_generating_potential(r_station, moon_geo, GM_MOON)
    v_quad = quadrupole_potential(r_station, moon_geo, GM_MOON)
    rel_err = np.abs(v_exact - v_quad).max() / np.abs(v_exact).max()
    print("\nExact potential vs (3cos^2 psi - 1) approximation")
    print(f"  r/d = {R_EARTH / d_moon:.4f}")
    print(f"  max relative difference  {rel_err:.2e}")

    # --- Two bulges, as a function of angle from the sublunar point ---
    psi = np.linspace(0.0, 360.0, 721)
    # A great circle through the sublunar point.
    moon_hat = moon_geo / d_moon
    # Any vector perpendicular to moon_hat spans the circle with it.
    perp = np.cross(moon_hat, [0.0, 0.0, 1.0])
    perp /= np.linalg.norm(perp)
    ring = R_EARTH * (
        np.cos(np.radians(psi))[:, None] * moon_hat
        + np.sin(np.radians(psi))[:, None] * perp
    )
    eta_ring = equilibrium_height(ring, [(moon_geo, GM_MOON)])

    # --- Figure ---
    fig = plt.figure(figsize=(13, 8))

    ax1 = fig.add_subplot(2, 2, (1, 2))
    levels = np.linspace(eta.min() * 100, eta.max() * 100, 25)
    cf = ax1.contourf(lon, lat, eta * 100, levels=levels, cmap="RdBu_r")
    ax1.contour(lon, lat, eta * 100, levels=levels, colors="k", linewidths=0.2)
    fig.colorbar(cf, ax=ax1, label="equilibrium tide (cm)")
    ax1.set(xlabel="longitude (deg)", ylabel="latitude (deg)",
            title="Equilibrium tide, Moon + Sun, one instant "
                  "(two highs, two lows)")

    ax2 = fig.add_subplot(2, 2, 3)
    ax2.plot(psi, eta_ring * 100, lw=1.6)
    ax2.axhline(0, color="k", lw=0.5)
    for x in (0, 180, 360):
        ax2.axvline(x, color="tab:red", lw=0.8, ls="--")
    ax2.set(xlabel="angle from sublunar point (deg)",
            ylabel="lunar equilibrium tide (cm)",
            title=r"Two bulges: the $3\cos^2\psi - 1$ shape",
            xticks=[0, 90, 180, 270, 360])

    ax3 = fig.add_subplot(2, 2, 4)
    ax3.plot(psi, eta_ring * 100, lw=1.4, label="Moon")
    eta_ring_sun = equilibrium_height(ring, [(sun_geo, GM_SUN)])
    ax3.plot(psi, eta_ring_sun * 100, lw=1.4, label="Sun")
    ax3.axhline(0, color="k", lw=0.5)
    ax3.set(xlabel="angle from sublunar point (deg)", ylabel="tide (cm)",
            title="Moon vs Sun, same great circle",
            xticks=[0, 90, 180, 270, 360])
    ax3.legend()

    fig.tight_layout()
    fig.savefig(f"{FIGURES}/03_tidal_bulge.png", dpi=130)
    print(f"\nWrote {FIGURES}/03_tidal_bulge.png")


if __name__ == "__main__":
    import os

    os.makedirs(FIGURES, exist_ok=True)
    main()
