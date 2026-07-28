"""Checks against values known analytically or from the literature.

These are deliberately physics tests rather than unit tests: each one pins a
number that a correct tidal model must reproduce.
"""

import numpy as np
import pytest

from tide.constants import (
    A_EMB,
    A_MOON,
    DAY,
    GM_EARTH,
    GM_MOON,
    GM_SUN,
    LOVE_FACTOR,
    R_EARTH,
    YEAR,
)
from tide.harmonics import THEORETICAL_RATIOS, fit, period_hours, unresolved_pairs
from tide.initial_conditions import EARTH, MOON, SUN, three_body_state, two_body_state
from tide.nbody import accelerations, integrate, total_energy
from tide.orbits import (
    NODAL_PERIOD,
    mean_motion_period,
    node_longitude,
    perigee_longitude,
    precession_period,
)
from tide.potential import (
    equilibrium_height,
    quadrupole_potential,
    station_position,
    tide_generating_potential,
)


def test_acceleration_matches_newton_for_a_pair():
    pos = np.array([[0.0, 0.0, 0.0], [1.0e9, 0.0, 0.0]])
    gm = np.array([GM_SUN, GM_EARTH])
    a = accelerations(pos, gm)
    # Each body accelerates toward the other with GM_other / r^2.
    assert a[0, 0] == pytest.approx(GM_EARTH / 1.0e18)
    assert a[1, 0] == pytest.approx(-GM_SUN / 1.0e18)
    # Newton's third law: the GM-weighted accelerations cancel. Compare
    # relatively -- the two terms are ~5e16, so an absolute tolerance would be
    # testing float64's mantissa rather than the physics.
    terms = gm[:, None] * a
    residual = np.abs(terms.sum(axis=0)).max()
    assert residual < 1e-12 * np.abs(terms).max()


def test_two_body_period_matches_kepler_third_law():
    pos0, vel0, gm = two_body_state()
    dt = 3600.0
    # Needs to span at least two perihelion passages to measure an interval.
    t, pos, vel = integrate(pos0, vel0, gm, dt, int(2.5 * YEAR / dt))

    rel = pos[:, 1] - pos[:, 0]
    r = np.linalg.norm(rel, axis=-1)
    is_min = (r[1:-1] < r[:-2]) & (r[1:-1] < r[2:])
    perihelia = t[1:-1][is_min]
    assert len(perihelia) >= 2

    predicted = 2.0 * np.pi * np.sqrt(A_EMB**3 / gm.sum())
    assert np.diff(perihelia).mean() == pytest.approx(predicted, rel=1e-3)
    # Unperturbed, so the revolution count agrees far more tightly.
    assert mean_motion_period(t, rel) == pytest.approx(predicted, rel=1e-5)


def test_symplectic_integrator_does_not_leak_energy():
    pos0, vel0, gm = three_body_state()
    dt = 600.0
    e0 = total_energy(pos0, vel0, gm)
    _, pos, vel = integrate(pos0, vel0, gm, dt, int(60 * DAY / dt))
    e1 = total_energy(pos[-1], vel[-1], gm)
    assert abs(e1 - e0) / abs(e0) < 1e-6


def test_sidereal_month(nodal_run):
    """The calibrated initial condition must reproduce the observed month.

    Measured over the full nodal cycle. A one-year window gives 27.333 d --
    off by 4e-4 -- because the solar perturbation has not averaged out yet.
    The mean motion is only well defined over many perturbation cycles.
    """
    sidereal = mean_motion_period(nodal_run["t"], nodal_run["moon"])
    assert sidereal / DAY == pytest.approx(27.321661, rel=2e-4)


def test_station_stays_on_the_sphere_and_completes_one_turn_per_sidereal_day():
    t = np.linspace(0.0, 5.0 * DAY, 2000)
    r = station_position(37.0, -122.0, t)
    assert np.allclose(np.linalg.norm(r, axis=-1), R_EARTH)

    # After exactly one sidereal day the station returns to where it started.
    from tide.constants import SIDEREAL_DAY

    start = station_position(37.0, -122.0, 0.0)
    later = station_position(37.0, -122.0, SIDEREAL_DAY)
    assert np.allclose(start, later, atol=1.0)


def test_tidal_potential_has_no_monopole_or_uniform_part():
    """The mean over the sphere vanishes, and so does the net force."""
    lat = np.linspace(-89.5, 89.5, 180)
    lon = np.linspace(0.0, 358.0, 180)
    lon_g, lat_g = np.meshgrid(lon, lat)
    r = station_position(lat_g, lon_g, 0.0)
    body = np.array([A_MOON, 0.0, 0.0])

    v = tide_generating_potential(r, body, GM_MOON)
    weight = np.cos(np.radians(lat_g))  # area element on a sphere
    mean = (v * weight).sum() / weight.sum()
    assert abs(mean) < 1e-3 * np.abs(v).max()


def test_quadrupole_approximation_is_close_to_exact():
    lat = np.linspace(-90.0, 90.0, 91)
    lon = np.linspace(0.0, 360.0, 181)
    lon_g, lat_g = np.meshgrid(lon, lat)
    r = station_position(lat_g, lon_g, 0.0)
    body = np.array([A_MOON, 0.0, 0.0])

    exact = tide_generating_potential(r, body, GM_MOON)
    approx = quadrupole_potential(r, body, GM_MOON)
    # r/d is about 1/60, and the next term in the expansion is O(r/d).
    assert np.abs(exact - approx).max() / np.abs(exact).max() < 0.05


