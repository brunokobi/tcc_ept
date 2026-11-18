"""Similaridade por embeddings sentence-transformers (spec 02)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd


def embed(texts: list[str], model_name: str) -> np.ndarray:
    raise NotImplementedError


def rank_candidates(cnae: pd.DataFrame, cnct: pd.DataFrame, top_k: int = 5) -> pd.DataFrame:
    raise NotImplementedError
