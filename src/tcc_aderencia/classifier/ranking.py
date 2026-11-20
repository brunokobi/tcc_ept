"""From a CNAE × course similarity matrix to course candidates and axis predictions."""

from __future__ import annotations

import numpy as np
import pandas as pd


def rank(sim: np.ndarray, cnae: pd.DataFrame, courses: pd.DataFrame, top_k: int = 5):
    """Return (candidates, axes).

    candidates: cnae_subclasse, rank, curso, eixo, score, w_T — top-k courses per subclass,
        w_T = score share among the top-k (a provisional weight until the LLM step).
    axes: cnae_subclasse, eixo_pred, score_1, eixo_2, score_2, margem — axis score is the max
        over its courses; `margem` (top1 − top2) feeds the ambiguity rule of the LLM step.
    """
    order = np.argsort(-sim, axis=1)[:, :top_k]
    rows = []
    for i, code in enumerate(cnae.cnae_subclasse):
        idx = order[i]
        s = np.clip(sim[i, idx], 0, None)
        w = s / s.sum() if s.sum() > 0 else np.full(len(idx), 1 / len(idx))
        for r, (j, sc, wt) in enumerate(zip(idx, sim[i, idx], w, strict=True), 1):
            rows.append((code, r, courses.curso.iat[j], courses.eixo.iat[j], float(sc), float(wt)))
    cand = pd.DataFrame(rows, columns=["cnae_subclasse", "rank", "curso", "eixo", "score", "w_T"])

    eixos = courses.eixo.to_numpy()
    names = np.unique(eixos)
    ax = np.column_stack([sim[:, eixos == e].max(axis=1) for e in names])
    o = np.argsort(-ax, axis=1)
    pick = np.arange(len(ax))
    axes = pd.DataFrame(
        {
            "cnae_subclasse": cnae.cnae_subclasse.to_numpy(),
            "eixo_pred": names[o[:, 0]],
            "score_1": ax[pick, o[:, 0]],
            "eixo_2": names[o[:, 1]],
            "score_2": ax[pick, o[:, 1]],
        }
    )
    axes["margem"] = axes.score_1 - axes.score_2
    return cand, axes
