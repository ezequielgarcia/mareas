"""Generate the figures in docs/img/ that illustrate each essay.

Run from the repository root:

    uv run python docs/make_figures.py

One function per essay. Some use data from the project's N-body simulation;
others are analytic constructions or figures from the literature. Which is which
is stated in each docstring and in the figure caption, so there is never any
doubt about what is our own result and what is context.

Note on language: code, identifiers and comments are English, like the rest of
the software. Only the plot labels and titles are Spanish, because they are
content read by the Spanish-language essays in docs/.
"""

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tide.constants import (  # noqa: E402
    A_EMB,
    A_MOON,
    DAY,
    GM_EARTH,
    GM_MOON,
    GM_SUN,
    G_SURFACE,
    R_EARTH,
    YEAR,
)
from tide.initial_conditions import EARTH, MOON, three_body_state  # noqa: E402
from tide.nbody import integrate  # noqa: E402
from tide.orbits import mean_motion_period, osculating_elements  # noqa: E402

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")

# Constants used only for illustration here, not by the simulation itself.
G = 6.674e-11
C_LIGHT = 2.998e8
M_SUN = 1.989e30
M_MOON = 7.348e22
GM_VENUS = 3.2486e14
GM_MARS = 4.2828e13
GM_JUPITER = 1.26687e17
GM_SATURN = 3.7931e16


def _save(fig, name):
    fig.tight_layout()
    path = os.path.join(IMG, name)
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print(f"  {path}")


