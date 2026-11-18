"""Instrumento shift-share (Bartik) e diagnósticos (spec 03/04)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def build_instrument(
    employment: pd.DataFrame, mapping: pd.DataFrame, base_lag: int = 1
) -> pd.DataFrame:
    raise NotImplementedError


def rotemberg_weights(panel: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError


def fit_2sls(panel: pd.DataFrame, outcome: str) -> object:
    raise NotImplementedError
