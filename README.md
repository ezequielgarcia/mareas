# Tides from scratch

Simulate the Sun, Earth and Moon under Newtonian gravity, then work out what the
oceans do about it — and check the answer against a century of tidal science.

Five short programs, read in order. Nothing but NumPy.

```
uv sync
uv run python 01_two_body.py     # gravity + integrator, checked against Kepler
uv run python 02_three_body.py   # add the Moon                        (~15 s)
uv run python 03_tidal_bulge.py  # why there are two bulges, not one
uv run python 04_tides.py        # spin the Earth: a tide record
uv run python 05_constituents.py # periods and amplitudes              (~20 s)
uv run pytest                    # 22 physics checks                    (~8 s)
```

Figures land in `figures/`.

**Prose documentation, in Spanish, in [`docs/`](docs/README.md)** — nine
illustrated essays on the physics behind the code: why there are two bulges and not
one, whether the Moon really is receding, why we always see the same face, tides
elsewhere in the solar system, why the Bay of Fundy has 16 m when this project
computes 25 cm, the Solent's double high water, the virial theorem (and how it
found dark matter), how robust the Earth-Moon-Sun system is, and an annotated
bibliography.

Only the essays are in Spanish. All software — code, identifiers and comments — is
in English; the sole exception is the figure labels, which are content for those
essays. Regenerate every figure with `uv run python docs/make_figures.py`.

---

## Is this possible ab initio?

Partly, and it is worth being precise about which part.

**Yes — the forcing.** The tide-generating potential follows from Newtonian
gravity and the orbital geometry with nothing fitted. That gets you every tidal
*period* exactly, all the *relative* amplitudes, and absolute amplitudes of the
right size (tens of cm). This project does that, and reproduces the classical
constituent amplitudes to within 2%.

**No — the tide at your local beach.** Observed coastal tides range from ~0.1 m
in the Mediterranean to ~11 m in the Bay of Fundy. That spread has almost
nothing to do with gravity: it is the *resonant, friction-damped response of
ocean basins* to the forcing computed here. Getting it requires solving the
Laplace tidal equations on a rotating sphere with real bathymetry. The
equilibrium tide this project computes is the honest ceiling of a pure
gravity calculation, and real tides depart from it by more than an order of
magnitude in places.

So: this gives you the *clock* of the tides with high precision, and the
*amplitude* only to within the factor that ocean dynamics supplies.

---

## The progression

Each program adds exactly one idea and prints checks against known values.

### 01 — Two bodies

Newton's law of gravity plus a velocity-Verlet integrator. No tides yet. The
point is to earn trust in the integrator by reproducing all three of Kepler's
laws: the ellipse's `a` and `e`, constant angular momentum, and the period
`2π√(a³/GM)`.

Gets the sidereal year to 1.7×10⁻⁷.

### 02 — Three bodies

`accelerations()` already sums over all pairs, so adding the Moon is a one-line
change to the initial condition. What changes is the behaviour:

- Earth stops moving smoothly — it orbits the Earth–Moon barycentre, 4,679 km
  from its own centre (0.73 Earth radii, inside the Earth but well off centre).
- The **sidereal** month (27.32 d, against the stars) differs from the
  **synodic** month (29.53 d, against the Sun). That gap is the origin of
  spring and neap tides.
- The Earth–Moon distance swings 356,805–406,330 km. Tidal force goes as 1/d³,
  so that is a large modulation — the N2 constituent.

And two slow cycles emerge that were never put in, both caused by the Sun
tugging on the lunar orbit:

| | simulated | accepted |
|---|---|---|
| nodal regression | 18.60 yr | 18.61 yr, retrograde |
| apsidal advance | 8.85 yr | 8.85 yr, prograde |

These are not fitted. They fall out of three bodies and inverse-square gravity,
and the 18.6-year one turns out to govern how long a record you need in
program 05.

### 03 — Water: two bulges, not one