# --------------------------------------------------------------------- essay 01
def fig_two_bulges():
    """The differential force field, which is what produces the two bulges.

    Exact calculation: residual acceleration = local pull minus the pull at
    Earth's centre. No approximations.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))

    d_vec = np.array([A_MOON, 0.0])  # Moon toward +x
    d = np.linalg.norm(d_vec)

    # Residual acceleration at points on the surface.
    angles = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    r = R_EARTH * np.stack([np.cos(angles), np.sin(angles)], axis=-1)
    sep = d_vec - r
    a_local = GM_MOON * sep / np.linalg.norm(sep, axis=-1)[:, None] ** 3
    a_centre = GM_MOON * d_vec / d**3
    a_residual = a_local - a_centre  # <- this is the tide

    scale = 0.9 * R_EARTH / np.abs(a_residual).max()
    ax1.add_patch(plt.Circle((0, 0), R_EARTH / 1e6, fc="tab:blue", alpha=0.25))
    ax1.quiver(
        r[:, 0] / 1e6, r[:, 1] / 1e6,
        a_residual[:, 0] * scale / 1e6, a_residual[:, 1] * scale / 1e6,
        color="tab:red", width=0.006, scale=1, scale_units="xy", angles="xy",
    )
    ax1.annotate("hacia la Luna", xy=(10.4, -9.6), xytext=(2.6, -9.6),
                 fontsize=9, va="center", color="dimgray",
                 arrowprops=dict(arrowstyle="->", color="dimgray", lw=1.1))
    ax1.set(xlim=(-11, 11), ylim=(-11, 11), xlabel="x (Mm)", ylabel="y (Mm)",
            title="Aceleración residual: estira en el eje,\ncomprime en los flancos")
    ax1.set_aspect("equal")

    # The 3cos^2(psi) - 1 profile along a great circle.
    psi = np.linspace(0, 360, 721)
    profile = 3 * np.cos(np.radians(psi)) ** 2 - 1
    ax2.plot(psi, profile, lw=2, color="tab:blue")
    ax2.axhline(0, color="k", lw=0.6)
    ax2.fill_between(psi, 0, profile, where=profile > 0, alpha=0.2,
                     color="tab:blue", label="pleamar")
    ax2.fill_between(psi, 0, profile, where=profile < 0, alpha=0.2,
                     color="tab:orange", label="bajamar")
    for x, text in ((0, "bajo\nla Luna"), (180, "antípoda")):
        ax2.annotate(text, xy=(x, 2), xytext=(x, 2.55), fontsize=8, ha="center",
                     color="tab:red",
                     arrowprops=dict(arrowstyle="->", color="tab:red", lw=0.8))
    ax2.set(xlim=(0, 360), ylim=(-1.6, 3.1), xticks=[0, 90, 180, 270, 360],
            xlabel="ángulo desde el punto sublunar ψ (grados)",
            ylabel=r"$3\cos^2\psi - 1$",
            title="La función es PAR en cos ψ:\nno distingue el lado cercano del lejano")
    ax2.legend(loc="upper right", fontsize=8)

    fig.suptitle("Documento 01 — por qué hay dos bultos y no uno "
                 "(cálculo exacto, sin aproximar)", fontsize=10, y=1.0)
    _save(fig, "01-dos-bultos.png")


# --------------------------------------------------------------------- essay 02
def fig_lunar_recession():
    """The leading bulge, the torque it produces, and the angular momentum split.

    Left panel: a schematic -- the lead angle is greatly exaggerated so it is
    visible; the real one is a few degrees. Right panel: real numbers for the
    Earth-Moon system.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    # --- Schematic of the leading bulge ---
    lead_angle = np.radians(28.0)  # heavily exaggerated
    theta = np.linspace(0, 2 * np.pi, 400)
    semi_major, semi_minor = 1.62, 1.02  # a good stretched tidal ellipsoid

    x_bulge = (semi_major * np.cos(theta) * np.cos(lead_angle)
               - semi_minor * np.sin(theta) * np.sin(lead_angle))
    y_bulge = (semi_major * np.cos(theta) * np.sin(lead_angle)
               + semi_minor * np.sin(theta) * np.cos(lead_angle))

    ax1.fill(x_bulge, y_bulge, color="tab:cyan", alpha=0.35, ec="tab:blue",
             lw=1.4, zorder=1)
    ax1.add_patch(plt.Circle((0, 0), 0.98, fc="tab:blue", alpha=0.85, zorder=2))

    # Earth-Moon axis, and the bulge axis leading it.
    ax1.plot([0, 4.6], [0, 0], "--", color="dimgray", lw=1.1, zorder=0)
    ax1.plot([-semi_major * np.cos(lead_angle), semi_major * np.cos(lead_angle)],
             [-semi_major * np.sin(lead_angle), semi_major * np.sin(lead_angle)],
             "-", color="tab:blue", lw=1.4, zorder=3)
    arc = np.linspace(0, lead_angle, 40)
    ax1.plot(2.15 * np.cos(arc), 2.15 * np.sin(arc), color="k", lw=1.0)
    ax1.annotate("adelanto", xy=(2.32, 0.52), fontsize=8)

    ax1.plot(4.6, 0, "o", color="darkgray", ms=15, zorder=3)
    ax1.annotate("Luna", xy=(4.6, -0.62), ha="center", fontsize=9)

    # The torque pair: action and reaction.
    ax1.annotate("", xy=(1.62, 0.42), xytext=(0.92, 1.32),
                 arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=2.4))
    ax1.annotate("la Luna tira del bulto\nhacia ATRÁS\n→ frena la Tierra",
                 xy=(0.55, 1.48), fontsize=8, color="tab:red", ha="center",
                 va="bottom")
    ax1.annotate("", xy=(4.62, 0.78), xytext=(3.52, 0.78),
                 arrowprops=dict(arrowstyle="-|>", color="tab:green", lw=2.4))
    ax1.annotate("el bulto tira de la Luna\nhacia ADELANTE\n→ sube de órbita",
                 xy=(4.05, 0.98), fontsize=8, color="tab:green", ha="center",
                 va="bottom")
    ax1.annotate("", xy=(-0.62, 1.32), xytext=(-1.72, 0.52),
                 arrowprops=dict(arrowstyle="-|>", color="dimgray", lw=1.8,
                                 connectionstyle="arc3,rad=-0.35"))
    ax1.annotate("giro de\nla Tierra", xy=(-1.95, 0.05), fontsize=8,
                 color="dimgray", ha="center", va="top")

    ax1.set(xlim=(-2.7, 5.6), ylim=(-2.3, 2.5),
            title="Esquema: la rotación arrastra el bulto\nPOR DELANTE de la "
                  "línea Tierra-Luna")
    ax1.set_aspect("equal")
    ax1.axis("off")

    # --- Angular momentum split (real numbers) ---
    m_earth, m_moon = 5.972e24, M_MOON
    inertia_earth = 0.3307 * m_earth * R_EARTH**2
    omega = 2 * np.pi / 86164.0905
    l_spin = inertia_earth * omega

    reduced_mass = m_earth * m_moon / (m_earth + m_moon)
    l_orbit = reduced_mass * np.sqrt((GM_EARTH + GM_MOON) * A_MOON)

    total = l_spin + l_orbit
    bars = ax2.barh(
        ["rotación\nde la Tierra", "órbita\nde la Luna"],
        [l_spin / 1e34, l_orbit / 1e34],
        color=["tab:orange", "tab:blue"],
    )
    for bar, value in zip(bars, (l_spin, l_orbit)):
        ax2.text(bar.get_width() + 0.06, bar.get_y() + bar.get_height() / 2,
                 f"{value / 1e34:.2f}  ({value / total * 100:.0f}%)",
                 va="center", fontsize=9)
    ax2.set(xlim=(0, 4.3), xlabel="momento angular (10³⁴ kg m²/s)",
            title="La órbita lunar ya guarda 5 veces más\nmomento angular que el "
                  "giro terrestre")
    # A single arrow, from the reservoir that loses to the one that gains.
    ax2.annotate("", xy=(1.45, 0.78), xytext=(1.45, 0.22),
                 arrowprops=dict(arrowstyle="-|>", color="k", lw=2.2))
    ax2.annotate("la marea transfiere\nen este sentido", xy=(1.62, 0.5),
                 fontsize=8.5, va="center")

    fig.suptitle("Documento 02 — cómo la marea aleja la Luna 3.8 cm/año",
                 fontsize=10, y=1.0)
    _save(fig, "02-retroceso-lunar.png")


