# De la teoría al puerto: por qué la marea real no se parece

Este proyecto calcula una marea de equilibrio de **25 a 65 cm**. Los números
reales:

| lugar | carrera de marea (vivas) |
|---|---|
| Bahía de Fundy (Canadá) | **~16 m** (máximo registrado) |
| Bristol Channel (Reino Unido) | ~13 m |
| Golfo de San Malo (Francia) | ~12 m |
| Cantábrico (Bilbao, Santander) | ~4.5 m |
| Vigo, Rías Baixas | ~3.5 m |
| Cádiz | ~3.2 m |
| Canarias | ~2.5 m |
| Mediterráneo (Barcelona, Valencia) | **~0.2 m** |
| Báltico | prácticamente nada |

Un factor de casi **100** entre el Mediterráneo y Fundy. Y nuestra marea de
equilibrio no acierta ni uno solo de esos números.

Esto no es un fallo del cálculo. Es el resultado más importante que hay que
entender: **la gravedad pone el reloj de la marea, pero la amplitud la pone el
océano.**

---

## El error de Newton (y la corrección de Laplace)

Newton, en los *Principia*, dio la teoría del equilibrio: el mar adopta en cada
instante la superficie equipotencial. Es lo que calcula
`tide/potential.py:equilibrium_height()`, y es lo que produce nuestros 25 cm.

El problema lo señaló **Laplace**: esa teoría exige que el bulto de marea *siga* a
la Luna. Veamos si puede.

En el ecuador, el bulto tendría que recorrer 40,000 km en un día lunar de 24 h 50
min, o sea unos **450 m/s**. Pero una perturbación en agua poco profunda viaja a la
velocidad de onda larga:

```
c = √(g h) = √(9.81 × 4000) ≈ 200 m/s
```

con h la profundidad media del océano, unos 4 km. **200 m/s frente a los 450 que
haría falta.** El océano no puede seguir el ritmo: no llega ni a la mitad.

Consecuencia: la marea real no es una marea de equilibrio en absoluto. Es una **onda
forzada** que corre por detrás del forzamiento, con la fase equivocada, rebotando en
los continentes e interfiriendo consigo misma. Laplace escribió las ecuaciones
correctas —las **ecuaciones de marea de Laplace**, aguas someras sobre una esfera en
rotación— y son las que se siguen resolviendo hoy.

---

## Qué hace realmente la marea: puntos anfidrómicos

Si dibujas en un mapa las líneas de igual hora de pleamar (*líneas cotidales*), no
obtienes una onda que barre el planeta de este a oeste. Obtienes **remolinos**.

La rotación de la Tierra desvía las corrientes (Coriolis) y la onda de marea queda
atrapada contra las costas como **onda de Kelvin**, girando alrededor de cada cuenca
—en sentido antihorario en el hemisferio norte. En el centro de cada uno de esos
giros hay un **punto anfidrómico**: un lugar donde la amplitud de ese constituyente
es **cero** y todas las horas de pleamar se cruzan a la vez.

Hay una docena de ellos repartidos por el mundo. En un punto anfidrómico de M2 no
hay marea semidiurna lunar en absoluto. Y a 200 km de allí puede haber varios
metros. Nada de esto se puede intuir desde la gravedad: es geometría de cuencas.

---

## Resonancia: de dónde salen los 16 m de Fundy

Fundy no tiene una marea grande porque la Luna esté más cerca de Canadá. La tiene
porque la bahía es **un instrumento afinado a la nota de la Luna**.

Una bahía abierta por la boca y cerrada al fondo es un resonador de cuarto de onda,
y su período propio viene dado por la **fórmula de Merian**:

```
T = 4L / √(g h)
```

Con L ≈ 270 km y h ≈ 60 m para la bahía:

```
T = 4 × 270,000 / √(9.81 × 60) = 1.08 × 10⁶ / 24.3 ≈ 44,500 s ≈ 12.4 h
```

Y el período de M2 es **12.42 h**. (El período propio del sistema completo Golfo de
Maine + Fundy se estima en unas 13 h, algo más largo que esta cuenta simplificada,
pero la conclusión es la misma.) La bahía está prácticamente en resonancia con el
forzamiento lunar, y como cualquier oscilador cerca de resonancia, amplifica
enormemente. De ~1 m en la entrada a ~16 m en el fondo.

Es exactamente el mismo fenómeno que empujar un columpio al ritmo justo, o que un
cantante rompa una copa. La única razón de que Fundy sea famosa es que
`4L/√(gh)` le salió parecido a 12.42 h.

El **Mediterráneo** es el caso opuesto: casi cerrado, comunicado con el Atlántico
solo por Gibraltar, demasiado pequeño para que el forzamiento directo haga gran cosa
y con períodos propios que no coinciden con M2. Resultado: 20 cm. Con una excepción
instructiva —el **golfo de Gabès**, en Túnez, sí tiene la geometría adecuada y llega
a ~2 m, diez veces más que el resto del Mediterráneo.

---

## Aguas someras: constituyentes que la gravedad no genera

