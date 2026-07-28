# ¿De verdad la Luna se está alejando?

Sí: **3.8 cm al año**, medido directamente. Y la culpa es de las mareas.

Este es probablemente el resultado más bonito de toda la teoría de mareas, porque
conecta tres cosas que parecen no tener nada que ver: por qué los días se alargan,
por qué la Luna se aleja, y por qué se disipa energía en el mar de Bering.

---

## Cómo lo sabemos

No es una inferencia teórica. Es una medida.

Las misiones Apollo 11, 14 y 15 y los rovers soviéticos Lunokhod dejaron
**retrorreflectores** en la superficie lunar: espejos de esquina que devuelven la
luz exactamente por donde vino. Desde 1969 se dispara un láser desde la Tierra,
se cronometra el viaje de ida y vuelta (unos 2.5 segundos) y se obtiene la
distancia Tierra-Luna con precisión de milímetros.

Medio siglo de esas medidas da la respuesta sin ambigüedad: la Luna se aleja
**3.8 cm/año**, unos 3.8 metros por siglo.

Hay confirmación independiente de otras tres fuentes:

- **Eclipses antiguos.** Registros babilónicos, chinos y árabes de eclipses
  ocurridos hace 2000–2500 años. Si extrapolas la rotación terrestre actual hacia
  atrás, predices que el eclipse se vio en un sitio distinto del que dice la
  tablilla. La discrepancia acumulada (que los astrónomos llaman ΔT) mide cuánto
  se ha frenado la Tierra.
- **Ritmitas de marea.** Sedimentos laminados que registran ciclos de sicigias y
  cuadraturas, capa a capa, como los anillos de un árbol. Los depósitos de
  Elatina (Australia), de hace ~620 millones de años, indican un día de unas
  **21.9 horas** y un año de unos **400 días**.
- **Corales fósiles** del Devónico, con bandas de crecimiento diarias y anuales,
  que dan una cuenta parecida.

Cuatro métodos completamente distintos, misma conclusión.

---

## El mecanismo: el bulto va por delante

Aquí está el truco, y es puramente geométrico.

Si la Tierra fuese un fluido sin rozamiento, el bulto de marea apuntaría
exactamente hacia la Luna. Pero el océano tiene fricción, tarda en responder, y
la Tierra gira mucho más rápido (24 h) que la Luna en su órbita (27.3 d). El
resultado es que **la rotación arrastra el bulto por delante de la línea
Tierra-Luna**, unos pocos grados.

```
        bulto adelantado
              ↓
         ___
       /     \
      |   T   | ----→ giro de la Tierra
       \ ___ /
                            ● Luna
```

Ese pequeño desfase lo cambia todo, porque ahora hay un par de fuerzas:

- **El bulto tira de la Luna hacia adelante.** La Luna gana momento angular.
- **La Luna tira del bulto hacia atrás.** La Tierra pierde momento angular: se
  frena.

El momento angular no se pierde, se *transfiere*: de la rotación de la Tierra a
la órbita de la Luna. Lo que sí se pierde es energía, disipada en calor por la
fricción.

### El detalle que a todo el mundo le descoloca

El bulto acelera a la Luna, la empuja hacia adelante en su órbita... y el
resultado es que **la Luna se mueve más despacio**.

No es contradicción. Al ganar energía la Luna sube a una órbita más alta, y por
la tercera ley de Kepler una órbita más alta es una órbita más lenta. Acelerarla
tangencialmente la promociona a un carril exterior donde tarda más en dar la
vuelta. Es exactamente lo mismo que le pasa a una nave que enciende motores para
subir de órbita.

---

## Los números

El reparto de momento angular en el sistema Tierra-Luna:

| | momento angular | fracción |
|---|---|---|
| rotación de la Tierra | 5.9 × 10³³ kg m²/s | 17% |
| órbita de la Luna | 2.9 × 10³⁴ kg m²/s | 83% |

La órbita lunar ya guarda **cinco veces** más momento angular que el giro de la
Tierra. El depósito grande es la órbita; la Tierra es la que va perdiendo.