# --------------------------------------------------------------------- essay 03
def fig_libration():
    """Why we see 59% of the Moon rather than 50%.

    Libration in longitude is computed FROM THE SIMULATION: it is the difference
    between the true and mean longitude of our lunar orbit. Libration in latitude
    is a geometric construction, because this project does not model the Moon's
    rotation (see the caveat in essay 03).
    """
    pos0, vel0, gm = three_body_state()
    dt = 3600.0
    t, pos, vel = integrate(pos0, vel0, gm, dt, int(1.2 * YEAR / dt))
    rel = pos[:, MOON] - pos[:, EARTH]

    # True longitude minus mean longitude = the equation of the centre, which is
    # exactly the optical libration in longitude.
    lon = np.unwrap(np.arctan2(rel[:, 1], rel[:, 0]))
    libration_lon = np.degrees(lon - np.polyval(np.polyfit(t, lon, 1), t))

    # Latitude: the Moon's spin axis is tilted 6.69 deg from its orbit normal.
    # Geometric construction on top of the real orbital phase.
    phase = lon - lon[0]
    libration_lat = -6.69 * np.sin(phase)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.0))

    days = t / DAY
    window = days <= 60
    ax1.plot(days[window], libration_lon[window], lw=1.4,
             label=f"longitud (±{np.abs(libration_lon).max():.1f}°, simulada)")
    ax1.plot(days[window], libration_lat[window], lw=1.4, ls="--",
             label="latitud (±6.7°, geométrica)")
    ax1.axhline(0, color="k", lw=0.5)
    ax1.set(xlabel="tiempo (días)", ylabel="libración (grados)",
            title="La Luna se balancea vista desde aquí")
    ax1.legend(fontsize=8)

    ax2.plot(libration_lon, libration_lat, lw=0.5, color="tab:purple")
    ax2.add_patch(plt.Circle((0, 0), 0.35, fc="k"))
    ax2.annotate("centro aparente\ndel disco", xy=(0, 0), xytext=(2.0, 1.2),
                 fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.8))
    ax2.set(xlabel="libración en longitud (grados)",
            ylabel="libración en latitud (grados)",
            title="Recorrido del punto sub-terrestre en un año\n"
                  "→ asoma el 9% extra de superficie")
    ax2.set_aspect("equal")
    ax2.grid(alpha=0.3)

    fig.suptitle("Documento 03 — la libración: por qué vemos el 59% de la Luna",
                 fontsize=10, y=1.0)
    _save(fig, "03-libracion.png")


# --------------------------------------------------------------------- essay 04
def fig_cube_law():
    """GM/d^3 for everything that is sometimes claimed to 'affect the tides'."""
    cases = [
        ("Luna", GM_MOON, A_MOON, "tab:blue"),
        ("Sol", GM_SUN, A_EMB, "tab:orange"),
        ("Venus\n(máx. acerc.)", GM_VENUS, 0.277 * A_EMB, "tab:green"),
        ("Marte\n(máx. acerc.)", GM_MARS, 0.524 * A_EMB, "tab:red"),
        ("Júpiter\n(máx. acerc.)", GM_JUPITER, 4.204 * A_EMB, "tab:brown"),
        ("Saturno\n(máx. acerc.)", GM_SATURN, 8.54 * A_EMB, "tab:gray"),
        ("una persona\nde 70 kg a 1 m", G * 70.0, 1.0, "tab:purple"),
    ]
    names = [c[0] for c in cases]
    values = np.array([c[1] / c[2] ** 3 for c in cases])
    reference = values[0]  # the Moon

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.0),
                                   gridspec_kw={"width_ratios": [1.35, 1]})

    ax1.bar(names, values, color=[c[3] for c in cases])
    ax1.set_yscale("log")
    ax1.set(ylabel="GM/d³  (s⁻²)",
            title="Capacidad de generar marea, escala logarítmica")
    ax1.tick_params(axis="x", labelsize=7.5)
    for i, value in enumerate(values):
        factor = value / reference
        label = f"×{factor:,.0f}" if factor >= 1 else f"1/{1 / factor:,.0f}"
        ax1.text(i, value * 1.7, label, ha="center", fontsize=7.5)
    ax1.axhline(reference, color="tab:blue", lw=0.8, ls=":")
    ax1.set_ylim(values.min() / 30, values.max() * 60)

    # How mass and distance trade off between Moon and Sun.
    advantages = (GM_SUN / GM_MOON, (A_EMB / A_MOON) ** 3)
    ax2.bar(["masa\n(Sol/Luna)", "distancia³\n(Luna/Sol)"], advantages,
            color=["tab:orange", "tab:blue"])
    ax2.set_yscale("log")
    ax2.set(ylabel="factor de ventaja",
            title="Sol vs Luna: el Sol gana 27 millones en masa,\n"
                  "la Luna gana 59 millones en distancia AL CUBO")
    for i, value in enumerate(advantages):
        ax2.text(i, value * 1.4, f"{value / 1e6:.0f} millones", ha="center",
                 fontsize=9)
    ax2.set_ylim(1e5, 4e8)

    fig.suptitle("Documento 04 — la marea va como 1/d³, no como 1/d²",
                 fontsize=10, y=1.0)
    _save(fig, "04-ley-del-cubo.png")


