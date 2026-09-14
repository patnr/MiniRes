# Changelog

Notable changes to `minires`.
The format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning is semantic, but `0.x`, meaning that **minor bumps may break the API**.
Such changes are marked **BREAKING** below.

The package is not on PyPI; it is consumed straight from git, so downstream users
should pin a tag (or commit hash) and advance it deliberately.

## [Unreleased]

Renamed to **MiniRes**; wells rebuilt (records, paths, BHP control, grouping, a
Peaceman well index); an adjoint model; aquifers; inactive cells; Corey
relative permeabilities; practical units.

### Added

- **Well records**: `model.wells = [dict(name="P1", xy=[1, 1], rate=-1), ...]`
  (or `ResSim(wells=[...])`), which `Wells.from_records` assembles into the
  per-completion arrays -- these remaining the whole of the (writable) config.
- **BHP-controlled wells**, `wells.bhp` (shaped like `rates`; `nan` entries
  stay rate-controlled, so the modes mix across wells and in time), solved
  simultaneously with the pressure. A BHP well also anchors the incompressible
  pressure equation, lifting both its pin and its rate balance. No native mode
  switching, and no declared flow direction.
- **A well model**: `peaceman_WI`, assigned to `wells.WI`, makes `sim` record
  bottom-hole pressures in `wells.actual_bhp` -- grid-independent to 0.2%,
  unlike the cell pressure that `sim` used to advertise as "BHP-like".
- **Well paths**: `well_path` discretizes a polyline into one completion per
  cell traversed. Under BHP control the split between them is solved for;
  under rate control it is prescribed.
- **Well grouping**: `wells.group` maps completions to their well and
  `wells.names` names them -- hence `wells.nWell`, `wells.rates_by_well`, and
  plot markers labelled by name.
- `ResSim.well_controls(S, P, k)`: the feedback-control hook (replacing
  `dynamic_rate`, ref Changed), returning `dict(rates=..., bhp=...)`, so an
  override governs the wells' *modes* too -- approximating, lagged by a step,
  the mode switching (e.g. a rate target with a BHP limit) that the model does
  not do natively.
- **Aquifers**, `aquifer_WI` and the record key `aquifer`: a BHP-controlled
  "well" completed in the cells that touch it, its `WI` the transmissibility
  of their boundary faces -- i.e. a Dirichlet condition imposed *at* the face,
  needing no boundary-condition machinery elsewhere. A finite (Fetkovich)
  aquifer is a `well_controls` override.
- **Inactive cells**, `ResSim.active`: a bool `(Nx, Ny)` mask carving an
  irregular reservoir out of the rectangular grid, with no fudge factors: zero
  transmissibility across their faces, identity rows in the pressure system,
  infinite pore volume (so they never bind the CFL). Disconnected regions are
  not detected, but the singular system one otherwise makes is caught by a new
  residual assertion on the pressure solve. Plots mask them, and
  `plt_field(cellwise=True)` paints cells flat.
- **An adjoint model**, `minires.tlm`, derived by hand: `adjoint` sweeps a
  trajectory (which `linearize`/`adj_step` recompute and reverse step by step)
  for the gradient wrt `S0`, `P0`, `log K` and the BHP controls, at the cost of
  about one `sim`. Explicit scheme only; the other parameters and the discrete
  decisions held fixed. Verified against finite differences; derivation and
  caveats in the module docstring.
- **Corey relative permeabilities**: exponents (`nw`, `no`) and end-points
  (`krw0`, `kro0`), defaulting to the quadratic curves as before. The
  normalized saturation is now clipped to $[0, 1]$, so an odd power cannot make
  a phase below its residual mobile with the wrong sign. `estimate_1CFL`
  follows the curves.
- **`ResSim.cdarcy`**, Darcy's constant, whereby the model may be posed in
  *practical* (non-coherent) units -- metric being `0.008527`, ECLIPSE's
  `CDARCY`. Its docstring is the units story; the default `1` changes nothing.
- **Cached preconditioning of the pressure solve** (`ResSim.cached_precond`,
  on by default): conjugate gradients preconditioned by an earlier step's
  factorization. Exact to the solver tolerance, so no recorded value changes;
  2--6x faster where the saturation hardly moves, 15--40% in a waterflood.
