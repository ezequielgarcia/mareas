# Documentación: la física de las mareas

Explicaciones en prosa, para leer sin ordenador delante. El código y los
resultados numéricos están en el [README principal](../README.md); esto es el
"por qué".

Cada documento es independiente, pero el orden tiene sentido.

---

### [01 — ¿Por qué hay dos mareas al día y no una?](01-por-que-hay-dos-mareas-al-dia.md)

El corazón del asunto, y donde casi toda la divulgación se equivoca. La marea no
es la atracción de la Luna, es la *diferencia* de atracción. Incluye el argumento
definitivo contra la explicación centrífuga: **habría dos bultos incluso si la Luna
no orbitase**. Y de dónde salen las 12 h 25 min.

### [02 — ¿De verdad la Luna se está alejando?](02-la-luna-se-aleja.md)

Sí, 3.8 cm al año, medido con láser desde 1969. Cómo el bulto de marea adelantado
transfiere momento angular, por qué acelerar la Luna la hace ir más despacio, los
3.7 TW que se disipan, por qué el día se alarga menos de lo que debería, y el
problema de que una extrapolación ingenua pone la Luna pegada a la Tierra hace solo
1,500 millones de años.

### [03 — ¿Por qué vemos siempre la misma cara de la Luna?](03-por-que-vemos-siempre-la-misma-cara.md)

Porque **sí** rota, exactamente una vez por órbita. El mecanismo que la frenó, el
bulto fósil congelado en su corteza que la mantiene sujeta hoy, por qué las dos
caras de la Luna no se parecen en nada, y por qué en realidad vemos el 59% y no el
50%. Con Mercurio y su resonancia 3:2 como contraste.

### [04 — ¿Por qué la Luna gana al Sol?](04-por-que-la-luna-gana-al-sol.md)

El Sol tiene 27 millones de veces más masa y pierde, porque la marea va como
**1/d³** y no como 1/d². Incluye la tabla que zanja las "alineaciones planetarias":
Júpiter levanta una marea de 1.5 micras, Venus le gana a Júpiter, y una persona
sentada a un metro de ti tiene 54,000 veces más capacidad mareal que la Luna.

### [05 — Mareas en el resto del universo](05-mareas-en-el-sistema-solar.md)

La misma física llevada al extremo: Ío y sus 400 volcanes, los océanos subterráneos
de Europa y Encélado (y por qué eso reescribe dónde buscar vida), el límite de Roche
y los anillos de Saturno, el cometa Shoemaker-Levy 9, y por qué es más seguro caer
en un agujero negro grande que en uno pequeño.

### [06 — De la teoría al puerto](06-de-la-teoria-al-puerto.md)

Por qué este proyecto da 25 cm y la bahía de Fundy tiene 16 m. El error de Newton y
la corrección de Laplace: el océano **no puede** seguir a la Luna, le faltan 250
m/s. Puntos anfidrómicos, resonancia de cuencas con la fórmula de Merian, los
constituyentes de aguas someras que la gravedad no genera, cómo se predice la marea
de verdad, y por qué la corriente máxima no coincide con la pleamar.

### [Bibliografía](bibliografia.md)

Ordenada por dificultad, marcando lo que está disponible gratis. Incluye las fuentes
de datos reales para la costa española (IHM, REDMAR) y un ejercicio final que resume
todo el proyecto: analizar un mareógrafo real con el código de este repositorio.

---

## Cómo se relaciona esto con el código

| documento | programa |
|---|---|
| 01 — dos bultos | `03_tidal_bulge.py`, `tide/potential.py` |
| 04 — 1/d³ | `03_tidal_bulge.py` (razón Luna/Sol = 2.178) |
| 01 — 12 h 25 min y sicigias | `04_tides.py` |
| 06 — análisis armónico | `05_constituents.py`, `tide/harmonics.py` |
| 02, 03 — retroceso y acoplamiento | **nada** — hacen falta disipación y cuerpos extensos |

Los documentos 02 y 03 explican física que este código deliberadamente **no**
modela: la simulación es conservativa y trata los cuerpos como masas puntuales. Eso
está dicho explícitamente en cada uno, para que no queden dudas sobre qué es
resultado de la simulación y qué es contexto.