The conceptual heart. If the Moon simply pulled water toward itself there would
be **one** high tide a day. There are two.

The Earth is in free fall toward the Moon, so what raises tides is the
*difference* between the local pull and the pull on Earth's centre. Starting
from the Moon's potential at a station **r** with the Moon at **d**, subtract
the two pieces that raise no tide — the constant `−GM/|d|`, and the term linear
in **r** that is just the whole Earth's acceleration — and you are left with

```
V(r) = GM ( 1/|d−r| − 1/|d| − (r·d)/|d|³ )
```

which is exact. Expanding for r ≪ d gives the familiar quadrupole

```
V ≈ (GM r² / 2d³)(3cos²ψ − 1)
```

and `3cos²ψ − 1` is positive both *under* the Moon and *opposite* it. Two
bulges. Earth rotates through both each day, which is why the dominant tide is
semidiurnal.

The `d⁻³` is the other lesson: tidal forcing falls off as the **cube** of
distance. The Sun is 27 million times more massive than the Moon but 390 times
further away, so it loses. Simulated ratio at mean distances: **2.178** against
the accepted 2.18.

### 04 — Spin the Earth

Combine the two: integrate the bodies, rotate a station through the bulge
pattern, record the water height. The first output that looks like a tide gauge.

- High waters at the equator every **12.4210 h** against 12.4206 h expected
  (half a lunar day — Earth must turn slightly more than 360° to bring the Moon
  back overhead).
- The envelope swells and fades on a 14.8-day cycle: spring and neap, the
  Sun–Moon beat, exactly half the synodic month from program 02.
- Away from the equator successive high waters become unequal — the *diurnal
  inequality*, which exists only because the Moon and Sun are not in Earth's
  equatorial plane. It peaks near 45° latitude, as `sin 2φ` demands.

### 05 — Periods and amplitudes

Decompose the record into standard tidal constituents. The frequencies are not
fitted — they are known in advance from astronomy — so the fit is linear and one
least-squares solve recovers every amplitude and phase.

The real validation is the **ratio test**. Within a species, amplitude ratios
are fixed by the expansion of the tidal potential and are independent of
latitude, of the Love number, and of every other choice we made:

| ratio | simulated | classical | error |
|---|---|---|---|
| S2/M2 | 0.4677 | 0.4652 | +0.5% |
| N2/M2 | 0.1879 | 0.1915 | −1.9% |
| K2/M2 | 0.1271 | 0.1266 | +0.4% |
| O1/K1 | 0.7143 | 0.7108 | +0.5% |
| P1/K1 | 0.3300 | 0.3312 | −0.4% |
| Q1/K1 | 0.1346 | 0.1361 | −1.1% |

Absolute amplitude too: M2 at the equator comes out at 16.783 cm, which with the
Love factor divided back out is 24.22 cm against the classical rigid-Earth
equilibrium value of ~24.2 cm.

And the latitude structure is essentially exact — M2 follows `cos²φ` and K1
follows `|sin 2φ|` to four digits, because they are degree-2 sectoral and
tesseral harmonics respectively.

---

## The physics we had to add to get this accurate

The first version of this code produced a lunar month 0.8% wrong and constituent
ratios off by 32%. Everything below turned out to be necessary. Several were
mistakes worth making.

### 1. A symplectic integrator

Velocity Verlet, not Runge–Kutta. A symplectic method's energy error oscillates
within a bound instead of accumulating, so a 20-year integration does not slowly
spiral. Measured energy drift over 20 years: **8.7×10⁻¹³**.

### 2. Tides are differential, not gravitational

See program 03. Subtracting the monopole and the uniform-acceleration term is
not a simplification — it *is* the physics. Skip it and you get one bulge a day
and an amplitude wrong by a factor of ~60.

### 3. Earth's obliquity, and the Moon's orbital inclination