- **The Egg model**, `examples/egg.py`: the channelized, 12-well benchmark of
  Jansen et al. (2014), flattened from 7 layers to one. The one *validation*
  against an external simulator -- it reproduces the deck's published ECLIPSE
  100 water cuts and oil rates to an RMS of 0.01 and about 5%.
- **`notebooks/`**: two browser demos -- `colab.ipynb`, and `interactive.py`, a
  [marimo](https://marimo.io) notebook whose sliders re-run the simulation,
  exported to WebAssembly at <https://patnr.github.io/MiniRes/wasm/>, where the
  Python runs in the reader's tab. Both install `minires` **from PyPI**, so
  they await the planned release.
- New examples: `well_control.py`, `well_path.py`, `aquifer.py`,
  `inactive_cells.py`, `water_cut_gradient.py`, `history_match_gradient.py`.

### Changed

- **BREAKING**: the project is **renamed to MiniRes**: the import is now
  `minires` (`from minires import ResSim`), the distribution `minires`, the
  repo <https://github.com/patnr/MiniRes> (CamelCase, a display name; GitHub
  resolves either case, so existing pins keep resolving) and the docs
  <https://patnr.github.io/MiniRes/minires.html> (whose path *is*
  case-sensitive). Class names are untouched, so downstream only the import
  line changes. The old name said the discretization -- which every simulator
  uses -- rather than what the package is, and lost the search to HEC-ResSim.
- **BREAKING**: injectors and producers are **unified into a single set of
  wells**, removing every per-kind code path: `inj_xy`/`prd_xy` -> `wells.xy`;
  `inj_rates`/`prd_rates` -> `wells.rates`, now **signed** (positive injects
  water, negative produces); `actual_rates` one signed `(nComp, nSteps)` array
  rather than a dict by kind, likewise the control hook's rates. The
  incompressible balance assertion is that the rates sum to 0, and a lone well
  no longer needs a zero-rate partner. Plot markers follow the sign
  (`well_scatter`'s `inj: bool` -> `sgn: int`, which silently reinterprets an
  old positional `False` as `0`). Regression values unaffected.
- **BREAKING**: the fluid properties are **grouped into `ResSim.fluid`** (a
  `minires.fluids.Fluid`): `model.vo` -> `model.fluid.vo`, `ResSim(vo=5,
  swc=.2)` -> `ResSim(fluid=dict(vo=5, swc=.2))` (a `dict`, a `Fluid` or
  `None`). The methods went with the parameters -- `RelPerm`, `dRelPerm`,
  `rescale_sat`, and `fractional_flow`/`dfractional_flow` (formerly one free
  function of `tlm` returning both) -- and are the one implementation of $f_w$,
  reused by the transport schemes, the CFL estimate and the examples' water
  cuts. Other curves are a `Fluid` subclass. Numerically unchanged.
- **BREAKING**: `wells.nWell` counts **wells**, not completions -- the latter
  being `wells.nComp` (forwarded by `ResSim.nComp`).
- **BREAKING**: `dynamic_rate` is removed in favour of `well_controls`, a
  superset of it; no shim. `rates = super().dynamic_rate(S, k)` becomes
  `ctrl = super().well_controls(S, P, k)`, with `rates` now `ctrl["rates"]`, a
  single signed array.
- **BREAKING**: `sim`'s `x0, p0` are renamed `S0, P0`; `assemble_wells(S, k)`
  gains the current pressure, `(S, P, k)`; and `TPFA` and `pressure_step`
  return the pressure *flat* (`Nxy`), like the saturation, their `p_prev`
  renamed `P` (callers indexing pressure in 2D must reshape).
- `_set_Q` is renamed `assemble_wells` and made public, with its partner
  `realize_bhp` (some callers set up a pressure solve without `sim`).
- **`minires.wells`** is a module of its own (the `Wells` dataclass and the
  free calculators `peaceman_WI`, `well_path`, `aquifer_WI`), leaving the core
  400 lines lighter.
