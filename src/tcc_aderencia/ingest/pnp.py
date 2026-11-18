"""Plataforma Nilo Peçanha: ofertas e indicadores por ciclo (spec 01)."""

from __future__ import annotations


def download(year: int) -> None:
    raise NotImplementedError


def load_cycles(years: list[int]) -> "pd.DataFrame":
    raise NotImplementedError


def match_courses_to_cnct(pnp: "pd.DataFrame", cnct: "pd.DataFrame") -> "pd.DataFrame":
    raise NotImplementedError

