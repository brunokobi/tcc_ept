"""Precisão/revocação/F1 por eixo, alfa de Krippendorff, comparação com baseline (spec 02)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from tcc_aderencia.config import SEED

NAO_SE_APLICA = "Não se aplica (nenhum curso técnico)"


def per_axis_metrics(gold: pd.DataFrame, pred: pd.DataFrame) -> pd.DataFrame:
    """Precision, recall, F1 and support per axis + macro/micro rows.

    gold: cnae_subclasse, eixo_principal; pred: cnae_subclasse, eixo_pred. Subclasses annotated
    as "não se aplica" count as a class of their own (a classifier that always assigns an axis
    gets them wrong).
    """
    m = gold.merge(pred, on="cnae_subclasse", how="inner")
    y, p = m.eixo_principal.to_numpy(), m.eixo_pred.to_numpy()
    rows = []
    for e in sorted(set(y) | set(p)):
        tp = int(((y == e) & (p == e)).sum())
        fp = int(((y != e) & (p == e)).sum())
        fn = int(((y == e) & (p != e)).sum())
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        rows.append((e, prec, rec, f1, int((y == e).sum())))
    out = pd.DataFrame(rows, columns=["eixo", "precisao", "revocacao", "f1", "suporte"])
    present = out[out.suporte > 0]
    macro = present[["precisao", "revocacao", "f1"]].mean()
    micro = float((y == p).mean())  # single-label: micro P = R = F1 = accuracy
    extra = pd.DataFrame(
        [
            ("macro", macro.precisao, macro.revocacao, macro.f1, int(present.suporte.sum())),
            ("micro", micro, micro, micro, len(m)),
        ],
        columns=out.columns,
    )
    return pd.concat([out, extra], ignore_index=True)


def bootstrap_f1(gold: pd.DataFrame, pred: pd.DataFrame, n: int = 2000, seed: int = SEED):
    """Point estimate and 95% percentile CI of macro-F1, resampling subclasses."""
    m = gold.merge(pred, on="cnae_subclasse")
    rng = np.random.default_rng(seed)

    def macro(df):
        t = per_axis_metrics(df[["cnae_subclasse", "eixo_principal"]], df[["cnae_subclasse", "eixo_pred"]])
        return float(t.loc[t.eixo == "macro", "f1"].iat[0])

    stats = []
    for _ in range(n):
        s = m.iloc[rng.integers(0, len(m), len(m))].copy()
        s["cnae_subclasse"] = np.arange(len(s)).astype(str)  # keep duplicates distinct
        stats.append(macro(s))
    lo, hi = np.percentile(stats, [2.5, 97.5])
    return macro(m), float(lo), float(hi)


def krippendorff_nominal(labels: pd.DataFrame) -> float:
    """Krippendorff's alpha (nominal) for annotators in columns, units in rows; NaN = missing."""
    import krippendorff

    data = labels.to_numpy(dtype=object).T
    cats = {v: i for i, v in enumerate(sorted({x for x in data.ravel() if pd.notna(x)}))}
    coded = np.array([[cats[x] if pd.notna(x) else np.nan for x in row] for row in data], float)
    return float(krippendorff.alpha(reliability_data=coded, level_of_measurement="nominal"))


def inter_llm_agreement(labels: pd.DataFrame) -> float:
    """Agreement between LLM providers (columns) — same statistic as for human annotators."""
    return krippendorff_nominal(labels)
