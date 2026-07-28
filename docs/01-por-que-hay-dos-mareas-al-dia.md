# ¿Por qué hay dos mareas al día y no una?

Si la marea fuese simplemente "la Luna tira del agua hacia sí", habría **una**
pleamar al día: la del momento en que la Luna pasa por encima. Hay dos, separadas
unas 12 h 25 min. Y hay una pleamar en el lado de la Tierra *opuesto* a la Luna,
donde su atracción es más débil.

Esto no es un detalle técnico. Es el corazón del asunto, y el sitio donde casi
todas las explicaciones divulgativas se equivocan.

---

## La clave: la Tierra está en caída libre

La Luna no tira del agua "más que de la Tierra". Tira de todo: del agua, de la
roca, de ti, del planeta entero. Y todo cae hacia la Luna a la vez.

Lo que produce marea no es la atracción, sino **la diferencia** entre la atracción
en un punto concreto y la atracción media sobre la Tierra completa. Estamos en un
sistema de referencia en caída libre, y en caída libre la gravedad uniforme es
invisible: los astronautas de la ISS flotan aunque la gravedad terrestre allí sea
casi tan intensa como aquí abajo. Solo se nota lo que *varía* de un punto a otro.

Y varía en tres direcciones distintas:

- **En el lado cercano a la Luna**, la atracción es más fuerte que la media. El
  residuo apunta hacia la Luna: el agua se abomba hacia ella.
- **En el lado lejano**, la atracción es más débil que la media. El residuo apunta
  *alejándose* de la Luna: el agua se queda atrás, y se abomba hacia fuera.
- **En los flancos**, la atracción apunta hacia el centro de la Luna, es decir un
  poco "hacia dentro" respecto a la vertical local. El residuo comprime.

Resultado: se estira en el eje Tierra-Luna y se comprime en el perpendicular. Un
elipsoide. **Dos bultos.**

```
            comprime
               ↓↓
         ↗   _____   ↖
   estira ← |     | → estira        ● Luna
         ↘   ‾‾‾‾‾   ↙
               ↑↑
            comprime
```

La Tierra gira dentro de ese patrón y una estación cruza los dos bultos cada
vuelta. De ahí las dos pleamares diarias, y de ahí que el constituyente dominante
sea **semidiurno**.

---

## El argumento definitivo contra la explicación centrífuga

Es muy común leer que el bulto lejano se debe a la "fuerza centrífuga" de la
rotación de la Tierra alrededor del baricentro Tierra-Luna. Esa explicación se
puede hacer funcionar con cuidado, pero casi siempre se usa mal, y hay una manera
de ver que no es lo esencial:

**Imagina que la Luna no orbitase.** Suéltala en reposo, de modo que la Tierra y
la Luna simplemente cayeran una hacia la otra en línea recta. No hay rotación, no
hay baricentro orbitado, no hay fuerza centrífuga de ningún tipo.

Seguiría habiendo **dos bultos**.

Porque el efecto es el gradiente del campo gravitatorio, y eso existe con órbita o
sin ella. La rotación alrededor del baricentro no es la causa; es una
circunstancia adicional. Si tu explicación de las mareas necesita la órbita, tu
explicación es incorrecta.

---

## Las matemáticas, que son cortas

El potencial de la Luna en una estación situada en **r** (medido desde el centro
de la Tierra), con la Luna en **d**, es −GM/|**d**−**r**|. Le restamos las dos
piezas que no producen marea:

- **−GM/|d|** es constante sobre toda la Tierra: un potencial constante no ejerce
  ninguna fuerza.
- El **término lineal en r** es la aceleración uniforme de la Tierra entera hacia
  la Luna. Al estar en el sistema geocéntrico en caída libre, se cancela.

Lo que queda es el **potencial generador de mareas**:

```
V(r) = GM ( 1/|d−r| − 1/|d| − (r·d)/|d|³ )
```

Esto es exacto, sin aproximaciones. Es lo que implementa
`tide/potential.py:tide_generating_potential()`, y el proyecto lo usa así, sin
truncar.

Si lo desarrollas para r ≪ d (la Tierra es 60 veces más pequeña que la distancia
a la Luna), el término dominante es:

```
V ≈ (GM r² / 2d³) (3cos²ψ − 1)
```

donde ψ es el ángulo entre la estación y la Luna. Y ahí está la clave algebraica:

| ψ | 3cos²ψ − 1 | |
|---|---|---|
| 0° (bajo la Luna) | **+2** | pleamar |
| 90° (flancos) | −1 | bajamar |
| 180° (antípoda) | **+2** | pleamar |

La función es **par en cos ψ**, así que no distingue el lado cercano del lejano.
Dos bultos, matemáticamente inevitables.

El programa `03_tidal_bulge.py` dibuja exactamente esta forma y compara la versión
exacta con la aproximada: difieren un 1.8%, del orden de r/d ≈ 1/56, como debe
ser.

---

## Entonces, ¿por qué 12 h 25 min y no 12 h 00?

Porque mientras la Tierra gira, la Luna avanza.

La Tierra completa una rotación respecto a las estrellas en 23 h 56 min (el día
sidéreo). Pero en ese tiempo la Luna se ha movido unos 13° a lo largo de su
órbita, así que la Tierra tiene que girar un poco más para volver a poner la Luna
en el mismo meridiano. Ese "poco más" son unos 50 minutos: el **día lunar** dura
24 h 50 min.

Dos bultos por día lunar → pleamares cada **12 h 25 min**.

La simulación mide 12.4210 h en el ecuador, frente a las 12.4206 h teóricas
(`04_tides.py`). Y por eso la marea "se retrasa" unos 50 minutos cada día, algo
que cualquiera que haya amarrado un barco dos días seguidos ha notado.

---

## ¿Y por qué la marea sube más algunos días?

Porque el Sol hace lo mismo que la Luna, con algo menos de la mitad de intensidad
(ver [04-por-que-la-luna-gana-al-sol.md](04-por-que-la-luna-gana-al-sol.md)).

- Cuando el Sol y la Luna están alineados —luna nueva y luna llena— sus dos
  elipsoides se suman: **mareas vivas** (sicigias, *spring tides*, y "spring" aquí
  no tiene nada que ver con la primavera, viene de *brotar*).
- En cuarto creciente y menguante están a 90° y se contrarrestan parcialmente:
  **mareas muertas** (cuadraturas, *neap tides*).

Como esto depende de la posición relativa Luna-Sol, el ciclo tiene el período de
media lunación: **14.77 días**, la mitad del mes sinódico de 29.53 d. El programa
`04_tides.py` lo mide en el ecuador y encuentra máximos cada ~15 días, con la
amplitud variando en un factor de 5.6 entre vivas y muertas.

Y encima las mareas vivas no son todas iguales, porque el ciclo de perigeo de
27.55 días las modula: una marea viva que coincide con el perigeo lunar es una
**marea viva perigea**, la más grande del ciclo, y es la que sale en las noticias
cuando inunda un paseo marítimo.

---

## Para leer más

- **Butikov (2002), "A dynamical picture of the oceanic tides"**, *American
  Journal of Physics* **70**, 1001. Si después de esto la explicación de los dos
  bultos te sigue pareciendo resbaladiza, este artículo es el mejor tratamiento
  del tema, y precisamente sobre por qué las versiones habituales fallan.
- El resto, en [bibliografia.md](bibliografia.md).