Without the 23.44° obliquity there are **no diurnal tides at all** — K1, O1, P1
and Q1 vanish identically. They exist only because the tide-raising bodies move
above and below the equatorial plane. The Moon's 5.145° inclination to the
ecliptic matters for the same reason, and it is also what drives the nodal
cycle.

### 4. The solid Earth deforms too

A tide gauge measures sea surface relative to the crust — but the crust is
rising and falling as well, and Earth's own tidal bulge adds to the potential.
Both fold into the diminishing factor

```
γ₂ = 1 + k₂ − h₂ = 1 + 0.302 − 0.609 ≈ 0.693
```

so the observable equilibrium tide is ~31% smaller than the rigid-Earth one.
Set `LOVE_FACTOR = 1.0` in `tide/constants.py` to see the rigid case.

### 5. Osculating elements ≠ mean elements

**The biggest trap.** The numbers you look up — "the Moon's semi-major axis is
384,399 km, eccentricity 0.0549" — are *mean* elements, averages over an orbit
the Sun is constantly deforming. Feed 384,399 km into a two-body initial
condition and the orbit oscillates about a *different* mean: we measured the
osculating axis swinging over 379,516–387,706 km (~1.1%, exactly the size of the
solar perturbation parameter `2·(GM☉/d☉³)·r☾³/GM⊕`).

The result was a mean axis 0.8% low and a lunar month 0.8% fast. That is fatal:
a 0.8% error in lunar mean motion shifts M2 by 0.24°/hr, and M2 and S2 are only
1.016°/hr apart. Harmonic analysis becomes meaningless.

The fix is what ephemeris fitting does — choose *osculating* elements at our
epoch so the *mean* behaviour matches the tables. `calibrate.py` iterates to
`a = 386,303 km`, `e = 0.0762`, giving a sidereal month of 27.321693 d against
27.321661 observed. The epoch eccentricity is far above the mean because we start
at perigee *and* at syzygy, where the Sun stretches the orbit hardest; the real
Moon's osculating eccentricity ranges over roughly 0.026–0.077, so this sits at
the top of the physical range rather than outside it. Details in
`tide/orbits.py`.

### 6. The record must span a full nodal cycle — 18.61 years

**The second big trap, and the one that fixed the ratios.** The lunar node
regresses over 18.61 years, swinging the Moon's peak declination between 18.3°
and 28.6°. Tabulated constituent amplitudes are *mean-node* values, so a short
record catches the node at whatever phase it happens to be in:

| record length | worst ratio error |
|---|---|
| 2 years | **32.1%** (K2/M2) |
| 8.85 years (one apsidal cycle) | 3.2% |
| **18.61 years (one nodal cycle)** | **1.9%** |
| 20 years | 2.8% |

Note that 20 years is *worse* than 18.61 — a partial extra nodal cycle
reintroduces bias. K2 and K1 move most, because they are the constituents whose
amplitude depends on the node. This is the same reason the official US standard
for tidal datums is a 19-year "National Tidal Datum Epoch"; that number is not
bureaucratic, it is 18.61 rounded up.

### 7. The Rayleigh criterion

Two constituents are only separable once the record is long enough for them to
drift a full cycle apart: `T = 1/|f₁ − f₂|`. S2 and K2 differ by 0.0821 °/hr,
needing **183 days**; K1 and P1 the same. Fit them with a shorter record and
least-squares will cheerfully split the energy between them however the noise
suggests. `harmonics.unresolved_pairs()` checks this before doing any work.

### 8. A bug worth mentioning: the lunar day

Building the spring/neap envelope with a 24.00-hour window beats against the
true 24.84-hour tidal day and manufactures a spurious ~29-day cycle. The first
version reported spring tides every 9.17 days. Use a **lunar**-day window
(`LUNAR_DAY` in `04_tides.py`), and measure the envelope at the equator where
the tide is purely semidiurnal — at 45° the diurnal component pollutes it.

---

## What this deliberately does not do

