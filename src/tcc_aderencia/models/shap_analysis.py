"""Gradient boosting + SHAP, exploratório (spec 04)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def explain(panel: pd.DataFrame, outcome: str) -> pd.DataFrame:
    raise NotImplementedError
