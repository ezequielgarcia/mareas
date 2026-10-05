# CLAUDE.md

Ab initio tides: Sun–Earth–Moon Newtonian gravity in NumPy → tide-generating
potential → equilibrium tide → harmonic analysis, validated against classical
tidal constituents. Educational project; the author (Ezequiel Garcia) also uses it
for a talk (`slides/`) and a set of Spanish essays (`docs/`).

`README.md` is the long-form explanation of the physics and of every trap
encountered. Read it before changing numbers or physics; this file only covers
how to work in the repo.

## Setup and commands

Python ≥ 3.11, managed with `uv` (`uv.lock` is committed on purpose, so the numbers
in the README stay reproducible). Not an installable package (`package = false`);
modules are imported from the repo root.

```
uv sync
uv run python 01_two_body.py        # Kepler check of the integrator
uv run python 02_three_body.py      # add the Moon (~15 s)
uv run python 03_tidal_bulge.py     # why two bulges
uv run python 04_tides.py           # tide record at a station
uv run python 05_constituents.py    # harmonic fit (~20 s)
uv run pytest                       # 22 physics checks, ~8 s, all passing at last review
uv run python calibrate.py          # re-solve lunar epoch elements (setup step)
uv run python docs/make_figures.py  # regenerate docs/img/*.png
uv run python slides/make_slide_figures.py                 # slide figures -> slides/img/
SOURCE_DATE_EPOCH=0 uv run python slides/make_slides.py slides/charla.md   # -> slides/charla.pdf
./slopcheck.py [--list] [FILE...]   # prose linter (see below)
```

Numbered programs write figures to `figures/` (git-ignored). Each prints checks
against known values; they are the documentation of the progression.

## Layout

- `01`…`05_*.py` — the progression. Each adds exactly one idea. Keep it that way.
- `tide/` — shared physics: `constants.py` (SI, GM not masses), `nbody.py` (gravity +
  velocity-Verlet), `initial_conditions.py`, `orbits.py` (osculating vs mean elements,
  calibration), `potential.py` (tide-generating potential, equilibrium height),
  `harmonics.py` (constituent speeds, least-squares fit, Rayleigh check).
- `tests/test_tide.py` — physics checks (Kepler, energy drift, ratios, latitude
  structure…), not just unit tests.
- `docs/` — nine Spanish essays + `bibliografia.md`; `docs/README.md` maps each essay
  to the code that backs it (and says which ones the code deliberately does *not* model).
- `slides/` — `make_slides.py` (Markdown → 16:9 PDF with matplotlib, 1920×1080 at 144 dpi,
  syntax documented in `slides/README.md`), `make_slide_figures.py`, `charla.md` (the
  talk, 18 slides), `syntax-demo.md`.
- `slopcheck.py` — scores prose (Markdown + Python docstrings/comments, EN and ES) for
  AI-slop tells; currently 0 hits on every rule. Run it after writing prose; a past
  commit existed solely to remove hits it flagged.

## Conventions

- **Language split:** all code, identifiers and comments are English. Prose in `docs/` and
  `slides/` is Spanish, and so are figure/plot labels (they are content). `README.md`
  is English. Commit messages are mostly Spanish, prefixed by area
  (`slides:`, `docs:`, `slopcheck:`), with a body explaining the why.
- Everything SI, float64 throughout (no JAX/GPU on purpose; see README "Where to go next").
- Dependencies: NumPy + matplotlib only (pytest in the dev group). Don't add more
  without a strong reason; "nothing but NumPy" is part of the pitch.
- Comments explain *why* (physics rationale, traps), not what. Match that density.
- `slides/charla.pdf` is committed deliberately so the deck can be projected without
  installing anything; other PDFs and per-slide PNGs are git-ignored. The PDF embeds a
  creation date, so regenerating changes bytes unless `SOURCE_DATE_EPOCH=0` is set.
  Only regenerate/commit it when the slides actually change.

## Physics gotchas (do not "simplify" these away)

- Tides are the *differential* potential: subtract the monopole and the term linear in
  **r** (Legendre n=0 and n=1). Not a simplification, it is the physics.
- Sign convention: `tide/potential.py` defines V with η = V/g, i.e. minus the usual
  potential; force is +∇V. The slides' appendix declares this.
- Lunar initial conditions use **osculating** elements from `calibrate.py`
  (`A_MOON_EPOCH`, `E_MOON_EPOCH`), not the tabulated mean ones (a 0.8% error in the
  month ruins M2/S2 separation). Re-run `calibrate.py` if integrator or setup changes.
- Constituent fits need a record of one full nodal cycle (**18.61 yr**, not 20) to match
  mean-node tabulated ratios; `harmonics.unresolved_pairs()` enforces the Rayleigh
  criterion. Use a lunar-day (24.84 h) window for the spring/neap envelope.
- `LOVE_FACTOR` (γ₂ ≈ 0.693) in `constants.py`; 1.0 gives the rigid-Earth tide.
- Epoch is synthetic (perihelion, perigee, syzygy at t=0): absolute phases are meaningless.
  Only periods and amplitudes are deliverables.
- Out of scope by design: ocean dynamics, bathymetry, overtides (M4…), Sa, bodies beyond
  Sun/Earth/Moon. Docs 02, 03, 07 explain physics the code does not model, and say so.

## Known small issues

- `pyproject.toml` comment mentions a `run.py` that does not exist.
- `figures/`, `.venv/`, `.pytest_cache/` are git-ignored; a fresh clone needs `uv sync`
  and a run of the numbered programs to get `figures/`. `slides/img/` and `docs/img/`
  are committed.

## Working from another machine

Nothing outside the repo is needed besides `uv`. Clone, `uv sync`, `uv run pytest`.
`bridge` plugin hooks seen in some sessions are unrelated to this project.
