"""Plataforma Nilo Peçanha: ofertas e indicadores por ciclo (spec 01)."""

from __future__ import annotations

import unicodedata
from pathlib import Path

import duckdb
import pandas as pd

from tcc_aderencia.config import DATA, REFERENCE

PNP_DIR = DATA / "pnp"
IBGE_RGI = DATA / "external" / "ibge_municipios_rgi.csv"
CNCT = DATA / "external" / "cnct4_cursos.csv"
OVERRIDES = REFERENCE / "pnp_cnct_overrides.csv"

# Outcome categories ("Categoria da Situação"): 2018 uses Evasão/Conclusão/Retidos;
# 2019+ use Evadidos/Concluintes/Em curso; 2023 splits conclusion into Concluintes/Concluídos.
EVASAO = ("Evadidos", "Evasão")
CONCLUSAO = ("Concluintes", "Concluídos", "Conclusão")

# Edition 2018 has no cycle code. This key reproduces the real code in 2019 and 2023 without
# ever splitting a cycle; it merges two cycles into one key in 0.3% (2019) / 0.9% (2023) of keys.
CYCLE_KEY = (
    "Cod Unidade",
    "Nome de Curso",
    "Data de Inicio do Ciclo",
    "Data de Fim Previsto do Ciclo",
    "Modalidade de Ensino",
    "Tipo de Oferta",
)


def download(year: int) -> None:
    raise NotImplementedError("PNP portal blocks automated download; get the CSV manually")


def load_cycles(
    years: list[int], tipo_curso: str = "Técnico", pnp_dir: Path = PNP_DIR
) -> pd.DataFrame:
    """One row per enrollment cycle with evasion and conclusion rates, enrollments and the
    territory (região imediata) of the teaching unit.

    Cycles come from `Código do Ciclo Matricula`; in edition 2018, which lacks it, they are
    reconstructed from `CYCLE_KEY` (`ciclo_reconstruido = True`). Each row of the source is one
    enrollment.
    """
    files = [str(pnp_dir / f"eficiencia_academica_{y}.parquet") for y in years]
    ev = ", ".join(f"'{c}'" for c in EVASAO)
    co = ", ".join(f"'{c}'" for c in CONCLUSAO)
    key = " || '|' || ".join(f'coalesce(p."{c}", \'\')' for c in CYCLE_KEY)
    con = duckdb.connect()
    con.register("rgi", pd.read_csv(IBGE_RGI, dtype=str))
    return con.execute(
        f"""
        select cast(p."Ano" as int) as edicao,
               case when p."Código do Ciclo Matricula" = 'Não Informado'
                    then 'R:' || md5({key}) else p."Código do Ciclo Matricula" end as ciclo,
               bool_or(p."Código do Ciclo Matricula" = 'Não Informado') as ciclo_reconstruido,
               any_value(p."Cod Unidade") as campus,
               any_value(p."Código do Município com DV") as cod_mun7,
               any_value(r.cod_rgi) as territorio,
               any_value(trim(lower(p."Nome de Curso"))) as curso,
               any_value(p."Eixo Tecnológico") as eixo,
               any_value(p."Tipo de Oferta") as tipo_oferta,
               any_value(p."Modalidade de Ensino") = 'Educação a Distância' as ead,
               any_value(strptime(p."Data de Inicio do Ciclo", '%d/%m/%Y')) as inicio,
               any_value(strptime(p."Data de Fim Previsto do Ciclo", '%d/%m/%Y')) as fim_previsto,
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


def norm_course(name: str) -> str:
    """Lowercase, no accents, no 'técnico em' prefix, single spaces."""
    s = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().lower()
    s = s.replace("tecnico em ", "").replace("tecnico de ", "").replace("-", " ")
    return " ".join(s.split())


def course_lookup(cnct: pd.DataFrame) -> dict[str, str]:
    """Normalized current or former CNCT name → current CNCT course name."""
    names = {norm_course(c): c for c in cnct.curso}
    for c, old in zip(cnct.curso, cnct.nomenclaturas_anteriores.fillna(""), strict=True):
        for o in str(old).split("\n"):
            o = o.strip("• ").strip()
            if o:
                names.setdefault(norm_course(o), c)
    return names


def match_courses_to_cnct(pnp: pd.DataFrame, cnct: pd.DataFrame | None = None) -> pd.DataFrame:
    """Add `curso_cnct` and `eixo_cnct` to PNP rows (column `curso`).

    Order: manual overrides (`data/reference/pnp_cnct_overrides.csv`, columns
    `curso_pnp, curso_cnct`; empty `curso_cnct` = out of scope) → exact normalized name →
    former names listed in the CNCT. Unmatched rows keep NaN.
    """
    cnct = pd.read_csv(CNCT) if cnct is None else cnct
    lookup = course_lookup(cnct)
    over = {}
    if OVERRIDES.exists():
        o = pd.read_csv(OVERRIDES, dtype=str, keep_default_na=False)
        over = {norm_course(a): (b or None) for a, b in zip(o.curso_pnp, o.curso_cnct, strict=True)}
    keys = pnp.curso.map(norm_course)
    matched = keys.map(lambda k: over[k] if k in over else lookup.get(k))
    eixo = dict(zip(cnct.curso, cnct.eixo, strict=True))
    return pnp.assign(curso_cnct=matched, eixo_cnct=matched.map(eixo))
