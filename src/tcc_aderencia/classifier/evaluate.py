"""Precisão/revocação/F1 por eixo, alfa de Krippendorff, comparação com baseline (spec 02)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def per_axis_metrics(gold: pd.DataFrame, pred: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError


def inter_llm_agreement(labels: pd.DataFrame) -> float:
    raise NotImplementedError
