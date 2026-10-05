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


def main():
    os.makedirs(IMG, exist_ok=True)
    fig_two_bulges()
    fig_profile()
    fig_recession()


if __name__ == "__main__":
    main()
