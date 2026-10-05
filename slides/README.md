# Láminas

`make_slides.py` convierte un Markdown en un PDF de presentación, una lámina por
cada bloque separado por `---`. La página mide 13,333 × 7,5 pulgadas: exactamente
**1920 × 1080** a 144 ppp, así que llena un proyector de 1080p sin bandas negras.
El texto queda vectorial; sólo las imágenes van en mapa de bits.

```
uv run python slides/make_slides.py slides/deck.md            # -> slides/deck.pdf
uv run python slides/make_slides.py slides/deck.md --png      # + un PNG por lámina
uv run python slides/make_slides.py slides/deck.md --theme dark
```

`slides/syntax-demo.md` es una plantilla que usa toda la sintaxis; compílala para
ver cómo queda cada cosa.

## Cabecera del fichero (opcional)

```markdown
---
title: Título de la charla
author: Nombre
date: 2026
footer: Texto del pie, en todas las láminas
theme: light      # o dark
---
```

## Sintaxis de cada lámina

| Escribes | Sale |
| --- | --- |
| `---` en una línea | separador de lámina |
| `# Título` | título de la lámina, con la regla de color debajo |
| `## Subtítulo` | línea en color de acento bajo el título |
| `### Apartado` | encabezado pequeño dentro del cuerpo |
| texto normal | párrafo, ajustado al ancho |
| `- punto` | viñeta; dos espacios de sangría para el segundo nivel |
| `1. punto` | lista numerada, con tus propios números |
| `> texto` | cita destacada con barra de color |
| ` ```…``` ` | bloque de código monoespaciado sobre fondo gris |
| `![pie](../figures/04_tides.png)` | figura centrada; el corchete es el pie (déjalo vacío si no quieres pie) |
| `**negrita**` `*cursiva*` `` `código` `` | lo que indican |
| `$3\cos^2\psi - 1$` | fórmula (sintaxis LaTeX) |

Dos o más `![...]()` seguidos, sin línea en blanco entre ellos, se colocan lado a
lado en la misma fila.

## Distribución

Se deduce de lo que contiene la lámina, y se puede forzar con un comentario:

- **portada**: la primera lámina si sólo tiene `#` y `##`.
- **sección**: cualquier otra lámina que sólo tenga `#` y `##`.
- **contenido**: el caso normal, título arriba y el cuerpo debajo.
- **completa**: una lámina que sólo tenga figuras: ocupan toda la lámina.

```markdown
<!-- layout: section -->
<!-- notes: esto no se imprime; es para ti -->
```

Si el contenido no cabe, el tipo se reduce por pasos hasta que entre, y el
programa avisa por `stderr` si ni al mínimo cabe. Eso es señal de partir la
lámina en dos.