- **`mpl-tools` is dropped** -- the package should not concern itself with
  front-ends. Its `freshfig` was `plt.subplots(num=..., clear=True)` plus
  screen placement, so that is what the examples now call. `NicePrint` is
  likewise replaced by `AlignedRepr`, since adopted by `struct-tools` (`>=0.3`)
  and imported from there; the two `DotDict`s become a `Fluxes` named tuple
  (still `V.x`/`V.y`) and a plain `dict`.
- **Fewer examples** (15 -> 12), the overlapping ones folded together:
  `rate_scheduling` into `quarter_five_spot` (as its scheduled-rates variant),
  `depletion` between `buildup` and `well_control`, and `heterogeneous`
  dropped, being the README banner's first two panels already. The examples
  also configure their wells by records now. Reference values carry over.

### Fixed

- **`Ny = 1` runs** used to raise `ValueError: offset array contains duplicate
  values`, the x- and y-neighbour diagonals coinciding at `±1`. `_spdiags` now
  sums coincident diagonals, so a row reproduces a column to round-off.
  Plotting a 1D field is still not possible.
- The $O(c_t)$ term of the **transport** equation, previously neglected, is now
  included (`ResSim.storage_rate`), so a single-phase reservoir stays
  single-phase instead of accumulating water at an injector until it ran away
  -- which had limited `ct`. Saturations for `ct > 0` change accordingly;
  `ct = 0` is bit-for-bit unaffected.
- Scalar `K` (e.g. `ResSim(..., K=3.)`) broadcasts as documented, instead of
  raising `ValueError: cannot reshape array of size 2` (broken since v0.1.1).
- The explicit scheme's sub-step count is kept off the round-off
  (`estimate_1CFL` shaves a relative `1e-9`): round-numbered set-ups put
  `dt * cfl1` exactly on an integer, where the linear solver's last bits
  decided the count, differently across platforms.
- Two tolerances that were *absolute* are now **relative**, the magnitudes
  being a matter of the units: the rate-balance check of `time_stepper` and the
  upper-border nudge of `Grid2D.xy2sub`.

## [0.2.0] -- 2026-08-27

Compressibility, and a general tooling refresh.

### Added

- **Slight compressibility**, opt-in via the new `ct` attribute (`9300beb`).
  With `ct > 0` the pressure equation becomes parabolic (backward Euler), so
  pressure propagates at finite speed, the absolute pressure level becomes
  meaningful (anchored by `p0`), and injection need no longer balance production
  -- enabling e.g. primary depletion. The corresponding `O(ct)` term in the
  *transport* equation was deliberately neglected in this release (documented,
  with the resulting limit on `ct`); ref Unreleased, above.
- `examples/`: runnable illustrations that double as the regression test suite
  (`c1873dc`). `heterogeneous.py` and `quarter_five_spot.py` are the former
  `tests/test_fig1.py` and `test_fig6.py`; `rate_scheduling.py`,
  `pressure_diffusion.py`, `depletion.py`, `buildup.py` and
  `voidage_replacement.py` are new.
- Type hints throughout, checkable with `ty` (a dev dependency; not wired into CI)
  (`dac8634`).

### Changed

- **BREAKING**: `sim()` now returns the `(S, P)` trajectories rather than just
  the saturation `S`, and accepts an optional initial pressure `p0` (`9300beb`).
  Callers must unpack: `S, P = model.sim(...)`.
- **BREAKING**: minimum Python raised to 3.12 (from 3.9); CI matrix is now
  3.12--3.14 (`d21e48a`).
- Packaging/dev environment migrated from poetry to uv (`d21e48a`).
- Linting switched from flakeheaven to ruff (`1760b00`).
- Minimum matplotlib raised to 3.8 (`60e1813`).

### Fixed

- Figures now display when running as a plain script or under IPython, and
  `anim()` works on matplotlib >= 3.10, where `ContourSet` is itself an artist
  (`60e1813`).

## [0.1.1] -- 2023-10-24

Mostly an API-ergonomics release: well configuration, plotting and the grid
became attributes/methods of the model rather than free functions and setup
calls.

### Added