- **No ocean dynamics.** Equilibrium tide only. No Laplace tidal equations, no
  bathymetry, no resonance, no bottom friction, no amphidromic points, no
  overtides (M4, M6) — those are generated by shallow-water nonlinearity, not by
  gravity, so they are absent by construction.
- **Absolute phases are meaningless.** The epoch is synthetic — Earth at
  perihelion, Moon at perigee and at syzygy, all at t=0. That is not a real
  calendar date, so the phase column in program 05 has no relation to any actual
  tide table. Periods and amplitudes are the deliverable. Real ephemeris initial
  conditions (JPL DE440) would fix this.
- **Three bodies only.** Venus and Jupiter raise tides ~10⁻⁵ of the Moon's.
- **Spherical, ocean-covered Earth.** No continents, no polar flattening.
- **Sa is wrong, and honestly so.** The real annual constituent is dominated by
  meteorology — seasonal heating, wind, air pressure — not gravity. Our
  gravitational Sa of 0.6 mm is correct for gravity and irrelevant to a real
  gauge.

## Where to go next

The natural stage 6 is the dynamic ocean: solve the Laplace tidal equations
(shallow-water on a rotating sphere) forced by the potential from `03`, and watch
amphidromic systems and basin resonance appear. *That* is the step where a GPU
earns its keep — a global grid over many timesteps, with differentiable friction
and bathymetry for inversion. JAX would be the right tool there. It is the wrong
tool for the present project: three bodies for 20 years is a sub-minute
single-core job, and it needs float64 throughout, which JAX does not use by
default and which consumer GPUs run at 1/32 rate.

## Reading

Genuinely accessible, roughly in order of how much they assume:

- **Steacy Hicks, *Understanding Tides*** (NOAA CO-OPS, 2006). ~66 pages, free
  PDF, written for beginners, and it covers constituents and the 19-year datum
  epoch gently. The best first thing to read.
- **Open University, *Waves, Tides and Shallow-Water Processes***. The standard
  accessible undergraduate oceanography text.
- **David Pugh, *Changing Sea Levels* (2004)** and **Pugh & Woodworth,
  *Sea-Level Science* (2014)**. Pugh is the accessible authority on harmonic
  analysis; the constituent tables and the Rayleigh criterion discussion in
  *Sea-Level Science* map directly onto program 05.
- **Eugene Butikov, "A dynamical picture of the oceanic tides"**, *Am. J. Phys.*
  **70**, 1001 (2002). If the two-bulge explanation in program 03 still feels
  slippery, this paper is the clearest treatment of why the naive picture fails.
- **David Cartwright, *Tides: A Scientific History* (1999)**. How Newton,
  Laplace, Kelvin and Doodson each got a piece of it. Excellent context.
- **Doodson & Warburg, *Admiralty Manual of Tides* (1941)**. Old, and still the
  clearest exposition of the harmonic method and the Doodson numbers.
- **Duncan Agnew, "Earth Tides"** (*Treatise on Geophysics*, ch. 3.06) for the
  Love-number/solid-Earth side of §4 above.
- For stage 6: **Hendershott's** lecture notes on the Laplace tidal equations,
  and **Munk & Cartwright, "Tidal spectroscopy and prediction"** (1966) for the
  response method — both a real step up in difficulty.

## Layout

```
01_two_body.py  …  05_constituents.py   the progression — start here
calibrate.py                            solves for the epoch elements of §5
docs/                                   illustrated essays, in Spanish
docs/make_figures.py                 regenerates every docs figure
tide/constants.py                       SI constants and orbital elements
tide/initial_conditions.py              building the two- and three-body states
tide/nbody.py                           gravity + velocity-Verlet integrator
tide/orbits.py                          osculating elements, precession, calibration
tide/potential.py                       tide-generating potential, equilibrium tide
tide/harmonics.py                       constituent speeds and least-squares fit
tests/test_tide.py                      22 checks against known physics
```
