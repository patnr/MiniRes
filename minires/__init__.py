""".. include:: README.md"""

from importlib.metadata import version as _version

from minires.core import ResSim
from minires.grid import Fluxes, Grid2D
from minires.fluids import Fluid
from minires.wells import Wells, aquifer_WI, peaceman_WI, well_path

# Also pdoc's table of contents: `ResSim` is documented on the package page (beside the
# README), and the listed submodules on their own pages. `core` is deliberately absent,
# lest `ResSim` be documented twice; so are the other re-exports, which are documented
# in their home modules.
__all__ = ["ResSim", "grid", "fluids", "wells", "plotting", "tlm", "geostat"]

__version__ = _version("minires")  # single source: `version` in pyproject.toml
