"""Vínculos RAIS (PDET) por município × CNAE subclasse × ano (spec 01)."""

from __future__ import annotations


def download(year: int) -> None:
    raise NotImplementedError


def load_employment(years: list[int]) -> "pd.DataFrame":
    raise NotImplementedError