# --------------------------------------------------------------------- essay 05
def fig_solar_system():
    """Extreme tides: the moons of Jupiter and Saturn, and black holes."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.0))

    # Tide each satellite suffers from its primary. Satellite radius and
    # estimated dissipation are included to show GM/d^3 is not the whole story.
    # Columns: label, primary GM, orbital radius, satellite radius, heat, colour.
    pairs = [
        ("Ío\n← Júpiter", GM_JUPITER, 4.217e8, 1822e3, "~100 TW", "tab:red"),
        ("Europa\n← Júpiter", GM_JUPITER, 6.711e8, 1561e3, None, "tab:orange"),
        ("Ganímedes\n← Júpiter", GM_JUPITER, 1.070e9, 2634e3, None, "tab:olive"),
        ("Encélado\n← Saturno", GM_SATURN, 2.380e8, 252e3, "~16 GW", "tab:cyan"),
        ("Luna\n← Tierra", GM_EARTH, A_MOON, 1737e3, None, "tab:blue"),
        ("Tierra\n← Luna", GM_MOON, A_MOON, R_EARTH, None, "tab:green"),
    ]
    names = [p[0] for p in pairs]
    values = np.array([p[1] / p[2] ** 3 for p in pairs])
    ax1.bar(names, values, color=[p[5] for p in pairs])
    ax1.set_yscale("log")
    ax1.set(ylabel="GM/d³ del primario  (s⁻²)",
            title="Cuánta marea sufre cada satélite\n(referencia: la Luna = 1)")
    ax1.tick_params(axis="x", labelsize=7.5)
    reference = values[4]  # the Moon
    for i, (value, pair) in enumerate(zip(values, pairs)):
        factor = value / reference
        label = f"×{factor:,.0f}" if factor >= 1 else f"1/{1 / factor:,.0f}"
        if pair[4]:
            label += f"\n{pair[4]}"
        ax1.text(i, value * 1.7, label, ha="center", fontsize=7.5)
    ax1.set_ylim(values.min() / 8, values.max() * 90)
    ax1.annotate("Encélado sufre MÁS marea que Ío, pero disipa\n"
                 "10.000 veces menos: el calentamiento crece con\n"
                 "el tamaño del cuerpo, y Encélado tiene 252 km\n"
                 "de radio frente a los 1.822 km de Ío.",
                 xy=(0.03, 0.97), xycoords="axes fraction", fontsize=7.5,
                 va="top", color="dimgray", zorder=6,
                 bbox=dict(fc="white", ec="lightgray", alpha=0.92, pad=3.5))

    # Tide at a black hole's horizon goes as 1/M^2.
    solar_masses = np.logspace(0, 10, 400)
    horizon_tide = C_LIGHT**6 / (4.0 * G**2 * (solar_masses * M_SUN) ** 2)
    ax2.loglog(solar_masses, horizon_tide, lw=2, color="k")
    ax2.axhline(GM_MOON / A_MOON**3, color="tab:blue", lw=1.2, ls="--",
                label="marea de la Luna sobre la Tierra")
    # ~10 s^-2 stretches a human by about 2 g head to foot: the order of
    # magnitude at which this becomes dangerous.
    ax2.axhline(10.0, color="tab:red", lw=1.2, ls=":",
                label="~10 s⁻²: ≈2 g de estiramiento\nentre cabeza y pies")
    for mass, label, dx, dy in (
        (10, "AN estelar (10 M☉):\nte destroza mucho antes\nde llegar", 12, 0.02),
        (4e6, "Sgr A*  (4×10⁶ M☉):\ncruzas el horizonte\nsin notarlo", 8, 4e-4),
    ):
        y = C_LIGHT**6 / (4.0 * G**2 * (mass * M_SUN) ** 2)
        ax2.plot(mass, y, "o", color="tab:purple", ms=9, zorder=5)
        ax2.annotate(label, xy=(mass, y), xytext=(mass * dx, y * dy), fontsize=8,
                     arrowprops=dict(arrowstyle="->", lw=0.8))
    ax2.set(xlabel="masa del agujero negro (masas solares)",
            ylabel="marea en el horizonte (s⁻²)", ylim=(1e-14, 1e13),
            title="Es más seguro caer en un agujero negro GRANDE\n"
                  r"(la marea en el horizonte va como $1/M^2$)")
    ax2.legend(fontsize=7.5, loc="upper right")
    ax2.grid(alpha=0.3, which="both")

    fig.suptitle("Documento 05 — la misma física, llevada al extremo",
                 fontsize=10, y=1.0)
    _save(fig, "05-sistema-solar.png")


# --------------------------------------------------------------------- essay 06
def fig_equilibrium_vs_real():
    """Equilibrium tide against reality, and the reason: basin resonance."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.2))

    # Real spring tidal ranges (approximate values from the literature) against
    # what this project computes.
    sites = [
        ("Báltico", 0.05, "tab:gray"),
        ("Mediterráneo\n(Barcelona)", 0.2, "tab:gray"),
        ("ESTE PROYECTO\n(equilibrio)", 0.65, "tab:red"),
        ("Canarias", 2.5, "tab:blue"),
        ("Cádiz", 3.2, "tab:blue"),
        ("Vigo", 3.5, "tab:blue"),
        ("Solent\n(Portsmouth)", 3.9, "tab:green"),
        ("Bilbao", 4.5, "tab:blue"),
        ("St Malo", 12.0, "tab:purple"),
        ("Bristol Ch.", 13.0, "tab:purple"),
        ("Fundy", 16.0, "tab:purple"),
    ]
    ax1.barh([s[0] for s in sites], [s[1] for s in sites],
             color=[s[2] for s in sites])
    ax1.set_xscale("log")
    ax1.set(xlabel="carrera de marea en vivas (m), escala log", xlim=(0.03, 60),
            title="Un factor 300 entre el Báltico y Fundy.\n"
                  "La gravedad es la misma en todos.")
    ax1.tick_params(axis="y", labelsize=7.5)
    for i, site in enumerate(sites):
        ax1.text(site[1] * 1.15, i, f"{site[1]:g} m", va="center", fontsize=7.5)

    # Quarter-wave resonance: amplification = 1/|cos(omega L / c)|
    depth = 60.0  # typical bay depth, m
    wave_speed = np.sqrt(G_SURFACE * depth)
    omega = 2 * np.pi / (12.4206 * 3600.0)  # M2
    length = np.linspace(1e3, 5e5, 2000)
    amplification = 1.0 / np.abs(np.cos(omega * length / wave_speed))
    amplification = np.minimum(amplification, 60)  # friction caps the peak

    ax2.plot(length / 1e3, amplification, lw=2, color="tab:purple")
    l_resonant = np.pi / 2 * wave_speed / omega
    ax2.axvline(l_resonant / 1e3, color="k", lw=0.8, ls="--")
    ax2.annotate(f"resonancia de cuarto de onda\nL = cT/4 ≈ "
                 f"{l_resonant / 1e3:.0f} km",
                 xy=(l_resonant / 1e3, 30), xytext=(l_resonant / 1e3 - 240, 40),
                 fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.8))
    ax2.plot(270, 1.0 / abs(np.cos(omega * 270e3 / wave_speed)), "o",
             color="tab:red", ms=9, zorder=5)
    ax2.annotate("Bahía de Fundy\n(L ≈ 270 km, h ≈ 60 m)", xy=(270, 40),
                 xytext=(60, 50), fontsize=8, color="tab:red",
                 arrowprops=dict(arrowstyle="->", color="tab:red", lw=0.8))
    ax2.axhline(1, color="dimgray", lw=0.7, ls=":")
    ax2.annotate("sin amplificación", xy=(388, 2.3), fontsize=7.5,
                 color="dimgray")
    ax2.annotate("(sin fricción el pico divergería;\nen la realidad la fricción "
                 "lo limita\na una amplificación de ~5-10)",
                 xy=(305, 52), fontsize=7.5, color="dimgray")
    ax2.set(xlabel="longitud de la bahía L (km)",
            ylabel="amplificación en el fondo de la bahía",
            ylim=(0, 62), xlim=(0, 500),
            title=f"Fórmula de Merian, h = {depth:.0f} m\n"
                  "Fundy está casi exactamente en resonancia con M2")

    fig.suptitle("Documento 06 — la gravedad pone el reloj; el océano pone la "
                 "amplitud", fontsize=10, y=1.0)
    _save(fig, "06-equilibrio-vs-real.png")


