"""Caminho O: peso CNAE → curso pelas ocupações (CBO) do curso na RAIS (spec 02).

w_O(s, c) = Σ_{o ∈ CBO(c)} V(s, o) / Σ_o V(s, o), where V(s, o) is the national number of active
jobs in subclass s and occupation o, averaged over `years`. CNCT lists 6-digit occupations or
4-digit families (e.g. Informática: 3171;3172), so occupations match by prefix. Courses without
CBO (26 civil ones, e.g. Administração) only get the T path.
"""

from __future__ import annotations

import duckdb
import pandas as pd

from tcc_aderencia.config import DATA, INTERIM
from tcc_aderencia.ingest.cnae import harmonize

DEFAULT_YEARS = range(2019, 2024)


def course_cbo(cnct: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per (civil course, CBO code or family prefix)."""
    if cnct is None:
        cnct = pd.read_csv(DATA / "external" / "cnct4_cursos.csv")
    c = cnct[cnct.eixo != "Militar"].dropna(subset=["cbo_codes"])
    c = c.assign(cbo=c.cbo_codes.astype(str).str.split(";")).explode("cbo")
    return c.assign(cbo=c.cbo.str.strip())[["curso", "eixo", "cbo"]].drop_duplicates()


def subclass_occupation(years=DEFAULT_YEARS) -> pd.DataFrame:
    """V(s, o): national mean jobs per (CNAE 2.3 subclass, CBO) over `years`."""
    files = [f"{INTERIM}/rais/{y}/*.parquet" for y in years]
    v = duckdb.sql(
        f"""select cnae_subclasse, cbo, sum(vinculos) / {len(list(years))} as vinculos
            from read_parquet({files}) group by all"""
    ).df()
    return harmonize(v).groupby(["cnae_subclasse", "cbo"], as_index=False).vinculos.sum()


def build_w_o(v: pd.DataFrame, cc: pd.DataFrame) -> pd.DataFrame:
    """Columns cnae_subclasse, curso, eixo, w_O, vinculos_subclasse (only w_O > 0)."""
    con = duckdb.connect()
    con.register("v", v)
    con.register("cc", cc)
    return con.execute(
        """
        with tot as (select cnae_subclasse, sum(vinculos) t from v group by 1),
             link as (
               select v.cnae_subclasse, cc.curso, any_value(cc.eixo) eixo, sum(v.vinculos) l
               from v join (select distinct curso, eixo, cbo from cc) cc
                 on starts_with(v.cbo, cc.cbo)
               group by 1, 2)
        select link.cnae_subclasse, curso, eixo, l / t as w_O, t as vinculos_subclasse
        from link join tot using (cnae_subclasse)
        order by 1, w_O desc
        """
    ).df()
