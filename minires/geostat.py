"""Gaussian random fields, for synthetic permeabilities and priors.

A stationary, isotropic Gaussian field over the given points -- typically the cell
centres of a `minires.Grid2D.mesh` -- defined by its *variogram*, $ γ(h) $, i.e.
the covariance $ c(h) = 1 - γ(h) $ as a function of the distance $ h $. Here the
Gaussian one, `variogram_gauss`, whose one parameter of note is the range, `r`
(the correlation drops to $ e^{-3} $ at $ h = r $, for the default `a`).
`cov_sqrt` forms the covariance matrix of the field over the points and returns
its (upper) Cholesky factor, $ \\mathbf{C} = \\mathbf{C}_{1/2}^T \\mathbf{C}_{1/2} $,
so that `gaussian_fields` samples the field as $ \\mathbf{z} \\, \\mathbf{C}_{1/2} $,
with $ \\mathbf{z} $ standard normal -- `N` of them at a time, each of unit
variance and zero mean.

>>> from minires import Grid2D
>>> grid = Grid2D(Lx=1, Ly=1, Nx=8, Ny=8)
>>> C12 = cov_sqrt(grid.mesh, r=.3)
>>> C12.shape
(64, 64)
>>> Cov = 1 - variogram_gauss(dist_euclid(vectorize(*grid.mesh)), r=.3)
>>> bool(np.allclose(C12.T @ C12, Cov))
True
>>> fields = gaussian_fields(grid.mesh, N=3, r=.3, rng=np.random.default_rng(0))
>>> fields.shape
(3, 64)

The covariance matrix is *dense*, `(nPts, nPts)`, and factorized outright (with a
tiny jitter on the diagonal, the Gaussian covariance being nearly singular), so
this is for the toy grids of this package -- a few thousand cells at most --
and not a geostatistics library. The fields being Gaussian, they serve as
*log*-permeabilities (`K = exp(logK)`), or as the Gaussian prior of an ensemble
method (ref `examples.random_fields`, and the tutorials of
[HistoryMatching](https://github.com/patnr/HistoryMatching), which also use
`cov_sqrt` as the change of variables of a variational method).
`funm_psd` is a general matrix function for such (positive semi-definite)
covariances, e.g. the symmetric square root.
"""

import numpy as np
import scipy.linalg as sla


def variogram_gauss(xx: np.ndarray, r: float, n: float = 0, a: float = 1 / 3) -> np.ndarray:
    """Gaussian variogram at the distances `xx`.

    Params: range `r`, nugget `n`, and `a`, which scales the range
    (for the default, the covariance $ 1 - γ $ is $ e^{-3} $ at `r`).
    Ref: <https://en.wikipedia.org/wiki/Variogram#Variogram_models>

    >>> xx = np.array([0, 1, 2])
    >>> variogram_gauss(xx, 1, n=0.1, a=1)
    array([0.        , 0.6689085 , 0.98351593])
    """
    # Gauss
    gamma = 1 - np.exp(-(xx**2) / r**2 / a)
    # Sill (=1)
    gamma *= 1 - n
    # Nugget
    gamma[xx != 0] += n
    return gamma


def vectorize(*XYZ: np.ndarray) -> np.ndarray:
    """Reshape coordinate arrays (`nDim` of them, of equal `shape`) to `(nPts, nDim)`."""
    return np.stack(XYZ).reshape((len(XYZ), -1)).T


def dist_euclid(X: np.ndarray) -> np.ndarray:
    """Pairwise distances between the rows of `X`, like `squareform(pdist(X))`."""
    diff = X[:, None, :] - X
    d2 = np.sum(diff**2, axis=-1)
    return np.sqrt(d2)


def funm_psd(C, fun, rk=None, rtol=1e-8, sym_square=True, **kwargs):
    """Matrix function evaluation for a positive semi-definite matrix.

    Adapted from the `scipy.linalg.funm` doc.

    Note: small `rk` and `driver="evx"` should be faster,
    but in my (simple but hopefully relevant) trials
    sticking with the default "evr" and `rk=None` is usually faster.
    Alternatively, could try iterative algorithms from `sparse.linalg`.

    Example
    -------
    >>> def sqrtm(C):
    ...     return funm_psd(C, np.sqrt)
    """
    # EVD -- possibly truncated (for speed)
    idx = [max(0, len(C) - rk), len(C) - 1] if rk else None
    ews, V = sla.eigh(C, subset_by_index=idx, **kwargs)

    # Truncate (for stability) -- NB: ordering low-->high!
    nNull = sum(ews <= rtol * ews.max())
    ews = ews[nNull:]
    V = V[:, nNull:]

    # Apply
    ews = fun(ews)

    # Reconstruct
    funC = V * ews
    if sym_square:
        # Optional, since not necessary e.g. for cholesky factors (for sampling)
        # But, without it the sqrtm is beholden to the "vagaries" of lapack version?
        funC = funC @ V.T
    return funC


def cov_sqrt(pts: tuple, r: float = 0.2) -> np.ndarray:
    """Cholesky factor, `C12`, of the covariance (Gaussian variogram) over `pts`.

    `pts` are coordinate arrays, e.g. `Grid2D.mesh` (or `(xx,)` in 1D).
    The factor is upper triangular, such that `Cov == C12.T @ C12`,
    and so `z @ C12` has covariance `Cov` if `z` is standard normal.
    """
    dists = dist_euclid(vectorize(*pts))
    Cov = 1 - variogram_gauss(dists, r)
    # C12    = sla.sqrtm(Cov).real.T                      # unstable for n >≈ 20
    # C12    = funm_psd(Cov, np.sqrt, sym_square=True).T  # too slow for n >= 50^2
    C12 = sla.cholesky(Cov + 1e-10 * np.eye(len(Cov)))
    return C12


def gaussian_fields(pts: tuple, N: int = 1, r: float = 0.2, rng=None) -> np.ndarray:
    """Sample `N` Gaussian random fields over `pts`, as `(N, nPts)`.

    Each of zero mean and unit variance, with the covariance of `cov_sqrt`
    (Gaussian variogram of range `r`). The draws come from `rng`
    (a `numpy.random.Generator`), or the global `numpy.random` state if `None`.
    """
    rng = np.random if rng is None else rng
    C12 = cov_sqrt(pts, r)
    fields = rng.standard_normal((N, len(C12))) @ C12
    return fields