# --------------------------------------------------------------------- essay 07
def fig_solent():
    """The Solent's double high water, as the sum of M2 and its M4 harmonic.

    These curves ILLUSTRATE the mechanism; they are not Southampton's real
    harmonic constants. For navigation use the almanac -- see essay 07.
    """
    period_m2 = 12.4206
    t = np.linspace(0, 24.84, 2000)  # one lunar day
    w = 2 * np.pi / period_m2

    a2 = 1.4  # M2 amplitude, m
    a4 = 0.42  # M4 amplitude, m -- above A2/4, which is the threshold

    m2_only = a2 * np.cos(w * t)
    with_m4 = a2 * np.cos(w * t) - a4 * np.cos(2 * w * t)
    # With this sign the fall is slow and the rise fast: "flood dominance", the
    # usual case in shallow estuaries and the one that produces tidal bores.
    asymmetric = a2 * np.cos(w * t) - a4 * np.sin(2 * w * t)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.0))

    ax1.plot(t, m2_only, lw=1.6, ls="--", color="dimgray", label="solo M2")
    ax1.plot(t, with_m4, lw=2.2, color="tab:blue", label="M2 + M4 (desfase 180°)")
    ax1.plot(t, -a4 * np.cos(2 * w * t), lw=1.0, color="tab:orange",
             label="componente M4 sola")
    ax1.axhline(0, color="k", lw=0.5)

    # Mark the central double high water, the one fully visible.
    theta = np.arccos(a2 / (4 * a4))  # exists only if a4 > a2/4
    for sign in (-1, 1):
        t_peak = period_m2 + sign * theta / w
        ax1.plot(t_peak, a2 * np.cos(w * t_peak) - a4 * np.cos(2 * w * t_peak),
                 "v", color="tab:red", ms=10, zorder=5)
    ax1.annotate("dos pleamares separadas\npor un bache de "
                 f"{2 * theta / w * 60:.0f} min",
                 xy=(period_m2,
                     a2 * np.cos(w * period_m2) - a4 * np.cos(2 * w * period_m2)),
                 xytext=(15.4, -0.55), fontsize=8, color="tab:red",
                 arrowprops=dict(arrowstyle="->", color="tab:red", lw=0.9))
    ax1.set(xlabel="tiempo (horas)", ylabel="altura (m)", xlim=(0, 24.84),
            ylim=(-2.3, 1.85),
            title="Doble pleamar: aparece cuando M4 > M2/4\n"
                  r"(aquí $A_4/A_2$ = " f"{a4 / a2:.2f}, umbral 0.25)")
    ax1.legend(fontsize=8, loc="lower right")

    ax2.plot(t, m2_only, lw=1.6, ls="--", color="dimgray", label="solo M2")
    ax2.plot(t, asymmetric, lw=2.2, color="tab:green",
             label="M2 + M4 (desfase 90°)")
    ax2.axhline(0, color="k", lw=0.5)
    ax2.annotate("subida rápida\n(dominancia de flujo)", xy=(9.6, -0.35),
                 xytext=(11.4, -1.75), fontsize=8, color="tab:green",
                 arrowprops=dict(arrowstyle="->", color="tab:green", lw=0.9))
    ax2.annotate("bajada lenta", xy=(3.4, 0.35), xytext=(1.2, -1.2),
                 fontsize=8, color="tab:green",
                 arrowprops=dict(arrowstyle="->", color="tab:green", lw=0.9))
    ax2.set(xlabel="tiempo (horas)", ylabel="altura (m)", xlim=(0, 24.84),
            ylim=(-2.3, 1.85),
            title="El mismo M4 con otra fase da asimetría:\n"
                  "la regla de los doceavos falla aquí")
    ax2.legend(fontsize=8, loc="lower right")

    fig.suptitle("Documento 07 — el Solent: cómo un armónico de aguas someras "
                 "deforma la marea (curvas ilustrativas)", fontsize=10, y=1.0)
    _save(fig, "07-solent.png")


