# MiniRes

<img src="https://raw.githubusercontent.com/patnr/MiniRes/main/logo.png" alt="The MiniRes logo" align="right" width="300"/>

A lean petroleum reservoir simulator
using TPFA (two-point flux approximation).
[**Documentation**](https://patnr.github.io/MiniRes/minires.html).

- **Small**: all of its physics fit in `core.py`'s 400 lines of code.
- **Capable**: two-phase, slight compressibility, BHP control, well paths, irregular outlines and faults (inactive cells), aquifers –
  **but** a toy: 2D uniform grid, immiscible, isothermal, and simple well models and operation.
- **Adjoint** model included; verified against finite differences.
- **Python**: [![PyPI](https://img.shields.io/pypi/v/minires?logo=pypi&logoColor=white)](https://pypi.org/project/minires/) (`pip install minires`), or demo it in a web browser via
  [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/patnr/MiniRes/blob/main/notebooks/colab.ipynb) (backend: Google)
  or [![marimo](https://marimo.io/shield.svg)](https://patnr.github.io/MiniRes/wasm/) (no backend!).
- **Fast**: similar to [JutulDarcy's](https://github.com/sintefmath/JutulDarcy.jl) (but no JIT startup/wait) at equal accuracy on 2D two-phase cases of size $100$ – $10^5$.
- **Reliable**: reproduces the numbers of the [Matlab code (2007)](http://folk.ntnu.no/andreas/papers/ResSimMatlab.pdf) from NTNU/Sintef by Jørg E. Aarnes, Tore Gimse, and Knut–Andreas Lie.
  Further validated against Buckley–Leverett's
  analytic solution, ECLIPSE's numbers on the Egg model
  and JutulDarcy's on quarter five-spot, SPE-10, and Egg.
- **Tested** extensively: [![GitHub CI](https://github.com/patnr/MiniRes/actions/workflows/tests.yml/badge.svg)](https://github.com/patnr/MiniRes/actions),
  with many [examples](https://patnr.github.io/MiniRes/examples.html) doubling as regression tests.

![The Egg model: permeability, pressure, oil saturation, and the adjoint sensitivity of a producer's water cut](https://raw.githubusercontent.com/patnr/MiniRes/main/collage.png)

## Used by

Please let me know (or make a PR) if you use this in your work,
and I will add it to this list.

- [History matching tutorial](https://github.com/patnr/HistoryMatching)

## Contributions

To also get the examples and tests, clone instead, and install with [uv](https://docs.astral.sh/uv/), in editable mode:

```sh
git clone https://github.com/patnr/MiniRes.git
cd MiniRes
uv sync  # or: pip install -e .
uv run pytest
uv run ruff check
```

### AI

AI (in particular Claude Code) has already played a major role in developing
the recent features here, so AI-generated contributions are welcome.
But there is a strong focus on minimising *slop*, meaning that the changes should be
as small as the job allows, and written in the style of what surrounds them.
`CLAUDE.md` carries conventions and a good deal of what has already been tried and rejected.
