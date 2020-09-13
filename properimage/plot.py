"""plot module from ProperImage,
for coadding astronomical images.

Written by Bruno SANCHEZ

PhD of Astromoy - UNC
bruno@oac.unc.edu.ar

Instituto de Astronomia Teorica y Experimental (IATE) UNC
Cordoba - Argentina

Of 301
"""

import logging

import numpy as np

from astropy.stats import sigma_clipped_stats

import matplotlib.pyplot as plt

import attr


# =============================================================================
# CONSTANTS
# =============================================================================

FONT = {
    "family": "sans-serif",
    "sans-serif": ["Computer Modern Sans serif"],
    "weight": "regular",
    "size": 12,
}

TEXT = {"usetex": True}


logger = logging.getLogger()


# =============================================================================
# FUNCTIONS
# =============================================================================


def primes(n):
    divisors = [d for d in range(2, n // 2 + 1) if n % d == 0]
    prims = [
        d for d in divisors if all(d % od != 0 for od in divisors if od != d)
    ]
    if len(prims) >= 4:
        return prims[-1] * prims[-2]
    elif len(prims) == 0:
        return n

    return max(prims)


def plot_psfbasis(
    psf_basis, path=None, nbook=False, size=4, iso=False, **kwargs
):
    # psf_basis.reverse()
    xsh, ysh = psf_basis[1].shape
    N = len(psf_basis)
    p = _primes(N)
    if N == 2:
        subplots = (2, 1)
    elif p == N:
        subplots = (np.rint(np.sqrt(N)), np.rint(np.sqrt(N) + 1))
    else:
        rows = N // p
        rows += N % p
        subplots = (p, rows)

    plt.figure(figsize=(size * subplots[0], size * subplots[1]))
    for i in range(len(psf_basis)):
        plt.subplot(subplots[1], subplots[0], i + 1)
        plt.imshow(psf_basis[i], interpolation="none", cmap="viridis")
        labels = {"j": i + 1, "sum": np.sum(psf_basis[i])}
        plt.title(r"$\sum p_{j:d} = {sum:4.3e}$".format(**labels))
        # , interpolation='linear')
        plt.colorbar(shrink=0.85)
        if iso:
            plt.contour(
                np.arange(xsh),
                np.arange(ysh),
                psf_basis[i],
                colors="red",
                alpha=0.4,
            )
    plt.tight_layout()
    if path is not None:
        plt.savefig(path)
    if not nbook:
        plt.close()


# def plot_afields(a_fields, x, y, path=None, nbook=False, size=4, **kwargs):
#     if a_fields[0] is None:
#         logging.warning("No a_fields were calculated. Only one Psf Basis")
#         return
#     # a_fields.reverse()
#     N = len(a_fields)
#     p = _primes(N)
#     if N == 2:
#         subplots = (2, 1)
#     elif p == N:
#         subplots = (np.rint(np.sqrt(N)), np.rint(np.sqrt(N) + 1))
#     else:
#         rows = N // p
#         rows += N % p
#         subplots = (p, rows)

#     plt.figure(figsize=(size * subplots[0], size * subplots[1]), **kwargs)
#     for i in range(len(a_fields)):
#         plt.subplot(subplots[1], subplots[0], i + 1)
#         a = a_fields[i](x, y)
#         mean, med, std = sigma_clipped_stats(a)
#         plt.imshow(a, vmax=med + 2 * std, vmin=med - 2 * std, cmap="viridis")
#         labels = {"j": i + 1, "sum": np.sqrt(np.sum(a ** 2))}
#         plt.title(r"$a_{j}$,$\sum a_{j}={sum:4.3e}$".format(**labels))
#         plt.colorbar(shrink=0.75, aspect=30)
#     plt.tight_layout()
#     if path is not None:
#         plt.savefig(path)
#     if not nbook:
#         plt.close()
#     return


def plot_S(S, path=None, nbook=False):
    if isinstance(S, np.ma.masked_array):
        S = S.filled()
    mean, med, std = sigma_clipped_stats(S)
    plt.imshow(
        S,
        vmax=med + 4 * std,
        vmin=med - 4 * std,
        interpolation="none",
        cmap="viridis",
    )
    plt.tight_layout()
    plt.colorbar()
    if path is not None:
        plt.savefig(path)
    else:
        plt.show()
    if not nbook:
        plt.close()
    return


def plot_R(R, path=None, nbook=False):
    if isinstance(R[0, 0], np.complex):
        R = R.real
    if isinstance(R, np.ma.masked_array):
        R = R.filled()
    plt.imshow(np.log10(R), interpolation="none", cmap="viridis")
    plt.tight_layout()
    plt.colorbar()
    if path is not None:
        plt.savefig(path)
    else:
        plt.show()
    if not nbook:
        plt.close()
    return


# =============================================================================
# PLOT API
# =============================================================================


@attr.s(frozen=True, repr=False, eq=False, order=False)
class Plot:

    DEFAULT_PLOT = "imshow"

    si = attr.ib()

    def __call__(self, plot=None, ax=None, **kwargs):
        if plot is not None and ("_" in plot or not hasattr(self, plot)):
            raise ValueError(f"Ivalid plot method '{plot}'")
        method = getattr(self, plot or Plot.DEFAULT_PLOT)
        if not callable(method):
            raise ValueError(f"Ivalid plot method '{plot}'")
        return method(ax=ax, **kwargs)

    def imshow(self, ax=None, **kwargs):
        ax = plt.gca() if ax is None else ax

        kwargs.setdefault("origin", "lower")

        ax.imshow(self.si.data, **kwargs)

        ax.set_title(f"SingleImage {self.si.data.shape}")
        return ax