# --------------------------------------------------------------------- essay 08
def fig_virial():
    """The virial theorem: why climbing an orbit slows you, and that it is a MEAN.

    The middle and right panels use the Earth-Moon orbit from the project's
    N-body simulation. The left panel is analytic.
    """
    mu = GM_EARTH + GM_MOON

    pos0, vel0, gm = three_body_state()
    dt = 300.0
    t, pos, vel = integrate(pos0, vel0, gm, dt, int(3.0 * YEAR / dt),
                            sample_every=2)
    r = pos[:, MOON] - pos[:, EARTH]
    v = vel[:, MOON] - vel[:, EARTH]
    d = np.linalg.norm(r, axis=-1)
    kinetic = 0.5 * np.sum(v * v, axis=-1)
    potential = -mu / d

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.6))

    # --- Panel 1: K, U, E against orbital radius (analytic) ---
    a = np.linspace(0.45, 2.1, 400) * A_MOON
    ax1.plot(a / A_MOON, mu / (2 * a) / 1e6, lw=2, color="tab:red",
             label="cinética  $K = +\\mu/2a$")
    ax1.plot(a / A_MOON, -mu / a / 1e6, lw=2, color="tab:blue",
             label="potencial  $U = -\\mu/a$")
    ax1.plot(a / A_MOON, -mu / (2 * a) / 1e6, lw=2.4, color="k",
             label="total  $E = -\\mu/2a$")
    ax1.axhline(0, color="dimgray", lw=0.6)
    ax1.axvline(1.0, color="tab:green", lw=1.1, ls="--")
    ax1.annotate("la Luna,\nhoy", xy=(1.0, -1.9), xytext=(1.25, -2.35),
                 fontsize=8, color="tab:green",
                 arrowprops=dict(arrowstyle="->", color="tab:green", lw=0.9))
    ax1.annotate("", xy=(1.55, 0.34), xytext=(1.05, 0.51),
                 arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=1.8))
    ax1.annotate("al subir de órbita\nla cinética BAJA", xy=(1.16, 0.62),
                 fontsize=8, color="tab:red")
    ax1.set(xlabel="radio orbital  $a$  (en unidades del actual)",
            ylabel="energía específica (MJ/kg)", ylim=(-2.6, 1.5),
            title="$U = -2K$  y  $E = -K$\nañadir energía a una órbita la FRENA")
    ax1.legend(fontsize=8, loc="lower right")

    # --- Panel 2: the instantaneous ratio is NOT 2 ---
    period = mean_motion_period(t, r)
    ratio = -potential / kinetic
    window = t <= 3 * period
    ax2.plot(t[window] / DAY, ratio[window], lw=1.3, color="tab:purple")
    ax2.axhline(2.0, color="k", lw=1.4, ls="--", label="lo que predice el virial")
    for label, idx, color, dx, dy in (
        ("perigeo: 1.86\n(más pequeño → $\\ddot I > 0$)",
         d[window].argmin(), "tab:red", 4.0, -0.005),
        ("apogeo: 2.10\n(más grande → $\\ddot I < 0$)",
         d[window].argmax(), "tab:blue", 3.5, 0.012),
    ):
        ax2.plot(t[idx] / DAY, ratio[idx], "o", color=color, ms=8, zorder=5)
        ax2.annotate(label, xy=(t[idx] / DAY + dx, ratio[idx] + dy),
                     fontsize=8, color=color, va="center")
    ax2.set(xlabel="tiempo (días)", ylabel="$-U/K$  instantáneo",
            ylim=(1.80, 2.20),
            title="Instante a instante NO se cumple\n(3 órbitas de la simulación)")
    ax2.legend(fontsize=8, loc="lower right")

    # --- Panel 3: the ratio OF THE MEANS does converge to 2 ---
    # Note this is -<U>/<K>, the ratio of the means, not the mean of the ratio.
    running_ratio = -np.cumsum(potential) / np.cumsum(kinetic)
    orbits = t / period
    settled = orbits >= 0.35  # the initial transient goes off scale
    ax3.plot(orbits[settled], running_ratio[settled], lw=1.6, color="tab:green")
    ax3.axhline(2.0, color="k", lw=1.4, ls="--")
    ax3.annotate("2 exacto: dos cuerpos aislados", xy=(20, 1.9955), fontsize=8)
    ax3.annotate(f"converge a {running_ratio[-1]:.4f}\n"
                 "el 0.3% que sobra es ⟨f·r⟩,\nla perturbación del Sol",
                 xy=(orbits[-1], running_ratio[-1]), xytext=(11, 2.022),
                 fontsize=8, color="tab:green",
                 arrowprops=dict(arrowstyle="->", color="tab:green", lw=0.9))
    ax3.set(xlabel="órbitas completas promediadas",
            ylabel="$-\\langle U\\rangle / \\langle K\\rangle$",
            ylim=(1.985, 2.032), xlim=(0, 41),
            title="Al promediar, sí\nEL VIRIAL ES UNA LEY DE PROMEDIOS")

    fig.suptitle("Documento 08 — el teorema virial", fontsize=10, y=1.0)
    _save(fig, "08-virial.png")


