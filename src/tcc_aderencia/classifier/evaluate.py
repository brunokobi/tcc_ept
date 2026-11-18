"""Precisão/revocação/F1 por eixo, alfa de Krippendorff, comparação com baseline (spec 02)."""

from __future__ import annotations


def per_axis_metrics(gold: "pd.DataFrame", pred: "pd.DataFrame") -> "pd.DataFrame":
    raise NotImplementedError


def inter_llm_agreement(labels: "pd.DataFrame") -> float:
    raise NotImplementedError