En aguas poco profundas las ecuaciones dejan de ser lineales: la velocidad de la
onda depende de la propia altura de la marea (√(g(h+η))), así que la cresta viaja
más rápido que el seno y la onda se deforma. Eso genera **armónicos** de los
constituyentes originales:

- **M4**, con período de 6.21 h, exactamente la mitad de M2
- **M6**, 4.14 h
- **MS4**, combinación de M2 y S2

Estos constituyentes **no existen en el forzamiento gravitatorio**. Por eso no
aparecen en `tide/harmonics.py` y no podrían aparecer: son creados por la dinámica
del propio océano. En estuarios someros pueden ser grandes, y son la razón de que
en algunos sitios la subida y la bajada duren tiempos muy distintos, o de que se
formen **macareos** (*tidal bores*), esa ola que remonta el río —el Severn en
Inglaterra, el Qiantang en China.

---

## Entonces, ¿cómo se predice la marea de verdad?

Con el mismo motor de este proyecto, pero alimentado con datos reales.

La receta que usan todos los almanaques del mundo desde Doodson es:

1. **Medir.** Instalar un mareógrafo y registrar el nivel durante al menos un año,
   idealmente 19 (ver la sección sobre el ciclo nodal en el
   [README](../README.md)).
2. **Analizar.** Ajustar por mínimos cuadrados las amplitudes y fases de cada
   constituyente a esas frecuencias astronómicas conocidas. Eso es literalmente
   `tide/harmonics.py:fit()`.
3. **Publicar** las **constantes armónicas** de ese puerto: una amplitud y una fase
   por constituyente. Típicamente 30–100 constituyentes para un puerto principal.
4. **Predecir.** Sumar los constituyentes hacia el futuro. Eso es
   `05_constituents.py:reconstruct()`.

El paso 2 y el paso 4 son los que ya tenemos. Lo que este proyecto no puede darte es
el paso 1: **las constantes armónicas de tu puerto son un dato empírico**, no algo
derivable de la gravedad. Codifican toda la respuesta del océano —resonancia,
fricción, geometría— en un par de números por constituyente.

Y funciona asombrosamente bien: la predicción astronómica de marea suele acertar
dentro de 10–20 cm. Lo que queda fuera es la **marea meteorológica** (*storm
surge*): presión atmosférica y viento pueden añadir o quitar más de un metro, y eso
es impredecible con más de unos días de antelación. Cuando una borrasca profunda
coincide con una marea viva perigea, es cuando hay inundación.

### Datos reales para la costa española

- **Instituto Hidrográfico de la Marina** (Cádiz) publica el *Anuario de Mareas*,
  la referencia oficial para navegación, con puertos patrón y puertos secundarios.
- **Puertos del Estado** (puertos.es) mantiene la red **REDMAR** de mareógrafos, con
  predicción y datos históricos descargables. Es la fuente para ver mareas reales y
  compararlas con lo que da este proyecto.

Un ejercicio bonito: descarga un año de un mareógrafo de REDMAR, pásalo por
`tide/harmonics.py:fit()`, y compara las constantes armónicas que obtengas con las
publicadas. El código de este repositorio ya sirve para eso sin cambios.

---

## Un aviso para navegantes: la corriente no va con la altura

Detalle práctico que sorprende: **el máximo de corriente de marea no coincide en
general con la pleamar**. Depende del tipo de onda:

- En una **onda progresiva** (mar abierto, canal largo), la corriente máxima ocurre
  *en* la pleamar y la bajamar.
- En una **onda estacionaria** (bahía resonante, cuenca cerrada), la corriente
  máxima ocurre a **media marea**, con 90° de desfase, y en pleamar la corriente es
  cero (*slack water*).

La mayoría de sitios reales están en algún punto intermedio, y por eso los atlas de
corrientes y los rombos de marea de las cartas se refieren siempre a **la hora de
pleamar de un puerto patrón**: la relación entre altura y corriente es local y hay
que tabularla, no se puede deducir.

Para planificar un paso —una barra, un estrecho, un puente— lo que importa es la
corriente, y para eso el dato es el atlas, no la tabla de alturas.

---

## Y esta es la etapa donde sí sirve una GPU

Resolver las ecuaciones de Laplace sobre una malla global, con batimetría real y
fricción de fondo, muchos pasos de tiempo, y opcionalmente diferenciable para
invertir parámetros a partir de observaciones: ese sí es un problema de GPU. Es la
etapa 6 natural de este proyecto y donde JAX sería la herramienta correcta.

Para tres cuerpos durante 20 años, en cambio, NumPy en un núcleo tarda menos de un
minuto. Cada herramienta a su escala.

---

## Para leer más

Ver [bibliografia.md](bibliografia.md). Para este capítulo en particular, **Pugh &
Woodworth, *Sea-Level Science*** es exactamente el libro: cubre análisis armónico,
respuesta oceánica, puertos secundarios y marea meteorológica con el nivel adecuado
para alguien que ya entiende el forzamiento.
