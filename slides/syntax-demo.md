---
title: Plantilla de láminas
subtitle: para comprobar la sintaxis
author: Ezequiel Garcia
date: 2026
footer: Plantilla · make_slides.py
theme: light
---

# Plantilla de láminas

## Esta lámina es la portada: sólo títulos, y es la primera

---

<!-- layout: section -->

# Lámina de sección

## Sólo títulos, pero no es la primera

---

# Lámina con viñetas

## Un subtítulo opcional, en color de acento

- Una viñeta de primer nivel
- Otra, con **negrita**, *cursiva* y `código`
  - Una viñeta de segundo nivel
  - Y otra
- Fórmulas en línea: $3\cos^2\psi - 1$

---

# Lámina con párrafo y cita

Un párrafo normal se ajusta solo al ancho de la lámina y se parte en las líneas
que haga falta.

> Una cita destacada, con una barra de color a la izquierda.

---

# Lámina con figura

![Una figura, con el texto del corchete como pie](../figures/03_tidal_bulge.png)

---

<!-- layout: full -->

![Dos figuras lado a lado](../figures/01_two_body.png)
![La segunda, con su propio pie](../figures/05_constituents.png)

---

# Lámina con código

```
uv run python slides/make_slides.py slides/deck.md
```

1. Las listas numeradas también funcionan
2. Y se numeran como tú las escribas