# --------------------------------------------------------------------- essay 09
# Years to integrate for the stability test. Raising this is how to reproduce the
# 1,500-year figure quoted in essay 09; it costs about 4 minutes instead of 40 s.
STABILITY_YEARS = 250.0


def fig_stability():
    """Robustness of the Earth-Moon system: bounded, and what breaking it costs.

    Panel 1: a long integration of the project's simulation (our own result).
    Panels 2 and 3: analytic arithmetic with the masses of real bodies.
    """
    mu = GM_EARTH + GM_MOON

    pos0, vel0, gm = three_body_state()
    dt = 1800.0
    t, pos, vel = integrate(pos0, vel0, gm, dt,
                            int(STABILITY_YEARS * YEAR / dt), sample_every=40)
    a, e = osculating_elements(pos[:, MOON] - pos[:, EARTH],
                               vel[:, MOON] - vel[:, EARTH], mu)

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15.5, 4.7))

    # --- Panel 1: a and e stay bounded for centuries ---
    # Plotting every sample over centuries is a solid block of ink: the orbit
    # oscillates thousands of times. What matters is that the BAND does not grow,
    # so show the per-year minimum and maximum instead of the raw signal.
    per_year = len(t) // int(STABILITY_YEARS)
    whole = per_year * int(STABILITY_YEARS)
    year_axis = np.arange(int(STABILITY_YEARS)) + 0.5
    a_year = (a[:whole] / 1e3).reshape(-1, per_year)
    e_year = e[:whole].reshape(-1, per_year)

    # Envelope lines only, no fill: two filled bands would overlap into a solid
    # block and hide the one thing that matters, which is that they stay flat.
    ax1.plot(year_axis, a_year.max(axis=1), lw=1.1, color="tab:blue")
    ax1.plot(year_axis, a_year.min(axis=1), lw=1.1, color="tab:blue")
    ax1.set(xlabel="tiempo (años)", ylabel="semieje osculador $a$ (km)",
            ylim=(378.4e3, 389.2e3),
            title=f"{STABILITY_YEARS:.0f} años: envolvente anual de $a$ y $e$.\n"
                  "Las bandas NO crecen")
    ax1.annotate(f"$a$: banda de {(a.max() - a.min()) / a.mean() * 100:.1f}%,\n"
                 "plana de principio a fin",
                 xy=(0.05, 0.76), xycoords="axes fraction", fontsize=8.5,
                 color="tab:blue", va="center")

    ax1_ecc = ax1.twinx()
    ax1_ecc.plot(year_axis, e_year.max(axis=1), lw=1.1, color="tab:orange")
    ax1_ecc.plot(year_axis, e_year.min(axis=1), lw=1.1, color="tab:orange")
    ax1_ecc.set(ylabel="excentricidad $e$", ylim=(0.005, 0.115))
    ax1_ecc.yaxis.label.set_color("tab:orange")
    ax1_ecc.tick_params(axis="y", labelcolor="tab:orange")
    ax1_ecc.annotate("$e$: modulada por los ciclos\napsidal (8.85 a) y nodal "
                     "(18.6 a),\npero también acotada",
                     xy=(0.05, 0.36), xycoords="axes fraction", fontsize=8.5,
                     color="tab:orange", va="center")

    # --- Panel 2: what it would take to unbind the Moon ---
    dv_needed = np.sqrt(2 * mu / A_MOON) - np.sqrt(mu / A_MOON)
    impulse_needed = M_MOON * dv_needed

    impacts = [
        ("Chicxulub\n(~12 km)", 1e15, 20e3, "tab:green"),
        ("Vesta\n(525 km)", 2.6e20, 20e3, "tab:olive"),
        ("Ceres\n(940 km)", 9.4e20, 20e3, "tab:orange"),
        ("Theia\n(tamaño Marte)", 6.4e23, 10e3, "tab:red"),
    ]
    fractions = np.array([i[1] * i[2] / impulse_needed for i in impacts])
    ax2.bar([i[0] for i in impacts], fractions, color=[i[3] for i in impacts])
    ax2.set_yscale("log")
    ax2.axhline(1.0, color="k", lw=1.6, ls="--")
    ax2.annotate("1.0 = justo lo necesario\npara desligar la Luna", xy=(0.05, 1.6),
                 fontsize=8)
    for i, fraction in enumerate(fractions):
        label = (f"{fraction:.0e}".replace("e-0", "e-") if fraction < 0.01
                 else f"{fraction:.2f}")
        ax2.text(i, fraction * 2.2, label, ha="center", fontsize=8)
    ax2.set(ylabel="fracción del impulso necesario", ylim=(1e-7, 3e4),
            title="Chicxulub queda un factor 10⁶ corto.\n"
                  "Solo cuenta algo de clase planetaria.")
    ax2.tick_params(axis="x", labelsize=7.5)

    # --- Panel 3: our Moon is an outlier ---
    # Masses from the literature (standard values, ~1% accuracy).
    moons = [
        ("Caronte / Plutón", 1.586e21, 1.303e22, "lightgray"),
        ("LUNA / TIERRA", M_MOON, 5.972e24, "tab:blue"),
        ("Titán / Saturno", 1.3452e23, 5.6834e26, "tab:orange"),
        ("Tritón / Neptuno", 2.139e22, 1.0241e26, "tab:orange"),
        ("Ganímedes / Júpiter", 1.4819e23, 1.8982e27, "tab:orange"),
        ("Ío / Júpiter", 8.932e22, 1.8982e27, "tab:orange"),
        ("Titania / Urano", 3.400e21, 8.6810e25, "tab:orange"),
        ("Fobos / Marte", 1.0659e16, 6.4171e23, "tab:orange"),
    ]
    moons.sort(key=lambda m: m[1] / m[2])
    ratios = np.array([m[1] / m[2] for m in moons])
    ax3.barh([m[0] for m in moons], ratios, color=[m[3] for m in moons])
    ax3.set_xscale("log")
    for i, ratio in enumerate(ratios):
        ax3.text(ratio * 1.5, i, f"1/{1 / ratio:,.0f}", va="center", fontsize=7.5)
    ax3.set(xlabel="masa del satélite / masa del planeta (escala log)",
            xlim=(3e-9, 3e2),
            title="Nuestra Luna es 52 veces más grande,\nen proporción, que la de "
                  "cualquier planeta")
    ax3.tick_params(axis="y", labelsize=7.5)
    # Notes go in the empty space to the right of the short bars.
    ax3.annotate("planeta enano;\nva de contraste", xy=(1.6, len(moons) - 1),
                 fontsize=7, color="dimgray", va="center")
    ax3.annotate("Mercurio y Venus\nno tienen ninguna", xy=(2e-3, 0),
                 fontsize=8, color="dimgray", va="center",
                 bbox=dict(fc="white", ec="lightgray", alpha=0.9, pad=2.5))

    fig.suptitle("Documento 09 — estabilidad del sistema Tierra-Luna-Sol",
                 fontsize=10, y=1.0)
    _save(fig, "09-estabilidad.png")


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    print("Generating documentation figures:")
    fig_two_bulges()
    fig_lunar_recession()
    fig_libration()
    fig_cube_law()
    fig_solar_system()
    fig_equilibrium_vs_real()
    fig_solent()
    fig_virial()
    fig_stability()
