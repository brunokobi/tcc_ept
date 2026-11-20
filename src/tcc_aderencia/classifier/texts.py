"""Textos de entrada do caminho T (spec 02): CNAE e cursos do CNCT."""

from __future__ import annotations

import re

import pandas as pd

from tcc_aderencia.config import DATA

_NOT_COMPRISES = re.compile(r"\|?\s*Esta subclasse N[ÃA]O compreende.*", re.IGNORECASE | re.DOTALL)


def comprises(obs: str) -> str:
    """Keep only the 'compreende' part of the explanatory notes (drop 'NÃO compreende')."""
    return _NOT_COMPRISES.sub("", str(obs or "")).strip()


def cnae_texts(cnae: pd.DataFrame | None = None) -> pd.DataFrame:
    """cnae_subclasse, texto = descrição + compreende + atividades."""
    if cnae is None:
        cnae = pd.read_csv(DATA / "external" / "cnae_subclasses.csv", dtype=str)
    texto = (
        cnae.descricao.str.capitalize()
        + ". "
        + cnae.observacoes.map(comprises)
        + ". Atividades: "
        + cnae.atividades.fillna("").str.lower()
    )
    return pd.DataFrame({"cnae_subclasse": cnae.cnae_subclasse, "texto": texto})


def course_texts(cnct: pd.DataFrame | None = None) -> pd.DataFrame:
    """curso, eixo, texto = nome + perfil + campo de atuação (civil courses only)."""
    if cnct is None:
        cnct = pd.read_csv(DATA / "external" / "cnct4_cursos.csv")
    c = cnct[cnct.eixo != "Militar"]
    texto = (
        c.curso + ". " + c.perfil.fillna("") + " Campo de atuação: " + c.campo_atuacao.fillna("")
    )
    return pd.DataFrame({"curso": c.curso, "eixo": c.eixo, "texto": texto}).reset_index(drop=True)