La potencia disipada por las mareas es de unos **3.7 TW** (teravatios). Para
comparar, el consumo energético de toda la humanidad ronda los 20 TW. Y no se
disipa uniformemente: cerca de la mitad se va en unos pocos mares someros donde
la fricción con el fondo es brutal —el mar de Bering, la plataforma patagónica,
el mar de Irlanda, la bahía de Hudson— y buena parte del resto en generar
**mareas internas** en el océano profundo, ondas en la estratificación de
densidad. Esa disipación en el interior del océano resulta ser importante para la
circulación global: es una de las fuentes de mezcla que mantiene la circulación
termohalina.

### Cuánto se alarga el día

La fricción de marea alarga el día unos **2.3 ms por siglo**. Pero lo que se
*observa* son unos 1.8 ms por siglo. La diferencia no es un error: la Tierra se
está volviendo más esférica desde la última glaciación, porque el manto sigue
recuperándose del peso de los hielos (rebote postglacial). Al concentrar masa
hacia el eje, disminuye su momento de inercia y **acelera** la rotación, como una
patinadora que recoge los brazos. Los dos efectos compiten, y gana la marea, pero
por menos.

---

## El problema del pasado

Aquí viene lo interesante, y es un sitio donde una extrapolación ingenua se
estrella de frente.

Si la Luna se aleja 3.8 cm/año y está a 384,400 km, extrapolando linealmente
hacia atrás estaría *pegada a la Tierra* hace unos 1,500 millones de años. Pero
la Luna tiene 4,500 millones de años. Algo no cuadra.

La resolución es que **la tasa actual no es representativa**. La disipación de
marea depende muchísimo de la forma de las cuencas oceánicas, y resulta que hoy
el océano está inusualmente cerca de resonancia con M2 (ver
[06-de-la-teoria-al-puerto.md](06-de-la-teoria-al-puerto.md)). Estamos en un
momento de disipación anómalamente alta. Con la deriva continental, las cuencas
han cambiado de forma muchas veces y la tasa de retroceso ha subido y bajado.

Esto se conoce como el *problema de la órbita lunar precámbrica* y sigue siendo
un tema activo: reconciliar la tasa actual con la edad de la Luna requiere
modelar la historia de las cuencas oceánicas, que es difícil. Es un buen ejemplo
de que un dato medido con precisión de milímetros puede seguir siendo difícil de
interpretar.

---

## El futuro

Si nada lo interrumpiera, el proceso terminaría en **acoplamiento mutuo**: la
Tierra se frenaría hasta que el día durase lo mismo que el mes, ambos unos 47
días actuales, con la Luna a unos 550,000 km. Siempre la misma cara de la Tierra
mirando a la Luna, igual que hoy la Luna nos mira a nosotros (ver
[03-por-que-vemos-siempre-la-misma-cara.md](03-por-que-vemos-siempre-la-misma-cara.md)).

Solo que eso tardaría unos **50,000 millones de años**, y el Sol se convertirá en
gigante roja en unos 5,000 millones. No va a pasar. La Tierra y la Luna morirán
sin llegar a sincronizarse.

---

## Lo que este proyecto NO hace

Importante, para no llevarse una idea equivocada: la simulación de este
repositorio **no reproduce nada de esto**.

El retroceso lunar requiere **disipación**: fricción, un bulto que se retrasa, un
par de fuerzas. Nuestro modelo es gravedad newtoniana pura entre tres masas
puntuales, sin rozamiento y sin océano dinámico. Es conservativo: la energía se
conserva a 8.7 × 10⁻¹³ en 20 años, que es precisamente la razón de que los
períodos salgan bien. Y también la razón de que la Luna no se aleje ni un
milímetro.

Para obtener el retroceso harían falta dos cosas que no tenemos: un océano con
fricción, y el par de fuerzas del bulto desfasado actuando de vuelta sobre la
órbita. Es una extensión posible, pero es un proyecto distinto.

---

## Para leer más

Ver [bibliografia.md](bibliografia.md). Para este tema en concreto:

- **Cartwright, *Tides: A Scientific History*** — el capítulo sobre la
  aceleración secular de la Luna, que es una historia de detectives de casi tres
  siglos (empieza con Halley notando la discrepancia en eclipses antiguos).
- **Munk & Wunsch (1998), "Abyssal recipes II"** — el trabajo que estableció el
  reparto de los 3.7 TW y su papel en la circulación oceánica. Denso pero
  fundamental.
- **Williams (2000), "Geological constraints on the Precambrian history of
  Earth's rotation and the Moon's orbit"** — las ritmitas y el problema del
  pasado.
