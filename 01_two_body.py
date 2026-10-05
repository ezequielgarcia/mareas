"""Program 01 -- Two bodies: the Sun and the Earth.

New idea: Newton's law of gravity, integrated numerically. Nothing about tides
yet. The point is to establish that the integrator is trustworthy, by checking
it against what we know analytically:

  * Kepler's 1st law -- the orbit is a closed ellipse with the measured
    semi-major axis and eccentricity we put in;
  * Kepler's 2nd law -- angular momentum is conserved (equal areas in equal
    times);
  * Kepler's 3rd law -- the period is 2*pi*sqrt(a^3 / GM).

If a simulation cannot reproduce a one-body-around-a-fixed-mass ellipse, no
amount of extra physics on top will save it.

Run:  python 01_two_body.py
"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tide.constants import A_EMB, DAY, E_EMB, YEAR
from tide.initial_conditions import two_body_state
from tide.nbody import integrate, total_energy
from tide.orbits import mean_motion_period

FIGURES = "figures"
DT = 3600.0  # 1 hour -- plenty for a one-year orbit
DURATION = 3.0 * YEAR  # long enough to see several perihelion passages


def main():
    pos0, vel0, gm = two_body_state()

    print("Two-body: Sun + Earth (Moon's mass folded into the Earth)")
    print(f"  timestep {DT:.0f} s, duration {DURATION / YEAR:.1f} yr")

    e0 = total_energy(pos0, vel0, gm)
    t, pos, vel = integrate(pos0, vel0, gm, DT, int(DURATION / DT))

    # Earth's position and velocity relative to the Sun.
    rel = pos[:, 1] - pos[:, 0]
    vel_rel = vel[:, 1] - vel[:, 0]
    r = np.linalg.norm(rel, axis=-1)

    # --- Kepler 1: the orbit is an ellipse with the elements we specified ---
    # For an ellipse, r_min = a(1-e) and r_max = a(1+e), so we can invert.
    a_measured = 0.5 * (r.max() + r.min())
    e_measured = (r.max() - r.min()) / (r.max() + r.min())
    print("\nKepler 1 -- shape of the orbit")
    print(f"  semi-major axis  {a_measured:.6e} m   (input {A_EMB:.6e})")
    print(f"  eccentricity     {e_measured:.6f}       (input {E_EMB:.6f})")

    # --- Kepler 2: specific angular momentum is constant ---
    h = np.cross(rel, vel_rel)
    h_mag = np.linalg.norm(h, axis=-1)
    print("\nKepler 2 -- equal areas in equal times")
    print(f"  |r x v| varies by {np.ptp(h_mag) / h_mag.mean():.2e} (relative)")

    # --- Kepler 3: the period ---
    # Two independent measurements. Counting complete revolutions of the
    # heliocentric longitude is the robust one; perihelion-to-perihelion is the
    # intuitive one.
    by_revolution = mean_motion_period(t, rel)

    is_min = (r[1:-1] < r[:-2]) & (r[1:-1] < r[2:])
    perihelion_times = t[1:-1][is_min]
    by_perihelion = (
        np.diff(perihelion_times).mean() if len(perihelion_times) > 1 else np.nan
    )

    predicted = 2.0 * np.pi * np.sqrt(A_EMB**3 / gm.sum())
    print("\nKepler 3 -- the period")
    print(f"  predicted  2*pi*sqrt(a^3/GM)   {predicted / DAY:.5f} d")
    print(f"  measured   per revolution      {by_revolution / DAY:.5f} d"
          f"   ({abs(by_revolution - predicted) / predicted:.1e} relative)")
    print(f"  measured   perihelion to perihelion  {by_perihelion / DAY:.5f} d"
          f"  ({len(perihelion_times)} passages)")
    print(f"  sidereal year, accepted        365.25636 d")

    # --- Integrator health ---
    # A symplectic integrator's energy error oscillates but does not grow.
    energies = np.array([
        total_energy(pos[k], vel[k], gm) for k in (0, len(t) // 2, len(t) - 1)
    ])
    print("\nIntegrator")
    print(f"  fractional energy drift {abs(energies - e0).max() / abs(e0):.2e}")

    # --- Figure ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5))

    au = 1.495978707e11
    ax1.plot(rel[:, 0] / au, rel[:, 1] / au, lw=0.8)
    ax1.plot(0, 0, "o", color="orange", ms=12, label="Sun")
    ax1.set(xlabel="x (au)", ylabel="y (au)",
            title=f"Earth's orbit, {DURATION / YEAR:.0f} years")
    ax1.set_aspect("equal")
    ax1.legend()

    ax2.plot(t / DAY, r / au, lw=0.9)
    ax2.set(
        xlabel="time (days)",
        ylabel="Sun-Earth distance (au)",
        title="Perihelion to aphelion: the 1.7% eccentricity",
    )

    fig.tight_layout()
    fig.savefig(f"{FIGURES}/01_two_body.png", dpi=130)
    print(f"\nWrote {FIGURES}/01_two_body.png")


if __name__ == "__main__":
    import os

    os.makedirs(FIGURES, exist_ok=True)
    main()
