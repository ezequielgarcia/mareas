# Bibliografía

Ordenada por lo que asume de ti, no por importancia. Marco con **(gratis)** lo que
está disponible legalmente sin pagar.

---

## Para empezar

**Steacy Hicks, *Understanding Tides*.** NOAA / CO-OPS, 2006. **(gratis, PDF)**
Unas 66 páginas escritas explícitamente para quien empieza. Cubre los dos bultos,
los constituyentes, los datums y el epoch de 19 años sin exigir cálculo. Si solo
vas a leer una cosa, lee esta. Búscalo en el sitio de NOAA Tides & Currents.

**Open University, *Waves, Tides and Shallow-Water Processes*.** 2ª ed.,
Butterworth-Heinemann. El manual estándar de oceanografía física accesible. Está
pensado para autoestudio, con ejercicios resueltos. El capítulo de mareas es
probablemente la mejor introducción de nivel universitario que existe en formato
libro.

**David Cartwright, *Tides: A Scientific History*.** Cambridge University Press,
1999. La historia del problema, desde las especulaciones antiguas hasta Doodson.
Se lee como narrativa y de paso te explica la física, porque cuenta cómo cada uno
—Newton, Bernoulli, Laplace, Kelvin, Darwin, Doodson— resolvió una pieza. Ideal si
te gusta entender *por qué* las cosas se hacen como se hacen.

---

## Análisis armónico y práctica

**David Pugh, *Tides, Surges and Mean Sea-Level*.** Wiley, 1987. **(gratis, PDF)**
El autor lo liberó y se puede descargar del National Oceanography Centre. Es la
referencia clásica y sigue siendo excelente. Aquí está el análisis armónico
explicado de verdad, con los constituyentes, el criterio de Rayleigh y los puertos
secundarios.

**Pugh & Woodworth, *Sea-Level Science*.** Cambridge University Press, 2014. La
puesta al día del anterior, ampliada a tsunamis, marea meteorológica y cambio del
nivel medio. Si te interesa el capítulo
[06-de-la-teoria-al-puerto.md](06-de-la-teoria-al-puerto.md), este es *el* libro
que lo desarrolla.

**Paul Schureman, *Manual of Harmonic Analysis and Prediction of Tides*.** US
Coast and Geodetic Survey, Special Publication 98, 1940 (reimpreso 1958).
**(gratis, PDF)** Un manual operativo, de la época en que esto se hacía a mano con
máquinas mecánicas. Es de donde vienen, por linaje directo, las velocidades de los
constituyentes que están en `tide/harmonics.py`. Seco pero definitivo: si alguna
vez dudas del valor exacto de la velocidad de un constituyente, se mira aquí.

**Doodson & Warburg, *Admiralty Manual of Tides*.** HMSO, 1941. Viejo y aún sin
sustituto para explicar el método armónico y los números de Doodson con claridad.

---

## La física, en profundidad

**Eugene Butikov, "A dynamical picture of the oceanic tides".** *American Journal
of Physics* **70**(9), 1001 (2002). El mejor tratamiento de por qué las
explicaciones habituales de los dos bultos fallan, y de cómo se hace bien. Es el
artículo que respalda
[01-por-que-hay-dos-mareas-al-dia.md](01-por-que-hay-dos-mareas-al-dia.md). Si
alguna vez tienes que *enseñar* mareas, léelo antes.

**A. T. Doodson, "The harmonic development of the tide-generating potential".*
*Proceedings of the Royal Society A* **100**, 305 (1921). El artículo fundacional:
aquí se inventa el esquema de seis argumentos astronómicos que aún se usa. Vale la
pena hojearlo aunque solo sea para ver el origen de los nombres M2, S2, K1.

**Cartwright & Tayler, "New computations of the tide-generating potential".**
*Geophysical Journal of the RAS* **23**, 45 (1971). El desarrollo armónico moderno
y preciso del potencial. Es la referencia contra la que se comparan las razones de
amplitud que valida `05_constituents.py`.

**Duncan Agnew, "Earth Tides".** En *Treatise on Geophysics*, cap. 3.06. La parte
de Tierra sólida: números de Love, marea del cuerpo terrestre, y por qué aparece el
factor γ₂ = 0.693 de `tide/constants.py`.

**Munk & Cartwright, "Tidal spectroscopy and prediction".** *Philosophical
Transactions of the Royal Society A* **259**, 533 (1966). El *método de respuesta*,
la alternativa al análisis armónico clásico: en vez de ajustar líneas discretas,
trata el océano como un sistema lineal con una función de transferencia. Un salto
de dificultad real, pero conceptualmente elegante.

