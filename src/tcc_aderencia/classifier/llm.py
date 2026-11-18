"""Desambiguação por LLM com saída estruturada e cache em disco (spec 02)."""

from __future__ import annotations


def is_ambiguous(top1: float, top2: float, tau: float, delta: float) -> bool:
    raise NotImplementedError


def resolve(cnae_row: dict, candidates: list[dict], model: str) -> dict:
    raise NotImplementedError
