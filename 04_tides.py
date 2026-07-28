"""Program 04 -- Spin the Earth: an actual tide record.

New idea: put the two previous programs together. Integrate the three bodies,
then rotate a station through the bulge pattern and record the water height as a
time series. This is the first program whose output looks like a tide gauge.

Three features to look for in the output:

  * High waters come every ~12h25m, not 12h00m. The Moon moves ~13 deg/day
    along its orbit, so Earth must turn a bit more than 360 deg to bring the
    Moon back overhead. A lunar day is 24h50m; half of that is 12h25m.

  * The amplitude swells and fades on a ~14.8-day cycle. That is the Sun-Moon
    beat: when they line up (new and full Moon) their bulges add -- spring
    tides; at quarter Moon they partly cancel -- neap tides. 14.8 days is half a
    synodic month, exactly as program 02 predicted.

  * Away from the equator, successive high waters differ in height (the
    "diurnal inequality"). This exists only because the Moon and Sun are not in
    Earth's equatorial plane, so one bulge passes closer to the station than the
    other.

Run:  python 04_tides.py
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tide.constants import DAY, GM_MOON, GM_SUN
from tide.initial_conditions import EARTH, MOON, SUN, three_body_state
from tide.nbody import integrate
from tide.potential import equilibrium_height, station_position

FIGURES = "figures"
DT = 600.0  # 10 min -- ~75 samples per tidal cycle
DURATION = 120.0 * DAY  # ~8 spring-neap cycles, enough to measure the period

STATION_LAT = 45.0
STATION_LON = 0.0

# A LUNAR day, not a solar one. Using a 24.00 h window to build the tidal
# envelope would beat against the true 24.84 h tidal day and manufacture a
# spurious ~29-day cycle in the envelope -- an easy and very misleading bug.
LUNAR_DAY = 24.8412 * 3600.0


def tide_series(lat, lon, t, moon_geo, sun_geo):
    """Equilibrium tide height at one station over a time series, m."""
    r_station = station_position(lat, lon, t)
    return equilibrium_height(r_station, [(moon_geo, GM_MOON), (sun_geo, GM_SUN)])


def high_water_interval(t, eta):
    """Mean time between successive high waters, hours."""
    is_max = (eta[1:-1] > eta[:-2]) & (eta[1:-1] > eta[2:])
    times = t[1:-1][is_max]
    return np.diff(times).mean() / 3600.0, times


def dominant_peaks(values, min_separation):
    """Local maxima, with any peak suppressed by a larger one within reach.

    Needed because the tidal envelope has small wiggles on top of the
    spring-neap swell; a naive local-maximum test counts those too.
    """
    candidates = [
        i for i in range(1, len(values) - 1)
        if values[i] > values[i - 1] and values[i] > values[i + 1]
    ]
    keep = [
        i for i in candidates
        if not any(values[j] > values[i] and abs(j - i) < min_separation
                   for j in candidates)
    ]
    return np.array(keep)


def main():
    pos0, vel0, gm = three_body_state()
    t, pos, vel = integrate(pos0, vel0, gm, DT, int(DURATION / DT))

    moon_geo = pos[:, MOON] - pos[:, EARTH]
    sun_geo = pos[:, SUN] - pos[:, EARTH]

    eta = tide_series(STATION_LAT, STATION_LON, t, moon_geo, sun_geo)
    eta_eq = tide_series(0.0, STATION_LON, t, moon_geo, sun_geo)

    print(f"Station at {STATION_LAT:.0f} N, {STATION_LON:.0f} E, "
          f"{DURATION / DAY:.0f} days at {DT:.0f} s")
    print(f"  range (max - min)  {(eta.max() - eta.min()) * 100:.1f} cm")
    print(f"  std dev            {eta.std() * 100:.1f} cm")

    interval, hw_times = high_water_interval(t, eta)
    interval_eq, _ = high_water_interval(t, eta_eq)
    print("\nSpacing of high waters")
    print(f"  at equator            {interval_eq:.4f} h"
          "   <- expected 12.4206 h, half a lunar day")
    print(f"  at {STATION_LAT:.0f} N               {interval:.4f} h")
    print("  The mid-latitude number is NOT a broken measurement. There the")
    print("  tide is 'mixed': the diurnal component is strong enough that some")
    print("  semidiurnal high waters are flattened out of existence, so peak")
    print("  counting no longer returns the semidiurnal period. Real gauges at")
    print("  such latitudes show exactly this. Program 05 separates the")
    print("  components properly instead of counting peaks.")

    # --- Spring/neap: track the envelope of the semidiurnal signal ---
    # Measured at the EQUATOR, where the diurnal components vanish (they go as
    # sin(2*lat)) and the tide is cleanly semidiurnal. At 45 N the envelope is
    # polluted by the diurnal signal and peak counting misfires.
    per_window = int(round(LUNAR_DAY / DT))  # see the LUNAR_DAY note above
    n_windows = len(t) // per_window
    windowed = eta_eq[: n_windows * per_window].reshape(n_windows, per_window)
    envelope = windowed.max(axis=1) - windowed.min(axis=1)
    envelope_t = (np.arange(n_windows) + 0.5) * LUNAR_DAY / DAY  # days

    # Springs are ~14.8 d apart; suppress any peak within 10 d of a bigger one.
    springs = dominant_peaks(envelope, min_separation=int(10.0 / (LUNAR_DAY / DAY)))
    print("\nSpring-neap cycle (equator, where the tide is purely semidiurnal)")
    print(f"  range over a lunar day varies {envelope.min() * 100:.1f} - "
          f"{envelope.max() * 100:.1f} cm  "
          f"(spring/neap ratio {envelope.max() / envelope.min():.2f})")
    if len(springs) > 1:
        spacing = np.diff(envelope_t[springs])
        print(f"  {len(springs)} spring maxima, spaced "
              f"{spacing.mean():.3f} +/- {spacing.std():.3f} d"
              "   (expected 14.765 = half a synodic month)")
    print("  Successive springs are unequal because the 27.55-day perigee cycle")
    print("  modulates them -- a spring tide at perigee is a 'perigean spring'.")

    # --- Diurnal inequality: are consecutive highs unequal? ---
    def inequality(series):
        is_max = (series[1:-1] > series[:-2]) & (series[1:-1] > series[2:])
        peaks = series[1:-1][is_max]
        return np.abs(np.diff(peaks)).mean() * 100 if len(peaks) > 2 else np.nan

    print("\nDiurnal inequality (mean height difference between "
          "successive high waters)")
    for lat in (0.0, 20.0, 45.0, 60.0):
        series = tide_series(lat, STATION_LON, t, moon_geo, sun_geo)
        print(f"  {lat:>4.0f} deg   {inequality(series):>6.2f} cm")

    # --- Figure ---
    fig, axes = plt.subplots(3, 1, figsize=(12, 9))
    days = t / DAY

    axes[0].plot(days, eta_eq * 100, lw=0.4)
    axes[0].plot(envelope_t, envelope * 50, color="tab:red", lw=1.4,
                 label="envelope (lunar-day range / 2)")
    axes[0].plot(envelope_t, -envelope * 50, color="tab:red", lw=1.4)
    axes[0].plot(envelope_t[springs], envelope[springs] * 50, "v",
                 color="k", ms=6, label="spring maxima")
    axes[0].set(xlabel="time (days)", ylabel="tide (cm)",
                title=f"{DURATION / DAY:.0f} days at the equator -- purely "
                      "semidiurnal, spring/neap beat every 14.8 d")
    axes[0].legend(loc="upper right", fontsize=8)

    zoom = (days >= 10) & (days <= 14)
    axes[1].plot(days[zoom], eta[zoom] * 100, lw=1.2, label=f"{STATION_LAT:.0f} N")
    axes[1].plot(days[zoom], eta_eq[zoom] * 100, lw=1.2, ls="--", label="equator")
    for hw in hw_times[(hw_times / DAY >= 10) & (hw_times / DAY <= 14)]:
        axes[1].axvline(hw / DAY, color="grey", lw=0.5)
    axes[1].set(xlabel="time (days)", ylabel="tide (cm)",
                title="4-day zoom -- high waters every 12h25m (grey lines), "
                      "unequal away from the equator")
    axes[1].legend(fontsize=8)

    axes[2].plot(days, np.linalg.norm(moon_geo, axis=-1) / 1e6, lw=1.0,
                 color="tab:purple")
    axes[2].set(xlabel="time (days)", ylabel="Earth-Moon distance (Mm)",
                title="For comparison: the monthly perigee cycle, which "
                      "modulates spring tide height")

    fig.tight_layout()
    fig.savefig(f"{FIGURES}/04_tides.png", dpi=130)
    print(f"\nWrote {FIGURES}/04_tides.png")


if __name__ == "__main__":
    import os

    os.makedirs(FIGURES, exist_ok=True)
    main()