**Munk & Wunsch, "Abyssal recipes II: energetics of tidal and wind mixing".**
*Deep-Sea Research I* **45**, 1977 (1998). De donde salen los ~3.7 TW de disipación
mareal de [02-la-luna-se-aleja.md](02-la-luna-se-aleja.md), y el argumento de que
la marea es una de las fuentes de mezcla que mantiene la circulación oceánica
global.

---

## Mareas en el sistema solar

**Murray & Dermott, *Solar System Dynamics*.** Cambridge University Press, 1999.
*El* libro de dinámica de sistemas planetarios. Capítulo 4 para evolución de marea
y resonancias espín-órbita, capítulo 8 para resonancias de movimiento medio (la de
Laplace de Ío-Europa-Ganímedes). Nivel de posgrado, pero se puede leer por
capítulos sueltos.

**Peale, Cassen & Reynolds, "Melting of Io by tidal dissipation".** *Science*
**203**, 892 (1979). Predijeron el vulcanismo de Ío por calentamiento de marea, y
se publicó **días antes** de que la Voyager 1 sobrevolara y lo confirmara. Uno de
los mejores ejemplos que existen de predicción teórica confirmada de inmediato.

**S. J. Peale, "Rotational histories of the natural satellites"** y trabajos
relacionados, sobre por qué Mercurio quedó en resonancia 3:2 y no 1:1.

**Williams, "Geological constraints on the Precambrian history of Earth's rotation
and the Moon's orbit".** *Reviews of Geophysics* **38**, 37 (2000). Las ritmitas de
marea, la duración del día en el pasado, y el problema de la órbita lunar
precámbrica de [02-la-luna-se-aleja.md](02-la-luna-se-aleja.md).

---

## Si quieres extender el código

**Jean Meeus, *Astronomical Algorithms*.** 2ª ed., Willmann-Bell. Si quieres
arreglar la limitación de la "época sintética" del proyecto y anclar la simulación
a una fecha real de calendario, aquí están los algoritmos, explicados para
implementarlos. Es el libro de referencia de la astronomía computacional práctica.

**JPL Horizons** y **SPICE/NAIF** (NASA JPL). **(gratis)** Efemérides reales
(DE440) con precisión de metros. Sustituir nuestras condiciones iniciales
aproximadas por un estado real de Horizons haría que las *fases* de los
constituyentes fuesen significativas, no solo los períodos y las amplitudes.

**Notas de clase de Myrl Hendershott** sobre las ecuaciones de marea de Laplace
(circulan de los cursos de verano del GFD de Woods Hole). El punto de partida
habitual para quien va a programar un modelo de marea dinámica, o sea la etapa 6
de [06-de-la-teoria-al-puerto.md](06-de-la-teoria-al-puerto.md).

---

## Datos reales, para la costa española

**Instituto Hidrográfico de la Marina** (Cádiz). Publica el **Anuario de Mareas**,
la referencia oficial para navegación en aguas españolas: puertos patrón, puertos
secundarios y correcciones. Es el documento que se usa a bordo.

**Puertos del Estado** — `puertos.es`. **(gratis)** Mantiene la red **REDMAR** de
mareógrafos, con predicciones y series históricas descargables. Es la fuente para
comparar este proyecto con la realidad.

**NOAA Tides & Currents** — `tidesandcurrents.noaa.gov`. **(gratis)** Para la costa
de EEUU, pero además publica las **constantes armónicas** de cada estación de forma
abierta y bien documentada. Muy útil si quieres alimentar
`tide/harmonics.py:fit()` con constantes reales y ver la diferencia con nuestra
marea de equilibrio.

**Sonel** y el **Permanent Service for Mean Sea Level (PSMSL)**. **(gratis)** Series
largas de mareógrafos de todo el mundo, para análisis de nivel medio y tendencias.

---

## Un ejercicio recomendado

Cuando hayas leído lo básico: descarga un año de datos de un mareógrafo de REDMAR
cerca de donde navegas, pásalo tal cual por `tide/harmonics.py:fit()`, y compara.

Vas a encontrar tres cosas, y las tres son instructivas:

1. Los **períodos** coinciden exactamente con los nuestros — la astronomía es la
   astronomía.
2. Las **amplitudes** no se parecen en nada, porque ahí está la respuesta del
   océano.
3. Aparece **varianza que ningún constituyente astronómico explica**: es la marea
   meteorológica, y es la razón de que la predicción de marea nunca sea perfecta.

Ese ejercicio es, en el fondo, el resumen de todo el proyecto.
