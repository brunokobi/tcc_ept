"""Linha de base por palavras-chave / TF-IDF (spec 02)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def classify(cnae: pd.DataFrame, cnct: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError
