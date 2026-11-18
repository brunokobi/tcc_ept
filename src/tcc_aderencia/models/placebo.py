"""Placebos de território e de eixo (spec 04)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def territory_placebo(panel: pd.DataFrame, seed: int) -> pd.DataFrame:
    raise NotImplementedError


def axis_placebo(panel: pd.DataFrame, seed: int) -> pd.DataFrame:
    raise NotImplementedError
