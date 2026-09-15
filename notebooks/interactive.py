"""MiniRes in the browser, with sliders: a [marimo](https://marimo.io) notebook.

Exported to WebAssembly (Pyodide) by `.github/workflows/docs.yml`, and published at
<https://patnr.github.io/MiniRes/wasm/>, in run mode with the code hidden: the
essential snippet is quoted in the introduction's fenced block instead (showing
the cells themselves, `--show-code`, was tried and found too busy). Also runs natively: `uv run marimo edit
notebooks/interactive.py`.
"""

import marimo

__generated_with = "0.24.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # MiniRes

    A [2D two-phase reservoir simulator](https://patnr.github.io/MiniRes/)
    running **in this tab** -- the Python is WebAssembly, there is no server.
    Drag the sliders: the simulation re-runs (the following code):

    ```python
    model = ResSim(Lx=1, Ly=1, Nx=32, Ny=32,
                   fluid=dict(vo=M.value),
                   wells=[dict(name="Inj",  xy=[0, 0], rate=+1),
                          dict(name="Prod", xy=[1, 1], rate=-1)])

    S, P = model.sim(0.7/nSteps, nSteps, np.zeros(model.Nxy), pbar=False)
    ```
    """)
    return


@app.cell(hide_code=True)
async def _():
    import sys

    import marimo as mo

    if sys.platform == "emscripten":  # i.e. WebAssembly, in the browser
        import micropip

        await micropip.install("minires")

    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.ticker import MaxNLocator

    import minires
    from minires import ResSim

    return MaxNLocator, ResSim, minires, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    nSteps = 28
    # `debounce`: re-run on release, not on every pixel of a drag.
    M = mo.ui.slider(1, 10, value=1, show_value=True, debounce=True,
                     label=r"Viscosity ratio, $\mu_o/\mu_w$")
    k = mo.ui.slider(0, nSteps, value=nSteps, show_value=True, debounce=True,
                     label="Time step")
    mo.vstack([M, k])
    return M, k, nSteps


@app.cell
def _(M, ResSim, nSteps, np):
    model = ResSim(Lx=1, Ly=1, Nx=32, Ny=32,
                   fluid=dict(vo=M.value),
                   wells=[dict(name="Inj",  xy=[0, 0], rate=+1),
                          dict(name="Prod", xy=[1, 1], rate=-1)])

    S, P = model.sim(0.7/nSteps, nSteps, np.zeros(model.Nxy), pbar=False)
    return P, S, model


@app.cell
def _(MaxNLocator, P, S, k, model, plt):
    fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(10, 4.2))
    model.plt_field(ax1, S[k.value], "oil")
    # Levels fixed over time (the whole of `P`), at round numbers.
    model.plt_field(ax2, P[k.value], title="Pressure",
                    levels=MaxNLocator(11).tick_values(P.min(), P.max()))
    fig
    return


@app.cell(hide_code=True)
def _(minires, mo):
    mo.md(rf"""
    At $\mu_o/\mu_w = 1$ the front is the symmetric arc that gives the
    quarter five-spot its name. Raising the ratio makes the water the more
    mobile phase: it channels along the diagonal and breaks through early,
    leaving the flanks unswept -- an unfavourable mobility ratio.

    [Docs](https://patnr.github.io/MiniRes/minires.html)
    &middot; [More examples](https://patnr.github.io/MiniRes/examples.html)
    &middot; [GitHub](https://github.com/patnr/MiniRes)
    &middot; minires {minires.__version__}
    """)
    return


if __name__ == "__main__":
    app.run()
