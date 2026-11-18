"""Estabelecimentos ativos por município × CNAE × ano, a partir do pipeline CNPJ existente (spec 01)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def build_establishment_stock(years: list[int]) -> pd.DataFrame:
    raise NotImplementedError