- Time-dependent well rates: `inj_rates`/`prd_rates` are reshaped to
  `(nWell, nTime)`, with singletons broadcast over time (`988b47e`).
- `dynamic_rate(S, k)`: an override point for rates that depend on the current
  state (e.g. shutting wells on water breakthrough), plus the `actual_rates`
  record of what the wells really did (`e3d4026`).
- Simulations with no flow at all (no injectors/producers, or zero rates) now
  run, without warnings (`f0ff50e`, `ebc9235`).
- Convenience properties `nInj`, `nPrd` (`34323da`, `adc8953`), and a `name`
  attribute (`f3ce235`).
- Plotting: grid overlay in `plt_field()` (`14f45dc`), a `locator` style key
  (`c2254ee`), `finalize` in the plotters (`0525c45`), well-marker sizing via
  forwarded kwargs (`f2afbaa`), and a clearer bullseye argmax indicator
  (`0301231`).

### Changed

- **BREAKING**: `config_wells()` removed. Well specs are plain attributes
  (`inj_xy`, `inj_rates`, `prd_xy`, `prd_rates`) whose setters do the
  normalization -- snapping positions to the nearest grid node and reshaping
  rates (`18588dd`, `55d6f35`). `K` is likewise broadcast in its setter
  (`4643295`).
- **BREAKING**: `recurse()` renamed to `sim()` (`89b1c0e`).
- **BREAKING**: `prod`/`nProd` renamed to `prd`/`nPrd` throughout (`adc8953`).
- **BREAKING**: `ResSim` is now a dataclass, changing the constructor signature
  (`708f756`, `f665312`).
- **BREAKING**: plotting functions became methods of the inherited `Plot2D`
  mixin (`70c19e5`), plot coordinates are absolute rather than relative
  (`d8369d1`), and `plt_field()` changed its `colorbar`/`wells` defaults
  (`60594a6`).
- **BREAKING**: `M` renamed to `Nxy` (`095ec3f`), `.grid` renamed to `.domain`
  (`c13a8b7`), and `Q` made private (`34a57a6`).
- **BREAKING**: out-of-bounds coordinate conversions raise instead of being
  silently clamped (`1c3754c`); rates are asserted non-negative (`f405043`).
  Assertions generally gained messages (`6f8db6a`).
- Lists are accepted wherever arrays are (`6ca6a4c`).

## [0.1.0] -- 2023-03-29

Initial Python translation of the Matlab codes of Aarnes, Gimse & Lie (2007):
the TPFA pressure solver, both the explicit-upwind and implicit
(Newton--Raphson) saturation steppers, the grid utilities, the plotting
facilities, and the reproductions of the paper's Figs. 1 and 6 that verify
agreement with the Matlab output. See the deviations below.

## Deviations from the Matlab codes

Structural differences from the original, as opposed to changes over time.
The Python code still reproduces the Matlab output (up to linear-solver and
randomness differences), as verified by `examples/quarter_five_spot.py`.

- `83293bc`: Converted from 3D to 2D for simplicity.
- `a9fcc49`: Index ordering is C-major (numpy standard), not F-major.
- `7543f57`: Vectors are "numpy-thonic", in using 1d arrays, not (2d) columns.
- `cade315`: Several linear solvers suggested.
- `f33c571`: OOP -- so that ensembles of independent models can be forecast.
- `55ce732`: Facilities for working on the grid.
- `e0d12b0`, `988b47e`: Convenient well config, with rates that may vary in
  time. Total injection must equal total production only in the incompressible
  case; see `ct` below.
- `e3d4026`: A hook for state-dependent (feedback) well control:
  `dynamic_rate()`, since generalized to `well_controls()`.
- `d827ce8`, `70c19e5`: Plotting facilities (fields, streamlines, wells,
  animation) as a mixin.
- `9300beb`: Optional slight compressibility (`ct > 0`); the Matlab codes are
  strictly incompressible.
- `dac8634`: Type hints, checkable with `ty`.

[0.2.0]: https://github.com/patnr/MiniRes/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/patnr/MiniRes/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/patnr/MiniRes/releases/tag/v0.1.0
