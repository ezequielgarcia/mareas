"""Genera las figuras de docs/img/ que ilustran cada documento.

Ejecutar desde la raíz del repositorio:

    uv run python docs/generar_figuras.py

Cada función corresponde a un documento. Algunas usan datos de la simulación de
N-cuerpos del proyecto; otras son construcciones analíticas o datos de la
literatura. Está indicado en cada caso, tanto aquí como en el pie de la figura,
para que nunca haya duda sobre qué es resultado propio y qué es contexto.
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

# Constantes que solo se usan aquí, para ilustrar.
G = 6.674e-11
C_LIGHT = 2.998e8
M_SUN = 1.989e30
GM_VENUS = 3.2486e14
GM_MARS = 4.2828e13
GM_JUPITER = 1.26687e17
GM_SATURN = 3.7931e16


def _guardar(fig, nombre):
    fig.tight_layout()
    ruta = os.path.join(IMG, nombre)
    fig.savefig(ruta, dpi=130)
    plt.close(fig)
    print(f"  {ruta}")


# ---------------------------------------------------------------- documento 01
def fig_dos_bultos():
    """El campo de fuerzas diferencial, que es el origen de los dos bultos.

    Cálculo exacto: aceleración residual = atracción local menos atracción en el
    centro de la Tierra. Nada de aproximaciones.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2))

    d_vec = np.array([A_MOON, 0.0])  # Luna hacia +x
    d = np.linalg.norm(d_vec)

    # Aceleración residual en puntos de la superficie.
    ang = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    r = R_EARTH * np.stack([np.cos(ang), np.sin(ang)], axis=-1)
    sep = d_vec - r
    a_local = GM_MOON * sep / np.linalg.norm(sep, axis=-1)[:, None] ** 3
    a_centro = GM_MOON * d_vec / d**3
    a_res = a_local - a_centro  # <- esto es la marea

    escala = 0.9 * R_EARTH / np.abs(a_res).max()
    ax1.add_patch(plt.Circle((0, 0), R_EARTH / 1e6, fc="tab:blue", alpha=0.25))
    ax1.quiver(
        r[:, 0] / 1e6, r[:, 1] / 1e6,
        a_res[:, 0] * escala / 1e6, a_res[:, 1] * escala / 1e6,
        color="tab:red", width=0.006, scale=1, scale_units="xy", angles="xy",
    )
    ax1.annotate("hacia la Luna", xy=(10.4, -9.6), xytext=(2.6, -9.6),
                 fontsize=9, va="center", color="dimgray",
                 arrowprops=dict(arrowstyle="->", color="dimgray", lw=1.1))
    ax1.set(xlim=(-11, 11), ylim=(-11, 11), xlabel="x (Mm)", ylabel="y (Mm)",
            title="Aceleración residual: estira en el eje,\ncomprime en los flancos")
    ax1.set_aspect("equal")

    # El perfil 3cos^2(psi) - 1 sobre un círculo máximo.
    psi = np.linspace(0, 360, 721)
    perfil = 3 * np.cos(np.radians(psi)) ** 2 - 1
    ax2.plot(psi, perfil, lw=2, color="tab:blue")
    ax2.axhline(0, color="k", lw=0.6)
    ax2.fill_between(psi, 0, perfil, where=perfil > 0, alpha=0.2,
                     color="tab:blue", label="pleamar")
    ax2.fill_between(psi, 0, perfil, where=perfil < 0, alpha=0.2,
                     color="tab:orange", label="bajamar")
    for x, txt in ((0, "bajo\nla Luna"), (180, "antípoda")):
        ax2.annotate(txt, xy=(x, 2), xytext=(x, 2.55), fontsize=8, ha="center",
                     color="tab:red",
                     arrowprops=dict(arrowstyle="->", color="tab:red", lw=0.8))
    ax2.set(xlim=(0, 360), ylim=(-1.6, 3.1), xticks=[0, 90, 180, 270, 360],
            xlabel="ángulo desde el punto sublunar ψ (grados)",
            ylabel=r"$3\cos^2\psi - 1$",
            title="La función es PAR en cos ψ:\nno distingue el lado cercano del lejano")
    ax2.legend(loc="upper right", fontsize=8)

    fig.suptitle("Documento 01 — por qué hay dos bultos y no uno "
                 "(cálculo exacto, sin aproximar)", fontsize=10, y=1.0)
    _guardar(fig, "01-dos-bultos.png")