def test_moon_out_tides_the_sun_by_about_two():
    ratio = (GM_MOON / A_MOON**3) / (GM_SUN / A_EMB**3)
    assert ratio == pytest.approx(2.18, rel=0.02)


def test_two_bulges_per_rotation():
    """The lunar tide at the equator peaks twice per lunar day, not once."""
    pos0, vel0, gm = three_body_state()
    dt = 600.0
    t, pos, vel = integrate(pos0, vel0, gm, dt, int(10 * DAY / dt))
    moon_geo = pos[:, MOON] - pos[:, EARTH]

    eta = equilibrium_height(station_position(0.0, 0.0, t), [(moon_geo, GM_MOON)])
    is_max = (eta[1:-1] > eta[:-2]) & (eta[1:-1] > eta[2:])
    interval = np.diff(t[1:-1][is_max]).mean() / 3600.0
    # Half a lunar day.
    assert interval == pytest.approx(12.4206, rel=5e-3)


def test_m2_period_is_the_semidiurnal_lunar_period():
    assert period_hours("M2") == pytest.approx(12.4206, rel=1e-4)
    assert period_hours("S2") == pytest.approx(12.0, rel=1e-9)


def test_rayleigh_criterion_flags_a_short_record():
    # One month cannot separate S2 from K2 (needs ~183 days).
    bad = unresolved_pairs(("M2", "S2", "K2"), 30 * DAY)
    assert ("S2", "K2", pytest.approx(182.6, rel=1e-2)) in [
        (a, b, need) for a, b, need in bad
    ]
    # Two years can.
    assert unresolved_pairs(("M2", "S2", "K2"), 2 * YEAR) == []


@pytest.fixture(scope="module")
def nodal_run():
    """One full 18.61-year nodal cycle, shared by every test below.

    A shorter record would fail the ratio tests -- see the docstring of
    05_constituents.py. This is the expensive fixture in the suite (~10 s).
    """
    pos0, vel0, gm = three_body_state()
    dt = 900.0
    t, pos, vel = integrate(
        pos0, vel0, gm, dt, int(NODAL_PERIOD / dt), sample_every=4
    )
    return {
        "t": t,
        "moon": pos[:, MOON] - pos[:, EARTH],
        "sun": pos[:, SUN] - pos[:, EARTH],
        "moon_vel": vel[:, MOON] - vel[:, EARTH],
    }


@pytest.fixture(scope="module")
def fitted(nodal_run):
    """Harmonic fit at 30 N over the full nodal cycle."""
    eta = equilibrium_height(
        station_position(30.0, 0.0, nodal_run["t"]),
        [(nodal_run["moon"], GM_MOON), (nodal_run["sun"], GM_SUN)],
    )
    return fit(nodal_run["t"], eta)


def test_nodal_regression_period(nodal_run):
    """The 18.6-year nodal cycle is emergent -- the Sun's perturbation does it."""
    period = precession_period(
        nodal_run["t"], node_longitude(nodal_run["moon"], nodal_run["moon_vel"])
    )
    assert period < 0, "the line of nodes must regress, not advance"
    assert abs(period) / YEAR == pytest.approx(18.61, rel=0.02)


def test_apsidal_precession_period(nodal_run):
    period = precession_period(
        nodal_run["t"],
        perigee_longitude(
            nodal_run["moon"], nodal_run["moon_vel"], GM_EARTH + GM_MOON
        ),
    )
    assert period > 0, "the line of apsides must advance, not regress"
    assert period / YEAR == pytest.approx(8.85, rel=0.02)


@pytest.mark.parametrize("ratio_name", list(THEORETICAL_RATIOS))
def test_constituent_ratios_match_the_classical_expansion(ratio_name, fitted):
    a, b = ratio_name.split("/")
    got = fitted[a]["amplitude"] / fitted[b]["amplitude"]
    assert got == pytest.approx(THEORETICAL_RATIOS[ratio_name], rel=0.03)


def test_m2_amplitude_matches_the_classical_equilibrium_value(nodal_run):
    """Rigid-Earth equilibrium M2 at the equator is ~0.242 m."""
    eta = equilibrium_height(
        station_position(0.0, 0.0, nodal_run["t"]),
        [(nodal_run["moon"], GM_MOON), (nodal_run["sun"], GM_SUN)],
    )
    amplitude = fit(nodal_run["t"], eta)["M2"]["amplitude"]
    assert amplitude / LOVE_FACTOR == pytest.approx(0.242, rel=0.02)


def test_semidiurnal_amplitude_follows_cos_squared_latitude(nodal_run):
    """M2 must go as cos^2(latitude) -- it is a degree-2 sectoral harmonic."""
    amps = []
    for lat in (0.0, 30.0, 60.0):
        eta = equilibrium_height(
            station_position(lat, 0.0, nodal_run["t"]),
            [(nodal_run["moon"], GM_MOON), (nodal_run["sun"], GM_SUN)],
        )
        amps.append(fit(nodal_run["t"], eta)["M2"]["amplitude"])
    for lat, amp in zip((30.0, 60.0), amps[1:]):
        expected = amps[0] * np.cos(np.radians(lat)) ** 2
        assert amp == pytest.approx(expected, rel=1e-3)


def test_semidiurnal_dominates(fitted):
    assert fitted["M2"]["amplitude"] > fitted["K1"]["amplitude"]
    assert fitted["M2"]["amplitude"] > fitted["Mf"]["amplitude"]
