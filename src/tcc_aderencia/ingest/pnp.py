"""Plataforma Nilo Peçanha: ofertas e indicadores por ciclo (spec 01)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def download(year: int) -> None:
    raise NotImplementedError


def load_cycles(years: list[int]) -> pd.DataFrame:
    raise NotImplementedError


def match_courses_to_cnct(pnp: pd.DataFrame, cnct: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError
