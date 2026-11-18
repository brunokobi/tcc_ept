"""Simulação de poder com a estrutura real do painel (spec 04)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def minimum_detectable_effect(panel: pd.DataFrame, n_sims: int = 500, power: float = 0.8) -> float:
    raise NotImplementedError
