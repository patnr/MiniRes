"""Gaussian random fields (`minires.geostat`), in 1D and 2D, and the effect of the range.

A permeability field to simulate on, or a prior to history match with, has to
come from somewhere. `minires.geostat.gaussian_fields` samples a stationary,
isotropic Gaussian field over the cell centres, from a Gaussian variogram
(`minires.geostat.variogram_gauss`) whose range, `r`, sets the length scale of
the heterogeneity. This is what the heterogeneous examples use for their
$ \\log K $ (e.g. `examples.water_cut_gradient`), and what the tutorials of
[HistoryMatching](https://github.com/patnr/HistoryMatching) use for their
prior ensembles.

In the figure:

- Top left: a few realizations in 1D. Top right: their *empirical* variogram
  (half the mean squared difference between points a distance $ h $ apart,
  over many realizations) against the model's -- they agree, which is also
  asserted below: the sampler produces the covariance it claims to.
- Bottom: realizations in 2D, one row per range. A short range gives
  fine-grained heterogeneity, a long one smooth, large-scale trends -- with
  the same marginal distribution (standard normal) in every cell.
"""

import matplotlib.pyplot as plt
import numpy as np

from minires import ResSim
from minires.geostat import gaussian_fields, variogram_gauss
from minires.plotting import show

rng = np.random.default_rng(1)  # Reproducibility (the values are regression tested)

## 1D: realizations, and the empirical variogram
xx = np.linspace(0, 1, 201)
r = .2
fields_1d = gaussian_fields((xx,), N=2000, r=r, rng=rng)
lags = np.arange(1, 60)
h = lags * (xx[1] - xx[0])
gamma_emp = np.array([np.mean((fields_1d[:, lag:] - fields_1d[:, :-lag])**2) / 2 for lag in lags])
gamma_mod = variogram_gauss(h, r)
assert np.allclose(gamma_emp, gamma_mod, atol=.05)

## 2D: realizations for a few ranges
model = ResSim(Lx=1, Ly=1, Nx=32, Ny=32)
ranges = [.05, .2, .8]
nShow = 4
fields_2d = {r: gaussian_fields(model.mesh, N=nShow, r=r, rng=rng) for r in ranges}

## Plot
fig, axs = plt.subplots(num="Random fields", clear=True, nrows=1 + len(ranges), ncols=nShow,
                        figsize=(10, 2.6 * (1 + len(ranges))))
gs = axs[0, 0].get_gridspec()
for ax in axs[0]:
    ax.remove()
ax = fig.add_subplot(gs[0, :2])
ax.plot(xx, fields_1d[:5].T, lw=1)
ax.set(title=f"1D realizations, r = {r}", xlabel="x", ylabel="field")
ax = fig.add_subplot(gs[0, 2:])
ax.plot(h, gamma_emp, "o", ms=4, label=f"Empirical ({len(fields_1d)} realizations)")
ax.plot(h, gamma_mod, "k-", label="Gaussian variogram")
ax.axvline(r, c="k", ls=":", lw=1, label="r")
ax.set(title="Variogram", xlabel="Distance h", ylabel="γ(h)")
ax.legend(loc="lower right", fontsize="small")
kws: dict = dict(cmap="viridis", levels=np.linspace(-3, 3, 19), cticks=np.arange(-3, 4),
                 wells=False, labels=False, finalize=False)
for i, r in enumerate(ranges):
    for j, ax in enumerate(axs[1 + i]):
        h_ = model.plt_field(ax, fields_2d[r][j], colorbar=False,
                             title=f"r = {r}" if j == 0 else None, **kws)
fig.tight_layout()
fig.colorbar(h_, ax=axs[1:].ravel().tolist(), ticks=kws["cticks"], shrink=.6, pad=.02)

# Regression values, checked by `tests/test_examples.py`.
__digest__ = dict(gamma_emp = gamma_emp,
                  **{f"field_{i}": fields_2d[r][0] for i, r in enumerate(ranges)})  # per range

if __name__ == "__main__":
    show()
