"""Program 05 -- Periods and amplitudes: harmonic analysis.

New idea: decompose the time series from program 04 into the standard tidal
constituents. This is the payoff -- the answer to "what are the periods and
amplitudes of the tides?", derived from nothing but Newtonian gravity and the
orbital elements.

The frequencies are not fitted. They are known in advance from astronomy, so the
fit is linear: one least-squares solve recovers all amplitudes and phases.

The strongest evidence that this is really working is the *ratio* check. Within a
species (semidiurnal, diurnal), the amplitude ratios between constituents are
fixed by the expansion of the tidal potential and are independent of latitude, of
the Love number, and of anything else we chose. If S2/M2 comes out at 0.465 and
N2/M2 at 0.19, the physics is right.

RECORD LENGTH IS NOT A FREE CHOICE. The Moon's line of nodes regresses over
18.61 years (program 02 measures this), swinging the Moon's peak declination
between 18.3 and 28.6 degrees. The tabulated constituent amplitudes are
mean-node values, so a short record catches the node at whatever phase it
happens to be in and gets the amplitudes wrong -- K2 by 30% or more. This
program fits both a 2-year and a full-nodal-cycle record so you can watch that
happen. This is the same reason the official standard for tidal datums is a
19-year "National Tidal Datum Epoch".

Run:  python 05_constituents.py   (~20 s -- it integrates 18.6 years)
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tide.constants import DAY, GM_MOON, GM_SUN, LOVE_FACTOR, YEAR
from tide.harmonics import (
    DEFAULT_CONSTITUENTS,
    SPEEDS,
    THEORETICAL_RATIOS,
    fit,
    format_table,
    unresolved_pairs,
)
from tide.initial_conditions import EARTH, MOON, SUN, three_body_state
from tide.nbody import integrate
from tide.orbits import NODAL_PERIOD
from tide.potential import equilibrium_height, station_position

FIGURES = "figures"
DT = 600.0  # 10-minute integration steps, for accuracy
SAMPLE_EVERY = 6  # ...but store hourly, which is the tidal-analysis standard
DURATION = NODAL_PERIOD  # exactly one nodal cycle -- see the module docstring
SHORT = 2.0 * YEAR  # for contrast

STATION_LAT = 45.0
STATION_LON = 0.0


def ratio_report(result, label):
    """Print the species-internal amplitude ratios against classical theory."""
    print(f"\n  {label}")
    print(f"  {'ratio':<8} {'simulated':>10} {'theory':>10} {'error':>9}")
    print("  " + "-" * 39)
    worst = 0.0
    for key, expected in THEORETICAL_RATIOS.items():
        a, b = key.split("/")
        got = result[a]["amplitude"] / result[b]["amplitude"]
        err = (got - expected) / expected * 100.0
        worst = max(worst, abs(err))
        print(f"  {key:<8} {got:>10.4f} {expected:>10.4f} {err:>8.1f}%")
    print(f"  worst error: {worst:.1f}%")
    return worst


def main():
    # --- Resolvability check, before we do any work ---
    print(f"Record length {DURATION / DAY:.1f} d ({DURATION / YEAR:.2f} yr), "
          f"stored every {DT * SAMPLE_EVERY / 3600:.0f} h")
    bad = unresolved_pairs(DEFAULT_CONSTITUENTS, DURATION)
    if bad:
        print("  WARNING -- record too short to separate:")
        for a, b, need in bad:
            print(f"    {a}/{b} needs {need:.0f} d")
    else:
        tightest = min(
            ((a, b) for i, a in enumerate(DEFAULT_CONSTITUENTS)
             for b in DEFAULT_CONSTITUENTS[i + 1:]),
            key=lambda p: abs(SPEEDS[p[0]] - SPEEDS[p[1]]),
        )
        print("  all requested constituents pass the Rayleigh criterion; "
              f"tightest pair {tightest[0]}/{tightest[1]}")

    # --- Simulate ---
    pos0, vel0, gm = three_body_state()
    t, pos, vel = integrate(
        pos0, vel0, gm, DT, int(DURATION / DT), sample_every=SAMPLE_EVERY
    )
    moon_geo = pos[:, MOON] - pos[:, EARTH]
    sun_geo = pos[:, SUN] - pos[:, EARTH]
    bodies = [(moon_geo, GM_MOON), (sun_geo, GM_SUN)]

    eta = equilibrium_height(station_position(STATION_LAT, STATION_LON, t), bodies)
    result = fit(t, eta)

    print(f"\nStation {STATION_LAT:.0f} N, {STATION_LON:.0f} E "
          f"(Love factor gamma_2 = {LOVE_FACTOR:.3f})")
    print(format_table(result))

    explained = 1.0 - np.var(eta - reconstruct(t, result)) / np.var(eta)
    print(f"\n  these {len(DEFAULT_CONSTITUENTS)} constituents explain "
          f"{explained * 100:.2f}% of the variance")

    # --- The ratio test: the real ab initio validation ---
    print("\nAmplitude ratios within a species")
    print("  (fixed by the potential expansion -- independent of latitude and")
    print("   Love number, so these are a clean check on the dynamics)")

    short = t <= SHORT
    ratio_report(fit(t[short], eta[short]),
                 f"fitted to the first {SHORT / YEAR:.0f} years only:")
    ratio_report(result,
                 f"fitted to the full {DURATION / YEAR:.2f}-year nodal cycle:")
    print("\n  K2 and K1 are the constituents that move most, because they are")
    print("  the ones whose amplitude depends on the lunar node. Averaging over")
    print("  the whole 18.6-year cycle is what recovers the tabulated values.")

    # --- An absolute check, not just a ratio ---
    # The classical rigid-Earth equilibrium M2 amplitude at the equator is
    # ~0.242 m. Ours carries the Love factor, so divide it back out.
    eta_eq = equilibrium_height(station_position(0.0, STATION_LON, t), bodies)
    m2_equator = fit(t, eta_eq)["M2"]["amplitude"]
    print("\nAbsolute M2 amplitude at the equator")
    print(f"  simulated                    {m2_equator * 100:.3f} cm")
    print(f"  with the Love factor removed {m2_equator / LOVE_FACTOR * 100:.3f} cm")
    print("  classical rigid-Earth value   ~24.2 cm")

    # --- Latitude dependence: another shape the theory predicts exactly ---
    # Semidiurnal amplitude goes as cos^2(lat); diurnal as sin(2*lat).
    print("\nLatitude dependence of the two dominant constituents")
    print(f"  {'lat':>5} {'M2 (cm)':>9} {'cos^2 fit':>10} "
          f"{'K1 (cm)':>9} {'sin2 fit':>10}")
    print("  " + "-" * 46)
    lats = np.array([0.0, 15.0, 30.0, 45.0, 60.0, 75.0, 89.0])
    m2, k1 = [], []
    for lat in lats:
        r = fit(t, equilibrium_height(station_position(lat, STATION_LON, t), bodies))
        m2.append(r["M2"]["amplitude"])
        k1.append(r["K1"]["amplitude"])
    m2, k1 = np.array(m2), np.array(k1)

    m2_pred = m2[0] * np.cos(np.radians(lats)) ** 2
    k1_scale = k1[3] / np.abs(np.sin(np.radians(2 * 45.0)))
    k1_pred = k1_scale * np.abs(np.sin(np.radians(2 * lats)))
    for i, lat in enumerate(lats):
        print(f"  {lat:>5.0f} {m2[i] * 100:>9.3f} {m2_pred[i] * 100:>10.3f} "
              f"{k1[i] * 100:>9.3f} {k1_pred[i] * 100:>10.3f}")

    # --- Figure ---
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    names = sorted(DEFAULT_CONSTITUENTS, key=lambda n: SPEEDS[n])
    amps = [result[n]["amplitude"] * 100 for n in names]
    colors = ["tab:green" if SPEEDS[n] < 2 else
              "tab:orange" if SPEEDS[n] < 20 else "tab:blue" for n in names]
    axes[0].bar(names, amps, color=colors)
    axes[0].set(ylabel="amplitude (cm)",
                title="Constituent amplitudes\n(green: long period, "
                      "orange: diurnal, blue: semidiurnal)")
    axes[0].tick_params(axis="x", rotation=60)

    axes[1].plot(lats, m2 * 100, "o-", label="M2 (simulated)")
    axes[1].plot(lats, m2_pred * 100, "--", label=r"$\cos^2(\phi)$")
    axes[1].plot(lats, k1 * 100, "s-", label="K1 (simulated)")
    axes[1].plot(lats, k1_pred * 100, "--", label=r"$|\sin(2\phi)|$")
    axes[1].set(xlabel="latitude (deg)", ylabel="amplitude (cm)",
                title="Latitude dependence follows the\nspherical harmonics exactly")
    axes[1].legend(fontsize=8)

    # A periodogram makes the line spectrum visible without any fitting, and
    # shows the constituents clustering into species by how many times per day
    # they cycle.
    window = np.hanning(len(t))
    spectrum = np.abs(np.fft.rfft((eta - eta.mean()) * window))
    speed = np.fft.rfftfreq(len(t), d=DT * SAMPLE_EVERY / 3600.0) * 360.0
    axes[2].semilogy(speed, spectrum / spectrum.max(), lw=0.6)

    bands = [
        (0.0, 2.0, "long\nperiod", "tab:green"),
        (13.0, 16.0, "diurnal", "tab:orange"),
        (27.5, 31.0, "semidiurnal", "tab:blue"),
    ]
    for lo, hi, label, color in bands:
        axes[2].axvspan(lo, hi, color=color, alpha=0.13)
        axes[2].text((lo + hi) / 2, 1.6, label, fontsize=8, ha="center",
                     va="bottom", color=color)
    axes[2].set(xlim=(0, 33), ylim=(1e-6, 12),
                xlabel="speed (deg/hour)", ylabel="relative power",
                title="Spectrum: discrete lines, clustered\ninto species")

    fig.tight_layout()
    fig.savefig(f"{FIGURES}/05_constituents.png", dpi=130)
    print(f"\nWrote {FIGURES}/05_constituents.png")


def reconstruct(t, result, names=DEFAULT_CONSTITUENTS):
    """Rebuild the tide from fitted constituents, m."""
    out = np.full_like(t, result["Z0"])
    for name in names:
        w = np.radians(SPEEDS[name]) / 3600.0
        r = result[name]
        out += r["amplitude"] * np.cos(w * t - np.radians(r["phase_deg"]))
    return out


if __name__ == "__main__":
    import os

    os.makedirs(FIGURES, exist_ok=True)
    main()
