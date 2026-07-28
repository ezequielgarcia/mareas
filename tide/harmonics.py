"""Harmonic analysis: turning a tide time series into periods and amplitudes.

Classical tidal analysis assumes the tide is a sum of sinusoids at frequencies
fixed by astronomy:

    eta(t) = Z0 + sum_i  A_i * cos(w_i * t - g_i)

The frequencies w_i are *known in advance* -- they are integer combinations of
six astronomical rates (Earth's rotation, the Moon's orbit, the Sun's orbit,
lunar perigee, the lunar node, and perihelion), which is Doodson's scheme. So
we never have to search for them. Rewriting each term as

    A_i cos(g_i) cos(w_i t) + A_i sin(g_i) sin(w_i t)

makes the fit *linear* in the unknowns, and one least-squares solve recovers
every amplitude and phase at once.

The speeds below are the standard values in degrees per hour.
"""

import numpy as np

# Constituent speeds, degrees per hour.
SPEEDS = {
    # Long period
    "Sa": 0.0410686,  # solar annual
    "Ssa": 0.0821373,  # solar semiannual
    "Mm": 0.5443747,  # lunar monthly (from lunar orbit eccentricity)
    "Mf": 1.0980331,  # lunar fortnightly (from lunar declination)
    # Diurnal -- these exist only because the orbits are inclined to the equator
    "Q1": 13.3986609,
    "O1": 13.9430356,  # principal lunar diurnal
    "P1": 14.9589314,  # principal solar diurnal
    "K1": 15.0410686,  # lunisolar diurnal
    # Semidiurnal -- the two-bulge tide, and normally the dominant one
    "N2": 28.4397295,  # larger lunar elliptic
    "M2": 28.9841042,  # principal lunar
    "S2": 30.0000000,  # principal solar
    "K2": 30.0821373,  # lunisolar
}

# Amplitude ratios within a species, from the classical expansion of the
# potential (Doodson coefficients). These are independent of latitude and of
# the Love number, which makes them a clean check on an ab initio model.
THEORETICAL_RATIOS = {
    "S2/M2": 0.4652,
    "N2/M2": 0.1915,
    "K2/M2": 0.1266,
    "O1/K1": 0.7108,
    "P1/K1": 0.3312,
    "Q1/K1": 0.1361,
}

DEFAULT_CONSTITUENTS = tuple(SPEEDS)


def angular_frequency(name):
    """Constituent angular frequency, rad/s."""
    return np.radians(SPEEDS[name]) / 3600.0


def period_hours(name):
    """Constituent period, hours."""
    return 360.0 / SPEEDS[name]


def rayleigh_length_days(a, b):
    """Record length needed to separate two constituents, days.

    Two sinusoids are only distinguishable once the record is long enough for
    them to drift a full cycle out of phase: T = 1 / |f_a - f_b|. Fit a pair
    with a shorter record and the least-squares solve will happily split the
    energy between them in whatever way the noise suggests.
    """
    delta = abs(SPEEDS[a] - SPEEDS[b])
    return 360.0 / delta / 24.0 if delta > 0 else np.inf


def unresolved_pairs(names, duration_seconds):
    """Which requested constituent pairs the record is too short to separate."""
    duration_days = duration_seconds / 86400.0
    bad = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            need = rayleigh_length_days(a, b)
            if need > duration_days:
                bad.append((a, b, need))
    return sorted(bad, key=lambda x: -x[2])


def fit(t, eta, names=DEFAULT_CONSTITUENTS):
    """Least-squares fit of tidal constituents.

    Parameters
    ----------
    t     : (M,) array of times, s
    eta   : (M,) array of tide heights, m
    names : constituent names to solve for

    Returns
    -------
    dict mapping name -> {"amplitude": m, "phase_deg": deg, "period_hours": h},
    plus the key "Z0" holding the fitted mean level in m.
    """
    names = tuple(names)

    # Columns: a constant, then a cos/sin pair per constituent.
    columns = [np.ones_like(t)]
    for name in names:
        w = angular_frequency(name)
        columns.append(np.cos(w * t))
        columns.append(np.sin(w * t))
    design = np.stack(columns, axis=1)

    coeffs, *_ = np.linalg.lstsq(design, eta, rcond=None)

    result = {"Z0": coeffs[0]}
    for i, name in enumerate(names):
        c, s = coeffs[1 + 2 * i], coeffs[2 + 2 * i]
        result[name] = {
            "amplitude": float(np.hypot(c, s)),
            "phase_deg": float(np.degrees(np.arctan2(s, c)) % 360.0),
            "period_hours": period_hours(name),
        }
    return result


def format_table(result, names=DEFAULT_CONSTITUENTS):
    """Render a fit result as a readable text table."""
    lines = [
        f"{'name':<5} {'speed (deg/h)':>14} {'period (h)':>11} "
        f"{'amplitude (m)':>14} {'phase (deg)':>12}",
        "-" * 60,
    ]
    for name in sorted(names, key=lambda n: SPEEDS[n]):
        r = result[name]
        lines.append(
            f"{name:<5} {SPEEDS[name]:>14.7f} {r['period_hours']:>11.3f} "
            f"{r['amplitude']:>14.4f} {r['phase_deg']:>12.1f}"
        )
    return "\n".join(lines)