# ---------------------------------------------------------------- documento 02
def fig_retroceso_lunar():
    """El bulto adelantado, el par que produce, y el reparto de momento angular.

    Panel izquierdo: esquema (el desfase está muy exagerado; el real son pocos
    grados). Panel derecho: números reales del sistema Tierra-Luna.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    # --- Esquema del bulto adelantado ---
    desfase = np.radians(28.0)  # muy exagerado; el real son pocos grados
    th = np.linspace(0, 2 * np.pi, 400)
    a_b, b_b = 1.62, 1.02  # elipsoide de marea bien alargado

    xr = a_b * np.cos(th) * np.cos(desfase) - b_b * np.sin(th) * np.sin(desfase)
    yr = a_b * np.cos(th) * np.sin(desfase) + b_b * np.sin(th) * np.cos(desfase)

    ax1.fill(xr, yr, color="tab:cyan", alpha=0.35, ec="tab:blue", lw=1.4,
             zorder=1)
    ax1.add_patch(plt.Circle((0, 0), 0.98, fc="tab:blue", alpha=0.85, zorder=2))

    # Eje Tierra-Luna, y eje del bulto adelantado respecto a él.
    ax1.plot([0, 4.6], [0, 0], "--", color="dimgray", lw=1.1, zorder=0)
    ax1.plot([-a_b * np.cos(desfase), a_b * np.cos(desfase)],
             [-a_b * np.sin(desfase), a_b * np.sin(desfase)],
             "-", color="tab:blue", lw=1.4, zorder=3)
    arco = np.linspace(0, desfase, 40)
    ax1.plot(2.15 * np.cos(arco), 2.15 * np.sin(arco), color="k", lw=1.0)
    ax1.annotate("adelanto", xy=(2.32, 0.52), fontsize=8)

    ax1.plot(4.6, 0, "o", color="darkgray", ms=15, zorder=3)
    ax1.annotate("Luna", xy=(4.6, -0.62), ha="center", fontsize=9)

    # Par de fuerzas: acción y reacción.
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

    # --- Reparto de momento angular (números reales) ---
    I_tierra = 0.3307 * 5.972e24 * R_EARTH**2
    omega = 2 * np.pi / 86164.0905
    L_giro = I_tierra * omega

    m_t, m_l = 5.972e24, 7.348e22
    mu_red = m_t * m_l / (m_t + m_l)
    L_orbita = mu_red * np.sqrt((GM_EARTH + GM_MOON) * A_MOON)

    total = L_giro + L_orbita
    barras = ax2.barh(
        ["rotación\nde la Tierra", "órbita\nde la Luna"],
        [L_giro / 1e34, L_orbita / 1e34],
        color=["tab:orange", "tab:blue"],
    )
    for barra, valor in zip(barras, (L_giro, L_orbita)):
        ax2.text(barra.get_width() + 0.06, barra.get_y() + barra.get_height() / 2,
                 f"{valor / 1e34:.2f}  ({valor / total * 100:.0f}%)",
                 va="center", fontsize=9)
    ax2.set(xlim=(0, 4.3), xlabel="momento angular (10³⁴ kg m²/s)",
            title="La órbita lunar ya guarda 5 veces más\nmomento angular que el "
                  "giro terrestre")
    # Una sola flecha, del depósito que pierde al que gana.
    ax2.annotate("", xy=(1.45, 0.78), xytext=(1.45, 0.22),
                 arrowprops=dict(arrowstyle="-|>", color="k", lw=2.2))
    ax2.annotate("la marea transfiere\nen este sentido", xy=(1.62, 0.5),
                 fontsize=8.5, va="center")

    fig.suptitle("Documento 02 — cómo la marea aleja la Luna 3.8 cm/año",
                 fontsize=10, y=1.0)
    _guardar(fig, "02-retroceso-lunar.png")


# ---------------------------------------------------------------- documento 03
def fig_libracion():
    """Por qué vemos el 59% de la Luna y no el 50%.

    La libración en longitud se calcula A PARTIR DE LA SIMULACIÓN: es la
    diferencia entre la longitud verdadera y la media de nuestra órbita lunar.
    La libración en latitud es una construcción geométrica, porque este proyecto
    no modela la rotación de la Luna (ver el aviso del documento 03).
    """
    pos0, vel0, gm = three_body_state()
    dt = 3600.0
    t, pos, vel = integrate(pos0, vel0, gm, dt, int(1.2 * YEAR / dt))
    rel = pos[:, MOON] - pos[:, EARTH]

    # Longitud verdadera menos longitud media = ecuación del centro. Eso es
    # exactamente la libración óptica en longitud.
    lon = np.unwrap(np.arctan2(rel[:, 1], rel[:, 0]))
    ajuste = np.polyfit(t, lon, 1)
    libracion_lon = np.degrees(lon - np.polyval(ajuste, t))

    # Latitud: el eje de rotación lunar está inclinado 6.69 deg respecto a la
    # normal de su órbita. Construcción geométrica sobre la fase orbital real.
    fase = lon - lon[0]
    libracion_lat = -6.69 * np.sin(fase)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.0))

    dias = t / DAY
    sel = dias <= 60
    ax1.plot(dias[sel], libracion_lon[sel], lw=1.4,
             label=f"longitud (±{np.abs(libracion_lon).max():.1f}°, simulada)")
    ax1.plot(dias[sel], libracion_lat[sel], lw=1.4, ls="--",
             label="latitud (±6.7°, geométrica)")
    ax1.axhline(0, color="k", lw=0.5)
    ax1.set(xlabel="tiempo (días)", ylabel="libración (grados)",
            title="La Luna se balancea vista desde aquí")
    ax1.legend(fontsize=8)

    ax2.plot(libracion_lon, libracion_lat, lw=0.5, color="tab:purple")
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
    _guardar(fig, "03-libracion.png")


# ---------------------------------------------------------------- documento 04
def fig_ley_cubo():
    """GM/d^3 para todo lo que a veces se dice que 'afecta a las mareas'."""
    casos = [
        ("Luna", GM_MOON, A_MOON, "tab:blue"),
        ("Sol", GM_SUN, A_EMB, "tab:orange"),
        ("Venus\n(máx. acerc.)", GM_VENUS, 0.277 * A_EMB, "tab:green"),
        ("Marte\n(máx. acerc.)", GM_MARS, 0.524 * A_EMB, "tab:red"),
        ("Júpiter\n(máx. acerc.)", GM_JUPITER, 4.204 * A_EMB, "tab:brown"),
        ("Saturno\n(máx. acerc.)", GM_SATURN, 8.54 * A_EMB, "tab:gray"),
        ("una persona\nde 70 kg a 1 m", G * 70.0, 1.0, "tab:purple"),
    ]
    nombres = [c[0] for c in casos]
    valores = np.array([c[1] / c[2] ** 3 for c in casos])
    colores = [c[3] for c in casos]
    ref = valores[0]  # la Luna

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.0),
                                   gridspec_kw={"width_ratios": [1.35, 1]})

    ax1.bar(nombres, valores, color=colores)
    ax1.set_yscale("log")
    ax1.set(ylabel="GM/d³  (s⁻²)",
            title="Capacidad de generar marea, escala logarítmica")
    ax1.tick_params(axis="x", labelsize=7.5)
    for i, v in enumerate(valores):
        factor = v / ref
        etiqueta = f"×{factor:,.0f}" if factor >= 1 else f"1/{1 / factor:,.0f}"
        ax1.text(i, v * 1.7, etiqueta, ha="center", fontsize=7.5)
    ax1.axhline(ref, color="tab:blue", lw=0.8, ls=":")
    ax1.set_ylim(valores.min() / 30, valores.max() * 60)

    # Cómo se compensan masa y distancia entre Luna y Sol.
    ax2.bar(["masa\n(Sol/Luna)", "distancia³\n(Luna/Sol)"],
            [GM_SUN / GM_MOON, (A_EMB / A_MOON) ** 3],
            color=["tab:orange", "tab:blue"])
    ax2.set_yscale("log")
    ax2.set(ylabel="factor de ventaja",
            title="Sol vs Luna: el Sol gana 27 millones en masa,\n"
                  "la Luna gana 59 millones en distancia AL CUBO")
    for i, v in enumerate((GM_SUN / GM_MOON, (A_EMB / A_MOON) ** 3)):
        ax2.text(i, v * 1.4, f"{v / 1e6:.0f} millones", ha="center", fontsize=9)
    ax2.set_ylim(1e5, 4e8)

    fig.suptitle("Documento 04 — la marea va como 1/d³, no como 1/d²",
                 fontsize=10, y=1.0)
    _guardar(fig, "04-ley-del-cubo.png")


# ---------------------------------------------------------------- documento 05
def fig_sistema_solar():
    """Mareas extremas: lunas de Júpiter y Saturno, y agujeros negros."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.0))

    # Marea que sufre cada satélite por parte de su primario. Radio del
    # satélite y disipación estimada, para mostrar que no basta con GM/d^3.
    pares = [
        ("Ío\n← Júpiter", GM_JUPITER, 4.217e8, 1822e3, "~100 TW", "tab:red"),
        ("Europa\n← Júpiter", GM_JUPITER, 6.711e8, 1561e3, None, "tab:orange"),
        ("Ganímedes\n← Júpiter", GM_JUPITER, 1.070e9, 2634e3, None, "tab:olive"),
        ("Encélado\n← Saturno", GM_SATURN, 2.380e8, 252e3, "~16 GW", "tab:cyan"),
        ("Luna\n← Tierra", GM_EARTH, A_MOON, 1737e3, None, "tab:blue"),
        ("Tierra\n← Luna", GM_MOON, A_MOON, R_EARTH, None, "tab:green"),
    ]
    nombres = [p[0] for p in pares]
    valores = np.array([p[1] / p[2] ** 3 for p in pares])
    ax1.bar(nombres, valores, color=[p[5] for p in pares])
    ax1.set_yscale("log")
    ax1.set(ylabel="GM/d³ del primario  (s⁻²)",
            title="Cuánta marea sufre cada satélite\n(referencia: la Luna = 1)")
    ax1.tick_params(axis="x", labelsize=7.5)
    referencia = valores[4]  # la Luna
    for i, (v, par) in enumerate(zip(valores, pares)):
        factor = v / referencia
        etiqueta = f"×{factor:,.0f}" if factor >= 1 else f"1/{1 / factor:,.0f}"
        if par[4]:
            etiqueta += f"\n{par[4]}"
        ax1.text(i, v * 1.7, etiqueta, ha="center", fontsize=7.5)
    ax1.set_ylim(valores.min() / 8, valores.max() * 90)
    ax1.annotate("Encélado sufre MÁS marea que Ío, pero disipa\n"
                 "10.000 veces menos: el calentamiento crece con\n"
                 "el tamaño del cuerpo, y Encélado tiene 252 km\n"
                 "de radio frente a los 1.822 km de Ío.",
                 xy=(0.03, 0.97), xycoords="axes fraction", fontsize=7.5,
                 va="top", color="dimgray", zorder=6,
                 bbox=dict(fc="white", ec="lightgray", alpha=0.92, pad=3.5))

    # Marea en el horizonte de un agujero negro: va como 1/M^2.
    masas = np.logspace(0, 10, 400)  # masas solares
    m_kg = masas * M_SUN
    marea_horizonte = C_LIGHT**6 / (4.0 * G**2 * m_kg**2)
    ax2.loglog(masas, marea_horizonte, lw=2, color="k")
    ax2.axhline(GM_MOON / A_MOON**3, color="tab:blue", lw=1.2, ls="--",
                label="marea de la Luna sobre la Tierra")
    # ~10 s^-2 estira unos 2 g entre cabeza y pies: el orden de magnitud en que
    # esto se vuelve peligroso para un cuerpo humano.
    ax2.axhline(10.0, color="tab:red", lw=1.2, ls=":",
                label="~10 s⁻²: ≈2 g de estiramiento\nentre cabeza y pies")
    for m, etiqueta, dx, dy in (
        (10, "AN estelar (10 M☉):\nte destroza mucho antes\nde llegar", 12, 0.02),
        (4e6, "Sgr A*  (4×10⁶ M☉):\ncruzas el horizonte\nsin notarlo", 8, 4e-4),
    ):
        y = C_LIGHT**6 / (4.0 * G**2 * (m * M_SUN) ** 2)
        ax2.plot(m, y, "o", color="tab:purple", ms=9, zorder=5)
        ax2.annotate(etiqueta, xy=(m, y), xytext=(m * dx, y * dy), fontsize=8,
                     arrowprops=dict(arrowstyle="->", lw=0.8))
    ax2.set(xlabel="masa del agujero negro (masas solares)",
            ylabel="marea en el horizonte (s⁻²)", ylim=(1e-14, 1e13),
            title="Es más seguro caer en un agujero negro GRANDE\n"
                  r"(la marea en el horizonte va como $1/M^2$)")
    ax2.legend(fontsize=7.5, loc="upper right")
    ax2.grid(alpha=0.3, which="both")

    fig.suptitle("Documento 05 — la misma física, llevada al extremo",
                 fontsize=10, y=1.0)
    _guardar(fig, "05-sistema-solar.png")


