"""Simulação de poder com a estrutura real do painel (spec 04).

Effect injection: the real cycle structure and the real outcome are kept; the adherence index Q
is drawn at random (territory × course, constant across cycles) so it carries no real effect.
In a linear probability model the estimate on `y + β·X` is `β + b₀`, with `b₀` and its standard
error coming from the regression on the real `y` alone. One regression per draw therefore gives
the power curve for every β, and the MDE is the smallest β rejected in `power` of the draws.

MDE is in outcome units (rate, 0–1) per 1 SD of the idiosyncratic territory × course component
of Q, i.e. the variation left after the campus × cycle and course × cycle fixed effects. If only
a fraction `f` of the variance of Q is idiosyncratic, the MDE per 1 SD of Q scales by 1/√f.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from linearmodels.iv.absorbing import AbsorbingLS
from scipy import stats

from tcc_aderencia.config import SEED

TERMS = ("q", "q_ead")


def _draw_q(panel: pd.DataFrame, rng: np.random.Generator) -> pd.Series:
    cells = panel[["territorio", "curso"]].drop_duplicates()
    cells = cells.assign(q=rng.standard_normal(len(cells)))
    return panel[["territorio", "curso"]].merge(cells, how="left")["q"].to_numpy()


def simulate(
    panel: pd.DataFrame,
    outcome: str = "evasao",
    absorb: tuple[str, ...] = ("campus", "curso"),
    n_sims: int = 500,
    seed: int = SEED,
) -> pd.DataFrame:
    """Per draw: estimate and clustered SE of `q` (H1a) and `q_ead` (H2) on the real outcome.

    `absorb` lists fixed effects interacted with the cycle edition (e.g. campus × edição).
    """
    rng = np.random.default_rng(seed)
    p = panel.reset_index(drop=True)
    fe = pd.DataFrame(
        {f: (p[f].astype(str) + "|" + p["edicao"].astype(str)).astype("category") for f in absorb}
    )
    clusters = p["territorio"].astype("category").cat.codes.to_frame("territorio")
    rows = []
    for i in range(n_sims):
        q = _draw_q(p, rng)
        exog = pd.DataFrame({"q": q, "q_ead": q * p["ead"].astype(float)})
        res = AbsorbingLS(p[outcome], exog, absorb=fe, weights=p["matriculas"]).fit(
            cov_type="clustered", clusters=clusters
        )
        rows.append(
            {"sim": i}
            | {f"b_{t}": res.params[t] for t in TERMS}
            | {f"se_{t}": res.std_errors[t] for t in TERMS}
        )
    return pd.DataFrame(rows)


def power_curve(sims: pd.DataFrame, term: str, betas: np.ndarray, alpha: float = 0.05):
    z = stats.norm.ppf(1 - alpha / 2)
    b, se = sims[f"b_{term}"].to_numpy(), sims[f"se_{term}"].to_numpy()
    return np.array([(np.abs(beta + b) / se > z).mean() for beta in betas])


def minimum_detectable_effect(
    sims: pd.DataFrame, term: str = "q_ead", power: float = 0.8, alpha: float = 0.05
) -> float:
    """Smallest positive β whose rejection rate across draws reaches `power`."""
    hi = 20 * sims[f"se_{term}"].max()
    betas = np.linspace(0, hi, 4001)
    pw = power_curve(sims, term, betas, alpha)
    ok = np.nonzero(pw >= power)[0]
    return float(betas[ok[0]]) if len(ok) else float("nan")
