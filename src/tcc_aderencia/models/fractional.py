"""Logit fracionário ponderado com efeitos fixos (spec 04)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def fit(panel: pd.DataFrame, outcome: str) -> object:
    raise NotImplementedError