# ---------------------------------------------------------------- documento 06
def fig_equilibrio_vs_real():
    """Marea de equilibrio frente a la realidad, y por qué: resonancia."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.2))

    # Carreras de marea reales (valores aproximados de la literatura) frente a
    # lo que da este proyecto.
    sitios = [
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
    nombres = [s[0] for s in sitios]
    rangos = [s[1] for s in sitios]
    ax1.barh(nombres, rangos, color=[s[2] for s in sitios])
    ax1.set_xscale("log")
    ax1.set(xlabel="carrera de marea en vivas (m), escala log",
            title="Un factor 300 entre el Báltico y Fundy.\n"
                  "La gravedad es la misma en todos.")
    ax1.tick_params(axis="y", labelsize=7.5)
    for i, r in enumerate(rangos):
        ax1.text(r * 1.15, i, f"{r:g} m", va="center", fontsize=7.5)
    ax1.set_xlim(0.03, 60)

    # Resonancia de cuarto de onda: amplificación = 1/|cos(omega L / c)|
    h = 60.0  # profundidad típica de bahía, m
    c = np.sqrt(G_SURFACE * h)
    T_m2 = 12.4206 * 3600.0
    omega = 2 * np.pi / T_m2
    L = np.linspace(1e3, 5e5, 2000)
    amplificacion = 1.0 / np.abs(np.cos(omega * L / c))
    amplificacion = np.minimum(amplificacion, 60)  # la fricción limita el pico

    ax2.plot(L / 1e3, amplificacion, lw=2, color="tab:purple")
    L_resonante = np.pi / 2 * c / omega
    ax2.axvline(L_resonante / 1e3, color="k", lw=0.8, ls="--")
    ax2.annotate(f"resonancia de cuarto de onda\nL = cT/4 ≈ "
                 f"{L_resonante / 1e3:.0f} km",
                 xy=(L_resonante / 1e3, 30), xytext=(L_resonante / 1e3 - 240, 40),
                 fontsize=8, arrowprops=dict(arrowstyle="->", lw=0.8))
    ax2.plot(270, 1.0 / abs(np.cos(omega * 270e3 / c)), "o", color="tab:red",
             ms=9, zorder=5)
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
            title=f"Fórmula de Merian, h = {h:.0f} m\n"
                  "Fundy está casi exactamente en resonancia con M2")

    fig.suptitle("Documento 06 — la gravedad pone el reloj; el océano pone la "
                 "amplitud", fontsize=10, y=1.0)
    _guardar(fig, "06-equilibrio-vs-real.png")


# ---------------------------------------------------------------- documento 07
def fig_solent():
    """La doble pleamar del Solent, como suma de M2 y su armónico M4.

    Curvas ILUSTRATIVAS del mecanismo, no constantes armónicas reales de
    Southampton. Para navegar hay que usar el almanaque; ver el documento 07.
    """
    T_m2 = 12.4206
    t = np.linspace(0, 24.84, 2000)  # un día lunar
    w = 2 * np.pi / T_m2

    A2 = 1.4  # amplitud M2, m
    A4 = 0.42  # amplitud M4, m -- por encima de A2/4, que es el umbral

    solo_m2 = A2 * np.cos(w * t)
    con_m4 = A2 * np.cos(w * t) - A4 * np.cos(2 * w * t)
    # Con este signo la bajada es lenta y la subida rápida: "dominancia de
    # flujo", el caso habitual en estuarios someros y el que forma macareos.
    asimetrica = A2 * np.cos(w * t) - A4 * np.sin(2 * w * t)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.0))

    ax1.plot(t, solo_m2, lw=1.6, ls="--", color="dimgray", label="solo M2")
    ax1.plot(t, con_m4, lw=2.2, color="tab:blue", label="M2 + M4 (desfase 180°)")
    ax1.plot(t, -A4 * np.cos(2 * w * t), lw=1.0, color="tab:orange",
             label="componente M4 sola")
    ax1.axhline(0, color="k", lw=0.5)

    # Marcar la doble pleamar central, la que se ve entera.
    theta = np.arccos(A2 / (4 * A4))  # existe solo si A4 > A2/4
    for signo in (-1, 1):
        t_pico = T_m2 + signo * theta / w
        ax1.plot(t_pico, A2 * np.cos(w * t_pico) - A4 * np.cos(2 * w * t_pico),
                 "v", color="tab:red", ms=10, zorder=5)
    ax1.annotate("dos pleamares separadas\npor un bache de "
                 f"{2 * theta / w * 60:.0f} min",
                 xy=(T_m2, A2 * np.cos(w * T_m2) - A4 * np.cos(2 * w * T_m2)),
                 xytext=(15.4, -0.55), fontsize=8, color="tab:red",
                 arrowprops=dict(arrowstyle="->", color="tab:red", lw=0.9))
    ax1.set(xlabel="tiempo (horas)", ylabel="altura (m)", xlim=(0, 24.84),
            ylim=(-2.3, 1.85),
            title="Doble pleamar: aparece cuando M4 > M2/4\n"
                  r"(aquí $A_4/A_2$ = " f"{A4 / A2:.2f}, umbral 0.25)")
    ax1.legend(fontsize=8, loc="lower right")

    ax2.plot(t, solo_m2, lw=1.6, ls="--", color="dimgray", label="solo M2")
    ax2.plot(t, asimetrica, lw=2.2, color="tab:green",
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
    _guardar(fig, "07-solent.png")


# ---------------------------------------------------------------- documento 08
def fig_virial():
    """El teorema virial: por qué subir de órbita frena, y que es un PROMEDIO.

    Los paneles central y derecho usan la órbita Tierra-Luna de la simulación de
    N-cuerpos del proyecto. El izquierdo es analítico.
    """
    mu = GM_EARTH + GM_MOON

    pos0, vel0, gm = three_body_state()
    dt = 300.0
    t, pos, vel = integrate(pos0, vel0, gm, dt, int(3.0 * YEAR / dt),
                            sample_every=2)
    r = pos[:, MOON] - pos[:, EARTH]
    v = vel[:, MOON] - vel[:, EARTH]
    d = np.linalg.norm(r, axis=-1)
    k = 0.5 * np.sum(v * v, axis=-1)
    u = -mu / d

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4.6))

    # --- Panel 1: K, U, E en función del radio orbital (analítico) ---
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

    # --- Panel 2: el cociente instantáneo NO vale 2 ---
    P = mean_motion_period(t, r)
    sel = t <= 3 * P
    ax2.plot(t[sel] / DAY, (-u / k)[sel], lw=1.3, color="tab:purple")
    ax2.axhline(2.0, color="k", lw=1.4, ls="--", label="lo que predice el virial")
    for etiqueta, idx, color, dx, dy in (
        ("perigeo: 1.86\n(más pequeño → $\\ddot I > 0$)",
         d[sel].argmin(), "tab:red", 4.0, -0.005),
        ("apogeo: 2.10\n(más grande → $\\ddot I < 0$)",
         d[sel].argmax(), "tab:blue", 3.5, 0.012),
    ):
        ax2.plot(t[idx] / DAY, (-u / k)[idx], "o", color=color, ms=8, zorder=5)
        ax2.annotate(etiqueta, xy=(t[idx] / DAY + dx, (-u / k)[idx] + dy),
                     fontsize=8, color=color, va="center")
    ax2.set(xlabel="tiempo (días)", ylabel="$-U/K$  instantáneo",
            ylim=(1.80, 2.20),
            title="Instante a instante NO se cumple\n(3 órbitas de la simulación)")
    ax2.legend(fontsize=8, loc="lower right")

    # --- Panel 3: el cociente DE LOS PROMEDIOS sí converge a 2 ---
    # Ojo: es -<U>/<K>, el cociente de los promedios, no el promedio del cociente.
    ratio_acumulado = -np.cumsum(u) / np.cumsum(k)
    orbitas = t / P
    desde = orbitas >= 0.35  # el transitorio inicial se sale de escala
    ax3.plot(orbitas[desde], ratio_acumulado[desde], lw=1.6, color="tab:green")
    ax3.axhline(2.0, color="k", lw=1.4, ls="--")
    ax3.annotate("2 exacto: dos cuerpos aislados", xy=(20, 1.9955), fontsize=8)
    ax3.annotate(f"converge a {ratio_acumulado[-1]:.4f}\n"
                 "el 0.3% que sobra es ⟨f·r⟩,\nla perturbación del Sol",
                 xy=(orbitas[-1], ratio_acumulado[-1]), xytext=(11, 2.022),
                 fontsize=8, color="tab:green",
                 arrowprops=dict(arrowstyle="->", color="tab:green", lw=0.9))
    ax3.set(xlabel="órbitas completas promediadas",
            ylabel="$-\\langle U\\rangle / \\langle K\\rangle$",
            ylim=(1.985, 2.032), xlim=(0, 41),
            title="Al promediar, sí\nEL VIRIAL ES UNA LEY DE PROMEDIOS")

    fig.suptitle("Documento 08 — el teorema virial", fontsize=10, y=1.0)
    _guardar(fig, "08-virial.png")


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    print("Generando figuras de la documentación:")
    fig_dos_bultos()
    fig_retroceso_lunar()
    fig_libracion()
    fig_ley_cubo()
    fig_sistema_solar()
    fig_equilibrio_vs_real()
    fig_solent()
    fig_virial()
