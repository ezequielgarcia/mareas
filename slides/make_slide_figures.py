"""Generate the figures used by the slide decks in slides/.

Run from the repository root:

    uv run python slides/make_slide_figures.py

These are NOT the figures from docs/img/. Those are sized for a document, with
document-sized type, and are unreadable from the back of a room. The ones here
are single-panel, carry large type, and sit on the slide background colour so
they blend into the lamina instead of showing up as a white rectangle.

The physics is the same as in docs/make_figures.py, and where a figure repeats a
calculation the calculation is the exact one, not a sketch: the residual
acceleration field is computed from Newtonian gravity, not drawn by hand.

Code, identifiers and comments are English, like the rest of the software. Only
the plot labels are Spanish, because they are slide content.
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tide.constants import A_EMB, A_MOON, GM_MOON, GM_SUN, R_EARTH  # noqa: E402
from tide.harmonics import SPEEDS, THEORETICAL_RATIOS  # noqa: E402

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
BG = "#FCFCFA"  # must match THEMES["light"]["bg"] in make_slides.py
INK = "#121A21"
BODY = "#333F4B"
MUTED = "#7C8894"
ACCENT = "#0B6E8F"
ACCENT2 = "#C2592E"

plt.rcParams.update(
    {
        "font.family": "Inter",
        "font.size": 17,
        "axes.titlesize": 20,
        "axes.labelsize": 18,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": BODY,
        "text.color": BODY,
        "xtick.color": BODY,
        "ytick.color": BODY,
        "xtick.labelsize": 16,
        "ytick.labelsize": 16,
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "savefig.facecolor": BG,
    }
)


def _save(fig, name):
    path = os.path.join(IMG, name)
    fig.savefig(path, dpi=170, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)
    print(path)


def fig_two_bulges():
    """The differential field: the exact residual acceleration on the surface.

    Residual = the Moon's pull at a point minus its pull at Earth's centre.
    That difference is the tide; no approximation is made.
    """
    fig, ax = plt.subplots(figsize=(11.5, 6.4))

    d_vec = np.array([A_MOON, 0.0])  # Moon toward +x
    d = np.linalg.norm(d_vec)
    angles = np.linspace(0, 2 * np.pi, 28, endpoint=False)
    r = R_EARTH * np.stack([np.cos(angles), np.sin(angles)], axis=-1)
    sep = d_vec - r
    a_local = GM_MOON * sep / np.linalg.norm(sep, axis=-1)[:, None] ** 3
    a_centre = GM_MOON * d_vec / d**3
    a_residual = a_local - a_centre

    scale = 0.95 * R_EARTH / np.abs(a_residual).max()
    unit = R_EARTH / 1e6

    # The shape the field produces, for reference.
    ellipse = plt.matplotlib.patches.Ellipse(
        (0, 0), 2 * 1.30 * unit, 2 * 0.86 * unit,
        fill=False, ec=ACCENT, lw=2.2, ls=(0, (6, 4)), alpha=0.9, zorder=4,
    )
    ax.add_patch(ellipse)
    ax.add_patch(plt.Circle((0, 0), unit, fc="tab:blue", alpha=0.22, zorder=2))
    ax.quiver(
        r[:, 0] / 1e6, r[:, 1] / 1e6,
        a_residual[:, 0] * scale / 1e6, a_residual[:, 1] * scale / 1e6,
        color=ACCENT2, width=0.0055, scale=1, scale_units="xy", angles="xy",
        zorder=3,
    )

    # Past the arrow tips, so the labels never sit on top of the field.
    ax.annotate("estira", xy=(14.1, 0.0), fontsize=19, color=ACCENT2, ha="center",
                va="center", fontweight=600)
    ax.annotate("estira", xy=(-14.1, 0.0), fontsize=19, color=ACCENT2, ha="center",
                va="center", fontweight=600)
    ax.annotate("comprime", xy=(0, 8.4), fontsize=19, color=ACCENT2, ha="center",
                fontweight=600)
    ax.annotate("comprime", xy=(0, -8.9), fontsize=19, color=ACCENT2, ha="center",
                fontweight=600)
    ax.annotate(
        "hacia la Luna", xy=(16.0, -9.4), xytext=(8.4, -9.4), fontsize=17,
        va="center", color=MUTED,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.6),
    )
    ax.set(xlim=(-16.8, 16.8), ylim=(-10.4, 10.4))
    ax.set_aspect("equal")
    ax.axis("off")
    _save(fig, "s02-dos-bultos.png")


def fig_profile():
    """The 3cos^2(psi) - 1 profile: even in cos psi, so +2 at 0 and at 180."""
    # Deliberately wide and short: on a slide the height is what runs out, so a
    # flat figure buys more width for the same vertical budget. The source size
    # is kept close to the size it ends up at, so the type scales ~1:1.
    fig, ax = plt.subplots(figsize=(10.6, 3.3))
    psi = np.linspace(0, 360, 721)
    profile = 3 * np.cos(np.radians(psi)) ** 2 - 1

    ax.fill_between(psi, 0, profile, where=profile > 0, alpha=0.22, color="tab:blue")
    ax.fill_between(psi, 0, profile, where=profile < 0, alpha=0.22, color="tab:orange")
    ax.plot(psi, profile, lw=3.0, color=ACCENT)
    ax.axhline(0, color=MUTED, lw=1.0)

    for x, text in ((0, "bajo la Luna  +2"), (180, "antípoda  +2")):
        ax.annotate(text, xy=(x, 2.05), xytext=(x, 2.9), fontsize=17, ha="center",
                    color=ACCENT2, fontweight=600,
                    arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=1.6))
    ax.annotate("flancos  −1", xy=(90, -1.15), fontsize=17, ha="center", va="top",
                color=BODY)

    ax.set(
        xlim=(-14, 374), ylim=(-2.3, 3.7), xticks=[0, 90, 180, 270, 360],
        xlabel="ángulo desde el punto sublunar  ψ  (grados)",
        ylabel=r"$3\cos^2\psi - 1$",
    )
    ax.spines[["top", "right"]].set_visible(False)
    _save(fig, "s04-perfil.png")


def fig_recession():
    """The leading bulge and the torque pair. The lead angle is exaggerated."""
    fig, ax = plt.subplots(figsize=(10.6, 4.9))

    lead = np.radians(28.0)  # heavily exaggerated; the real one is a few degrees
    theta = np.linspace(0, 2 * np.pi, 400)
    semi_major, semi_minor = 1.62, 1.02
    x = semi_major * np.cos(theta) * np.cos(lead) - semi_minor * np.sin(theta) * np.sin(lead)
    y = semi_major * np.cos(theta) * np.sin(lead) + semi_minor * np.sin(theta) * np.cos(lead)

    ax.fill(x, y, color="tab:cyan", alpha=0.35, ec=ACCENT, lw=2.0, zorder=1)
    ax.add_patch(plt.Circle((0, 0), 0.98, fc="tab:blue", alpha=0.85, zorder=2))
    ax.plot([0, 4.6], [0, 0], "--", color=MUTED, lw=1.4, zorder=0)
    ax.plot(
        [-semi_major * np.cos(lead), semi_major * np.cos(lead)],
        [-semi_major * np.sin(lead), semi_major * np.sin(lead)],
        "-", color=ACCENT, lw=2.0, zorder=3,
    )
    arc = np.linspace(0, lead, 40)
    ax.plot(2.15 * np.cos(arc), 2.15 * np.sin(arc), color=INK, lw=1.4)
    ax.annotate("adelanto", xy=(2.30, 0.46), fontsize=17, color=INK)

    ax.plot(4.6, 0, "o", color="darkgray", ms=24, zorder=3)
    ax.annotate("Luna", xy=(4.6, -0.75), ha="center", fontsize=18, color=BODY)

    ax.annotate("", xy=(1.62, 0.42), xytext=(0.86, 1.46),
                arrowprops=dict(arrowstyle="-|>", color=ACCENT2, lw=3.0))
    ax.annotate("la Luna tira del bulto hacia ATRÁS\n→ frena la Tierra",
                xy=(-0.45, 1.80), fontsize=17, color=ACCENT2, ha="center",
                va="bottom")
    ax.annotate("", xy=(4.66, 0.92), xytext=(3.40, 0.92),
                arrowprops=dict(arrowstyle="-|>", color="#1F7A45", lw=3.0))
    ax.annotate("el bulto tira de la Luna hacia ADELANTE\n→ sube de órbita",
                xy=(5.05, 1.04), fontsize=17, color="#1F7A45", ha="center",
                va="bottom")
    ax.annotate("", xy=(-0.62, 1.32), xytext=(-1.80, 0.52),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=2.4,
                                connectionstyle="arc3,rad=-0.35"))
    ax.annotate("giro de\nla Tierra", xy=(-2.40, 0.05), fontsize=17, color=MUTED,
                ha="center", va="top")

    ax.set(xlim=(-3.2, 7.6), ylim=(-1.75, 2.75))
    ax.set_aspect("equal")
    ax.axis("off")
    _save(fig, "s05-retroceso.png")


def fig_roche():
    """Jupiter's rings, inner moonlets and Shoemaker-Levy 9 against the two
    Roche limits.

    Both limits are computed here from densities alone, because the satellite's
    size cancels out of the derivation. Ring and orbit radii are observed values,
    written out below so there is no doubt which numbers are derived and which
    are measured.
    """
    R_J = 71_492e3        # equatorial radius, m
    RHO_J = 1326.0        # mean density, kg/m^3
    RHO_ICE = 917.0       # a comet or an icy moonlet
    RHO_ROCK = 3000.0

    def roche(coefficient, rho_satellite):
        return coefficient * (RHO_J / rho_satellite) ** (1 / 3)

    rigid_ice = roche(1.26, RHO_ICE)
    fluid_ice = roche(2.44, RHO_ICE)
    rigid_rock = roche(1.26, RHO_ROCK)

    # Observed radii, in R_J.
    halo = (92_000e3 / R_J, 122_500e3 / R_J)
    main = (122_500e3 / R_J, 129_000e3 / R_J)
    gossamer = (129_000e3 / R_J, 221_900e3 / R_J)
    metis = 128_000e3 / R_J
    sl9 = 1.32            # perijove, 7 July 1992

    fig, ax = plt.subplots(figsize=(10.6, 2.9))
    y = 0.0

    ax.add_patch(plt.Rectangle((0, y - 0.25), 1.0, 0.50, fc="#C58A4A",
                               ec="none", zorder=2))
    ax.text(0.5, y, "Júpiter", ha="center", va="center", fontsize=17,
            color="white", fontweight=600, zorder=3)
    ax.plot([0, 3.45], [y, y], color=MUTED, lw=1.0, zorder=1)

    for (x0, x1), alpha in ((halo, 0.30), (main, 0.85), (gossamer, 0.30)):
        ax.add_patch(plt.Rectangle((x0, y - 0.15), x1 - x0, 0.30, fc=ACCENT,
                                   alpha=alpha, ec="none", zorder=2))

    # Labels go above or below the line, never both at the same x.
    for x, text, colour in ((rigid_ice, f"límite rígido (hielo)\n{rigid_ice:.2f} $R_J$", BODY),
                            (fluid_ice, f"límite fluido (hielo)\n{fluid_ice:.2f} $R_J$", ACCENT2)):
        ax.plot([x, x], [-0.34, 0.26], ls=(0, (5, 3)), color=colour, lw=2.0, zorder=4)
        ax.text(x, 0.32, text, ha="center", va="bottom", fontsize=16, color=colour,
                fontweight=600)

    # Two rows of labels under the line, so no leader crosses another label.
    ax.plot(sl9, y, "v", color=ACCENT2, ms=13, zorder=5)
    ax.annotate(f"SL9, {sl9} $R_J$", xy=(sl9 - 0.02, -0.12), xytext=(sl9 - 0.14, -0.40),
                fontsize=16, color=ACCENT2, ha="right", va="top",
                arrowprops=dict(arrowstyle="-", color=ACCENT2, lw=1.2))
    ax.plot(metis, y, "o", color=INK, ms=10, zorder=5)
    ax.annotate("Metis y Adrastea", xy=(metis + 0.02, -0.12), xytext=(metis + 0.18, -0.40),
                fontsize=16, color=INK, ha="left", va="top",
                arrowprops=dict(arrowstyle="-", color=INK, lw=1.2))
    ax.annotate("anillo principal", xy=(sum(main) / 2, -0.16),
                xytext=(sum(main) / 2, -0.80), fontsize=16, ha="center",
                va="top", color=ACCENT, fontweight=600,
                arrowprops=dict(arrowstyle="-", color=ACCENT, lw=1.2))
    ax.text(2.85, -0.80, "halo y anillos tenues", fontsize=15, color=MUTED,
            ha="center", va="top")

    ax.set(xlim=(-0.05, 3.45), ylim=(-1.22, 1.05),
           xticks=[0, 1, 2, 3], xlabel="distancia al centro de Júpiter  ($R_J$)")
    ax.set_yticks([])
    ax.spines[["top", "right", "left"]].set_visible(False)
    _save(fig, "s08-roche.png")
    print(f"       rígido hielo {rigid_ice:.2f}, fluido hielo {fluid_ice:.2f}, "
          f"rígido roca {rigid_rock:.2f} R_J")


def fig_synthesis():
    """Three semidiurnal constituents and their sum: what the machine does.

    Speeds come from tide.harmonics.SPEEDS and the amplitudes from
    tide.harmonics.THEORETICAL_RATIOS, so the curve is the project's own
    constituents, not a drawing. Only the semidiurnal family is shown, because
    at the equator the diurnal species vanishes.
    """
    hours = np.linspace(0, 96, 4000)
    parts = [
        ("M2", 1.0),
        ("S2", THEORETICAL_RATIOS["S2/M2"]),
        ("N2", THEORETICAL_RATIOS["N2/M2"]),
    ]
    curves = [(name, amplitude,
               amplitude * np.cos(np.radians(SPEEDS[name] * hours)))
              for name, amplitude in parts]
    total = sum(curve for _, _, curve in curves)

    fig, ax = plt.subplots(figsize=(10.6, 4.0))
    days = hours / 24.0

    ax.plot(days, total, lw=3.0, color=ACCENT, zorder=3)
    ax.text(4.08, 0.0, "suma =\nla marea", fontsize=17, color=ACCENT,
            fontweight=600, va="center", ha="left")

    offsets = (-3.0, -4.9, -6.2)
    for (name, amplitude, curve), y0 in zip(curves, offsets):
        ax.plot(days, y0 + curve, lw=1.8, color=BODY, alpha=0.75)
        ax.plot([0, 4], [y0, y0], lw=0.8, color=MUTED, alpha=0.5, zorder=0)
        period = 360.0 / SPEEDS[name]
        ax.text(4.08, y0, f"{name}   {period:.2f} h".replace(".", ","),
                fontsize=17, color=BODY, va="center", ha="left")

    ax.set(xlim=(0, 5.25), ylim=(-7.0, 2.0), xticks=[0, 1, 2, 3, 4],
           xlabel="días")
    ax.set_yticks([])
    ax.spines[["top", "right", "left"]].set_visible(False)
    _save(fig, "s10-sintesis.png")


# --- Roche ellipsoids, for the virial annex -------------------------------
# The index symbols of a homogeneous ellipsoid,
#     A_i = a1 a2 a3 int_0^inf du / [ (a_i^2 + u) Delta(u) ],
#     Delta(u) = sqrt((a1^2+u)(a2^2+u)(a3^2+u)),
# mapped onto (0, 1) by u = 1/t - 1 and integrated with Gauss-Legendre.
_NODES, _WEIGHTS = np.polynomial.legendre.leggauss(240)
_T = 0.5 * (_NODES + 1.0)
_W = 0.5 * _WEIGHTS


def index_symbols(axes):
    """A_1, A_2, A_3 for semi-axes `axes`. They satisfy A_1 + A_2 + A_3 = 2."""
    a = np.asarray(axes, float)
    u = 1.0 / _T - 1.0
    jacobian = 1.0 / _T**2
    delta = np.sqrt(np.prod(a[:, None] ** 2 + u[None, :], axis=0))
    return np.array([np.prod(a) * np.sum(_W * jacobian / ((ai**2 + u) * delta))
                     for ai in a])


def roche_nu(alpha, beta):
    """nu = n^2 / (pi G rho) from each of the two equilibrium conditions.

    Hydrostatic equilibrium in the Hill potential forces the three quantities
        a1^2 (A1 - 3nu/2),  a2^2 A2,  a3^2 (A3 + nu/2)
    to be equal. Reading nu off the first pair and off the second pair gives two
    values; they agree only on the equilibrium sequence.
    """
    a1 = (alpha * beta) ** (-1.0 / 3.0)  # volume a1 a2 a3 = 1
    A1, A2, A3 = index_symbols([a1, a1 * alpha, a1 * beta])
    return ((2.0 / 3.0) * (A1 - alpha**2 * A2),
            2.0 * (alpha**2 * A2 - beta**2 * A3) / beta**2)


def roche_sequence(alphas):
    """Walk the equilibrium sequence: for each a2/a1, the a3/a1 that closes it."""
    out = []
    for alpha in alphas:
        lo, hi = 1e-4, alpha - 1e-7
        first = np.subtract(*roche_nu(alpha, lo))
        for _ in range(90):
            mid = 0.5 * (lo + hi)
            if np.subtract(*roche_nu(alpha, mid)) * first > 0:
                lo = mid
            else:
                hi = mid
        beta = 0.5 * (lo + hi)
        out.append((alpha, beta, roche_nu(alpha, beta)[0]))
    return np.array(out)


def fig_roche_sequence():
    """Where the sequence of Roche ellipsoids ends -- the fluid Roche limit.

    nu = n^2/(pi G rho) converts to distance with nu = (4/3)(R/d)^3 rho_M/rho_m,
    so the vertical axis is d in units of R (rho_M/rho_m)^(1/3): the Roche
    coefficient itself. The sequence has a minimum, and that minimum is the
    limit. Nothing here is fitted or looked up.
    """
    seq = roche_sequence(np.linspace(0.34, 0.72, 200))
    coefficient = (4.0 / (3.0 * seq[:, 2])) ** (1.0 / 3.0)
    i = int(np.argmin(coefficient))
    # Parabola through the minimum and its neighbours, for a sharper value.
    fit = np.polyfit(seq[i - 1:i + 2, 0], coefficient[i - 1:i + 2], 2)
    alpha_c = -fit[1] / (2 * fit[0])
    c_min = np.polyval(fit, alpha_c)
    beta_c = roche_sequence([alpha_c])[0, 1]

    # Zoomed on the turning point: that is where the whole result lives. The
    # rigid 1.26 is two thirds of a unit below and would flatten the curve to a
    # line, so it is left to the slide text.
    fig, ax = plt.subplots(figsize=(10.6, 3.3))
    ax.axhspan(2.30, c_min, color=ACCENT2, alpha=0.08, zorder=0)
    ax.plot(seq[:, 0], coefficient, lw=3.0, color=ACCENT)
    ax.plot(alpha_c, c_min, "o", color=ACCENT2, ms=13, zorder=4)
    label = ("límite de Roche fluido:   $d = "
             + f"{c_min:.3f}".replace(".", ",")
             + r"\,R\,(\rho_M/\rho_m)^{1/3}$")
    ax.annotate(label, xy=(alpha_c, c_min + 0.008),
                xytext=(0.355, 2.715),
                fontsize=17, color=ACCENT2, fontweight=600, ha="left", va="bottom",
                arrowprops=dict(arrowstyle="->", color=ACCENT2, lw=1.8,
                                connectionstyle="arc3,rad=-0.18"))
    ax.text(0.715, c_min - 0.022, "sin equilibrio: la marea lo desarma",
            fontsize=16, color=ACCENT2, ha="right", va="top")
    ax.set(xlim=(0.335, 0.725), ylim=(2.33, 2.80),
           xticks=[0.4, 0.5, 0.6, 0.7],
           yticks=[2.4, 2.5, 2.6, 2.7, 2.8],
           xlabel=r"achatamiento del elipsoide   $a_2/a_1$",
           ylabel=r"$d \,/\, R(\rho_M/\rho_m)^{1/3}$")
    ax.spines[["top", "right"]].set_visible(False)
    _save(fig, "s19-roche-virial.png")
    print(f"       nu_max = {4 / (3 * c_min**3):.6f}  ->  C = {c_min:.4f} "
          f"en a2/a1 = {alpha_c:.3f}, a3/a1 = {beta_c:.3f}")


def main():
    os.makedirs(IMG, exist_ok=True)
    fig_two_bulges()
    fig_profile()
    fig_recession()
    fig_roche()
    fig_synthesis()
    fig_roche_sequence()


if __name__ == "__main__":
    main()
