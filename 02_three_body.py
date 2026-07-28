"""Program 02 -- Three bodies: add the Moon.

New idea: nothing about the code changes. `accelerations` already sums over all
pairs, so going from two bodies to three is a one-line change to the initial
condition. What changes is the *behaviour*, and three effects are worth seeing
before we get anywhere near water:

  * The Earth no longer moves smoothly. It orbits the Earth-Moon barycentre,
    which sits ~4700 km from Earth's centre -- inside the Earth, but well off
    centre. Earth's monthly wobble is real and it matters for tides.

  * The sidereal month (Moon's period against the stars, 27.32 d) differs from
    the synodic month (Moon's period against the Sun, 29.53 d). The Sun-Moon
    *beat* is what produces spring and neap tides, so this ~2-day gap is the
    origin of the fortnightly cycle we will see in program 04.

  * The Earth-Moon distance is not constant: the ~5.5% eccentricity swings it
    between about 356,000 and 406,000 km. Since tide-raising force goes as
    1/d^3, that is a large modulation in lunar tidal strength. That is where the
    N2 constituent comes from.

And two slow cycles emerge that we never put in, both caused by the Sun tugging
on the lunar orbit. They matter enormously for program 05:

  * the line of nodes regresses with an 18.61-year period, which swings the
    Moon's maximum declination between 18.3 and 28.6 degrees;
  * the line of apsides advances with an 8.85-year period.

Run:  python 02_three_body.py   (~15 s -- it integrates 20 years)
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tide.constants import DAY, GM_EARTH, GM_MOON, OBLIQUITY, R_EARTH, YEAR
from tide.initial_conditions import EARTH, MOON, SUN, three_body_state
from tide.nbody import integrate, total_energy
from tide.orbits import (
    APSIDAL_PERIOD,
    NODAL_PERIOD,
    mean_motion_period,
    node_longitude,
    osculating_elements,
    perigee_longitude,
    precession_period,
)

FIGURES = "figures"
DT = 600.0  # 10 minutes -- the Moon's orbit needs finer steps than the Earth's
SAMPLE_EVERY = 6  # store hourly; the 10-minute steps are only for accuracy
DURATION = 20.0 * YEAR  # long enough to see the 18.6-year nodal cycle


def mean_period(t, signal):
    """Mean interval between successive local minima of a signal."""
    is_min = (signal[1:-1] < signal[:-2]) & (signal[1:-1] < signal[2:])
    times = t[1:-1][is_min]
    return np.diff(times).mean() if len(times) > 1 else np.nan


def main():
    pos0, vel0, gm = three_body_state()

    print("Three-body: Sun + Earth + Moon")
    print(f"  timestep {DT:.0f} s, duration {DURATION / YEAR:.1f} yr")

    e0 = total_energy(pos0, vel0, gm)
    t, pos, vel = integrate(
        pos0, vel0, gm, DT, int(DURATION / DT), sample_every=SAMPLE_EVERY
    )

    moon_geo = pos[:, MOON] - pos[:, EARTH]  # Moon, seen from Earth's centre
    sun_geo = pos[:, SUN] - pos[:, EARTH]  # Sun, seen from Earth's centre
    d_moon = np.linalg.norm(moon_geo, axis=-1)

    # --- Earth's wobble about the Earth-Moon barycentre ---
    f_moon = GM_MOON / (GM_EARTH + GM_MOON)
    print("\nEarth's monthly wobble")
    print(f"  barycentre offset from Earth's centre  {f_moon * d_moon.mean() / 1e3:.0f} km")
    print(f"  ... as a fraction of Earth's radius    {f_moon * d_moon.mean() / R_EARTH:.3f}")

    # --- Sidereal month: Moon's period in the inertial frame ---
    # Measured by counting complete revolutions of the geocentric longitude.
    sidereal = mean_motion_period(t, moon_geo)

    # --- Synodic month: period of the Moon's phase, i.e. Moon relative to Sun ---
    # The Moon's longitude relative to the Sun's, which is what "phase" means.
    sun_lon = np.arctan2(sun_geo[:, 1], sun_geo[:, 0])
    phase = np.stack([np.cos(-sun_lon), np.sin(-sun_lon), np.zeros_like(sun_lon)], -1)
    moon_rel_sun = np.stack([
        moon_geo[:, 0] * phase[:, 0] - moon_geo[:, 1] * phase[:, 1],
        moon_geo[:, 0] * phase[:, 1] + moon_geo[:, 1] * phase[:, 0],
        moon_geo[:, 2],
    ], axis=-1)
    synodic = mean_motion_period(t, moon_rel_sun)

    print("\nTwo different months")
    print(f"  sidereal (vs stars)  {sidereal / DAY:.4f} d   (accepted 27.3217)")
    print(f"  synodic  (vs Sun)    {synodic / DAY:.4f} d   (accepted 29.5306)")
    print(f"  spring-neap = half a synodic month  {synodic / DAY / 2:.3f} d")
    print("  1/synodic = 1/sidereal - 1/year, because Earth's own orbital")
    print("  motion means the Moon must catch up to the Sun each month")

    # --- Anomalistic month, and what the 1/d^3 law does with it ---
    anomalistic = mean_period(t, d_moon)
    strength = 1.0 / d_moon**3
    print("\nEarth-Moon distance")
    print(f"  perigee {d_moon.min() / 1e3:,.0f} km   apogee {d_moon.max() / 1e3:,.0f} km")
    print(f"  anomalistic month (perigee to perigee)  {anomalistic / DAY:.3f} d"
          "   (accepted 27.5545)")
    print(f"  tidal strength (1/d^3) varies by  "
          f"{(strength.max() - strength.min()) / strength.mean() * 100:.0f}%")

    # --- Slow cycles the Sun drives, which nobody told the simulation about ---
    moon_vel = vel[:, MOON] - vel[:, EARTH]
    nodal = precession_period(t, node_longitude(moon_geo, moon_vel))
    apsidal = precession_period(
        t, perigee_longitude(moon_geo, moon_vel, GM_EARTH + GM_MOON)
    )
    print("\nSlow cycles of the lunar orbit -- emergent, not prescribed")
    print(f"  nodal period    {abs(nodal) / YEAR:>6.2f} yr "
          f"({'retrograde' if nodal < 0 else 'prograde'})"
          f"   accepted {NODAL_PERIOD / YEAR:.2f} yr, retrograde")
    print(f"  apsidal period  {abs(apsidal) / YEAR:>6.2f} yr "
          f"({'retrograde' if apsidal < 0 else 'prograde'})"
          f"   accepted {APSIDAL_PERIOD / YEAR:.2f} yr, prograde")
    print("  The nodal cycle swings the Moon's maximum declination between")
    print("  18.3 and 28.6 deg, which modulates the diurnal tides by ~10-20%.")
    print("  Program 05 has to average over a full 18.6 years because of it.")

    # --- The Sun deforms the lunar orbit: osculating vs mean elements ---
    a_osc, e_osc = osculating_elements(moon_geo, moon_vel, GM_EARTH + GM_MOON)
    print("\nSolar perturbation of the lunar orbit")
    print(f"  osculating a  {a_osc.min() / 1e3:,.0f} - {a_osc.max() / 1e3:,.0f} km"
          f"   (mean {a_osc.mean() / 1e3:,.0f})")
    print(f"  osculating e  {e_osc.min():.4f} - {e_osc.max():.4f}"
          f"   (mean {e_osc.mean():.4f}, tabulated mean 0.0549)")
    print("  This ~1% wobble is why the initial condition needed calibrating;")
    print("  see tide/orbits.py.")

    print("\nIntegrator")
    e1 = total_energy(pos[-1], vel[-1], gm)
    print(f"  fractional energy drift  {abs(e1 - e0) / abs(e0):.2e}")

    # --- Figure ---
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5))
    axes = axes.ravel()

    days = t / DAY
    sel = days <= 60

    axes[0].plot(moon_geo[sel, 0] / 1e6, moon_geo[sel, 1] / 1e6, lw=0.9)
    axes[0].plot(0, 0, "o", color="tab:blue", ms=9, label="Earth")
    axes[0].set(xlabel="x (Mm)", ylabel="y (Mm)",
                title="Moon's geocentric orbit, 60 d")
    axes[0].set_aspect("equal")
    axes[0].legend()

    # Earth's wobble: subtract the smooth Earth-Moon-barycentre motion.
    emb = (GM_EARTH * pos[:, EARTH] + GM_MOON * pos[:, MOON]) / (GM_EARTH + GM_MOON)
    wobble = pos[:, EARTH] - emb
    axes[1].plot(wobble[sel, 0] / 1e3, wobble[sel, 1] / 1e3, lw=0.9)
    circle = plt.Circle((0, 0), R_EARTH / 1e3, fc="tab:blue", alpha=0.25,
                        label="Earth's surface")
    axes[1].add_patch(circle)
    axes[1].set(xlabel="x (km)", ylabel="y (km)",
                title="Earth's wobble about the barycentre")
    axes[1].set_aspect("equal")
    axes[1].legend(loc="upper right", fontsize=8)

    axes[2].plot(days[days <= 200], d_moon[days <= 200] / 1e6, lw=0.9)
    axes[2].set(xlabel="time (days)", ylabel="Earth-Moon distance (Mm)",
                title="Perigee/apogee: the source of N2")

    # The Moon's declination -- its angle above Earth's equator, which is what
    # the diurnal tides respond to. Convert ecliptic -> equatorial by undoing
    # the obliquity rotation that station_position applies.
    ce, se = np.cos(OBLIQUITY), np.sin(OBLIQUITY)
    z_equatorial = moon_geo[:, 1] * se + moon_geo[:, 2] * ce
    declination = np.degrees(np.arcsin(z_equatorial / d_moon))
    axes[3].plot(days / 365.25, declination, lw=0.3)
    axes[3].set(xlabel="time (years)", ylabel="Moon's declination (deg)",
                title="The 18.6-year nodal cycle: peak declination\n"
                      "breathes between 18.3 and 28.6 deg")
    for level in (18.3, 28.6, -18.3, -28.6):
        axes[3].axhline(level, color="tab:red", lw=0.7, ls="--")

    fig.tight_layout()
    fig.savefig(f"{FIGURES}/02_three_body.png", dpi=130)
    print(f"\nWrote {FIGURES}/02_three_body.png")


if __name__ == "__main__":
    import os

    os.makedirs(FIGURES, exist_ok=True)
    main()
