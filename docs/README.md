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

### [07 — El Solent: el mejor caso de estudio del mundo](07-el-solent.md)

Navegación práctica y física a la vez. La **doble pleamar** de Southampton y el
álgebra de una línea que la explica: aparece en cuanto el armónico M4 supera un
cuarto de M2. Por qué la Isla de Wight, con sus dos entradas, la produce; por qué
eso convirtió Southampton en el puerto de los transatlánticos; las corrientes de
4-5 nudos de Hurst Narrows; y por qué **la regla de los doceavos falla ahí**.

### [08 — El teorema virial](08-el-teorema-virial.md)

Por qué `2⟨K⟩ = −⟨U⟩`, y por qué eso hace que **añadir energía a una órbita la
frene**. **No sale de la conservación de la energía** —sale de Newton II más que el
sistema esté acotado— y el documento lo demuestra con la identidad de
Lagrange-Jacobi, verificada a 10⁻⁶ con datos de nuestra simulación. Insiste en que
es una **ley de promedios**: en el perigeo sale 1.86 y en el apogeo 2.10, nunca 2.
Termina con cómo Zwicky convirtió velocidades en masa en 1933 y **descubrió así la
materia oscura**, con el cálculo de Coma hecho en una servilleta.

### [09 — ¿Cuán estable es el sistema Tierra-Luna-Sol?](09-estabilidad.md)

Robusto sí, milagroso no. **Chicxulub es un millonésimo** de lo necesario para
perturbar la órbita lunar: haría falta algo más grande que Ceres, o sea la misma
clase de evento que creó el sistema. Pero atención al salto lógico — la robustez
explica la **persistencia**, no la **formación**, y todo apunta a que esa fue un
accidente: **nuestra Luna es, en proporción, 52 veces más grande que la de cualquier
otro planeta**, y Venus no tiene ninguna. Termina con el giro: sin la Luna, la
oblicuidad terrestre vagaría caóticamente, así que **la Luna es lo que hace estable
el clima**. Con una integración de 1.500 años como prueba.

### [Bibliografía](bibliografia.md)

Ordenada por dificultad, marcando lo que está disponible gratis. Incluye las fuentes
de datos reales para la costa española (IHM, REDMAR) y un ejercicio final que resume
todo el proyecto: analizar un mareógrafo real con el código de este repositorio.

---

## Las figuras

Cada documento lleva una figura. Se regeneran todas con:

```
uv run python docs/make_figures.py
```

Las de los documentos 01, 03, 08 y 09 usan datos de la simulación de N-cuerpos del
proyecto. Las demás son construcciones analíticas o datos de la literatura, y está
indicado en el pie de cada una, para que nunca haya duda sobre qué es resultado
propio y qué es contexto.

El software está escrito en inglés, como el resto del proyecto; solo los rótulos de
las figuras van en español, porque son contenido de estos documentos.

## Cómo se relaciona esto con el código

| documento | programa |
|---|---|
| 01 — dos bultos | `03_tidal_bulge.py`, `tide/potential.py` |
| 04 — 1/d³ | `03_tidal_bulge.py` (razón Luna/Sol = 2.178) |
| 01 — 12 h 25 min y sicigias | `04_tides.py` |
| 06, 07 — análisis armónico | `05_constituents.py`, `tide/harmonics.py` |
| 08 — relación virial e identidad de Lagrange-Jacobi | `tide/nbody.py` — **sí sale**, verificada a 10⁻⁶ |
| 09 — estabilidad acotada del sistema | `tide/orbits.py` — **sí sale**, 1.500 años integrados |
| 02, 03 — retroceso y acoplamiento | **nada** — hacen falta disipación y cuerpos extensos |
| 07 — el armónico M4 | **nada** — lo genera el océano, no la gravedad |

Los documentos 02, 03 y parte del 07 explican física que este código
deliberadamente **no** modela: la simulación es conservativa, trata los cuerpos como
masas puntuales y no tiene océano dinámico. Está dicho explícitamente en cada uno,
para que no queden dudas sobre qué es resultado de la simulación y qué es contexto.

El 08 es el caso interesante: la **relación** virial sí está en la simulación, pero
la **evolución secular** que produce no, porque necesita disipación. Tenemos los
rieles, no el motor.
