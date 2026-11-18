"""Estudo de evento com choques de grandes empregadores (spec 04)."""

from __future__ import annotations


def build_events(establishments: "pd.DataFrame") -> "pd.DataFrame":
    raise NotImplementedError


def fit(panel: "pd.DataFrame", events: "pd.DataFrame", window: tuple[int, int] = (-3, 3)) -> object:
    raise NotImplementedError

