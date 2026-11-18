"""Divisão regional do IBGE: município → região imediata/intermediária (spec 01)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def load_territories() -> pd.DataFrame:
    raise NotImplementedError
