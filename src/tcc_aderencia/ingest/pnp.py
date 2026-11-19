"""Plataforma Nilo Peçanha: ofertas e indicadores por ciclo (spec 01)."""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from tcc_aderencia.config import DATA

PNP_DIR = DATA / "pnp"
IBGE_RGI = DATA / "external" / "ibge_municipios_rgi.csv"

# Outcome categories per edition ("Categoria da Situação"). 2023 splits conclusion in two.
EVASAO = ("Evadidos",)
CONCLUSAO = ("Concluintes", "Concluídos")


def download(year: int) -> None:
    raise NotImplementedError("PNP portal blocks automated download; get the CSV manually")


def load_cycles(
    years: list[int], tipo_curso: str = "Técnico", pnp_dir: Path = PNP_DIR
) -> pd.DataFrame:
    """One row per enrollment cycle (`Código do Ciclo Matricula`) with evasion and conclusion
    rates, enrollments and the territory (região imediata) of the teaching unit.

    Edition 2018 has no cycle code and aggregated rows; it is not supported here (spec 01 log).
    """
    if 2018 in years:
        raise ValueError("PNP 2018 has no cycle code; reconstruct cycles separately (P5)")
    files = [str(pnp_dir / f"eficiencia_academica_{y}.parquet") for y in years]
    ev = ", ".join(f"'{c}'" for c in EVASAO)
    co = ", ".join(f"'{c}'" for c in CONCLUSAO)
    con = duckdb.connect()
    con.register("rgi", pd.read_csv(IBGE_RGI, dtype=str))
    df = con.execute(
        f"""
        select cast(p."Ano" as int) as edicao,
               p."Código do Ciclo Matricula" as ciclo,
               any_value(p."Cod Unidade") as campus,
               any_value(p."Código do Município com DV") as cod_mun7,
               any_value(r.cod_rgi) as territorio,
               any_value(trim(lower(p."Nome de Curso"))) as curso,
               any_value(p."Eixo Tecnológico") as eixo,
               any_value(p."Tipo de Oferta") as tipo_oferta,
               any_value(p."Modalidade de Ensino") = 'Educação a Distância' as ead,
               count(*) as matriculas,
               avg((p."Categoria da Situação" in ({ev}))::double) as evasao,
               avg((p."Categoria da Situação" in ({co}))::double) as conclusao
        from read_parquet(?) p
        left join rgi r on r.cod_mun7 = p."Código do Município com DV"
        where p."Tipo de Curso" = ?
        group by 1, 2
        """,
        [files, tipo_curso],
    ).df()
    return df
