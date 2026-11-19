"""Verificação de viabilidade com todos os dados baixados (RAIS 2012–2025 + PNP 2019–2023).

Descritivo apenas: nenhum modelo de efeito é estimado (regra do pré-registro). Mede cobertura e
qualidade das chaves, totais da RAIS, a ponte CBO (mapa O) em escala nacional, a variação de Q
e o quanto dela sobra após os FE (fração f), que reescala o MDE da §9 do relatório.

Uso: python scripts/verify_data.py [saida.json]
"""

from __future__ import annotations

import json
import sys
import unicodedata

import duckdb
import numpy as np
import pandas as pd

from tcc_aderencia.config import DATA, INTERIM
from tcc_aderencia.ingest.pnp import load_cycles

YEARS = list(range(2012, 2026))
# Estoque de vínculos ativos em 31/12 divulgado pelo MTE (milhões); conferir nas publicações.
OFFICIAL_STOCK_MI = {
    2012: 47.459, 2013: 48.948, 2014: 49.572, 2015: 48.061, 2016: 46.060, 2017: 46.282,
    2018: 46.632, 2019: 47.555, 2020: 46.236, 2021: 48.728, 2022: 52.777,
}  # fmt: skip
MIN_JOBS = 50  # cells with > 50 linked jobs, as in the prospecção


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return " ".join(s.replace("tecnico em ", "").replace("-", " ").split())


def rais_years(con) -> list[int]:
    return [y for y in YEARS if list((INTERIM / "rais" / str(y)).glob("*.parquet"))]


def rais_quality(con, years) -> pd.DataFrame:
    ibge = pd.read_csv(DATA / "external" / "ibge_municipios_rgi.csv", dtype=str)
    ibge["mun6"] = ibge.cod_mun7.str[:6]
    con.register("ibge", ibge)
    cnae = pd.read_csv(DATA / "external" / "cnae_subclasses.csv", dtype=str)[["cnae_subclasse"]]
    con.register("cnae", cnae)
    rows = []
    for y in years:
        con.execute(
            f"create or replace view r as select * from '{INTERIM}/rais/{y}/*.parquet'"
        )
        rows.append(
            con.execute(
                """
            select ?::int ano, sum(vinculos) vinculos, count(*) celulas,
                   count(distinct r.mun6) municipios,
                   coalesce(sum(vinculos) filter (where i.mun6 is null), 0) / sum(vinculos)
                       pct_mun_sem_ibge,
                   coalesce(sum(vinculos) filter (where c.cnae_subclasse is null), 0) / sum(vinculos)
                       pct_cnae_fora_23,
                   coalesce(sum(vinculos) filter (where not regexp_full_match(cbo, '[0-9]{6}')), 0)
                       / sum(vinculos) pct_cbo_invalido
            from r
            left join (select distinct mun6 from ibge) i using (mun6)
            left join cnae c using (cnae_subclasse)
            """,
                [y],
            ).df()
        )
    q = pd.concat(rows, ignore_index=True)
    q["oficial_mi"] = q.ano.map(OFFICIAL_STOCK_MI)
    q["dif_oficial_pct"] = 100 * (q.vinculos / 1e6 / q.oficial_mi - 1)
    return q


def course_cbo() -> pd.DataFrame:
    c = pd.read_csv(DATA / "external" / "cnct4_cursos.csv")
    c = c[c.eixo != "Militar"].dropna(subset=["cbo_codes"])
    c = c.assign(cbo=c.cbo_codes.str.split(";")).explode("cbo")
    return c[["curso", "eixo", "cbo"]].assign(cbo=lambda d: d.cbo.str.strip())


def q_by_rgi_course(con, year: int) -> pd.DataFrame:
    """Map O: course-linked jobs by região imediata → LQ. CNCT lists 6-digit occupations or
    4-digit families (e.g. Informática: 3171;3172), so CBOs match by prefix."""
    return con.execute(
        f"""
        with r as (select i.cod_rgi, x.cbo, sum(x.vinculos) v
                   from '{INTERIM}/rais/{year}/*.parquet' x
                   join (select distinct substr(cod_mun7,1,6) mun6, cod_rgi from ibge) i using (mun6)
                   group by all),
             tot_r as (select cod_rgi, sum(v) er from r group by 1),
             link as (select r.cod_rgi, cc.curso, sum(r.v) erc
                      from r join cc on starts_with(r.cbo, cc.cbo) group by all),
             tot_c as (select curso, sum(erc) ec from link group by 1),
             tot as (select sum(er) e from tot_r)
        select link.cod_rgi, link.curso, erc, ln((erc / er) / (ec / e)) as log_q
        from link join tot_r using (cod_rgi) join tot_c using (curso), tot
        """
    ).df()


def fe_share(df: pd.DataFrame) -> float:
    """Share of log Q variance NOT explained by additive RGI + course effects (fraction f)."""
    y = df.log_q.to_numpy()
    a = pd.Series(0.0, index=df.index)
    for _ in range(200):  # alternating projections
        old = a.copy()
        r = y - a
        b = r.groupby(df.curso).transform("mean")
        a = (y - b).groupby(df.cod_rgi).transform("mean")
        if np.abs(a - old).max() < 1e-10:
            break
    resid = y - a - b
    return float(resid.var() / y.var())


def main(out_json: str) -> None:
    con = duckdb.connect()
    years = rais_years(con)
    res: dict = {"rais_anos": years}

    qual = rais_quality(con, years)
    res["rais_qualidade"] = qual.round(5).to_dict("records")

    cc = course_cbo()
    con.register("cc", cc)
    cbo_set = set(cc.cbo)
    bridge = []
    for y in years:
        v = con.execute(
            f"select cbo, sum(vinculos) v from '{INTERIM}/rais/{y}/*.parquet' group by 1"
        ).df()
        prefixes = tuple(cbo_set)
        linked = v[v.cbo.str.startswith(prefixes)]
        present = {c for c in cbo_set if linked.cbo.str.startswith(c).any()}
        bridge.append(
            {
                "ano": y,
                "pct_vinculos_em_cbo_de_curso": float(linked.v.sum() / v.v.sum()),
                "cbos_de_curso_presentes": len(present),
                "cbos_de_curso_total": len(cbo_set),
            }
        )
    res["ponte_o"] = bridge

    qs = {y: q_by_rgi_course(con, y) for y in years}
    var = []
    for y, d in qs.items():
        big = d[d.erc > MIN_JOBS]
        var.append(
            {
                "ano": y,
                "celulas": len(d),
                "celulas_gt50": len(big),
                "dp_log_q_gt50": float(big.log_q.std()),
                "f_idiossincratica_gt50": fe_share(big),
                "f_idiossincratica_todas": fe_share(d),
            }
        )
    res["variacao_q"] = var

    pairs = []
    for y in years:
        if y + 5 in qs:
            m = qs[y].merge(qs[y + 5], on=["cod_rgi", "curso"], suffixes=("_0", "_1"))
            m = m[(m.erc_0 > MIN_JOBS) & (m.erc_1 > MIN_JOBS)]
            s = m.log_q_1 - m.log_q_0
            pairs.append(
                {
                    "anos": f"{y}-{y + 5}",
                    "pares": len(m),
                    "corr": float(m.log_q_0.corr(m.log_q_1)),
                    "dp_delta": float(s.std()),
                }
            )
    res["estabilidade_q_5anos"] = pairs

    # PNP ↔ CNCT (name or former name) ↔ Q coverage
    cyc = load_cycles([2019, 2020, 2021, 2022, 2023])
    cnct = pd.read_csv(DATA / "external" / "cnct4_cursos.csv")
    names = {norm(c): c for c in cnct.curso}
    for c, old in zip(cnct.curso, cnct.nomenclaturas_anteriores.fillna(""), strict=True):
        for o in old.split("\n"):
            names.setdefault(norm(o.strip("• ").strip()), c)
    cyc["curso_cnct"] = cyc.curso.map(lambda s: names.get(norm(s)))
    cyc["ano_q"] = cyc.edicao - 4  # Q before cycle start (cycles ≤ 4 years)
    qall = pd.concat([d.assign(ano_q=y) for y, d in qs.items()])
    qall = qall.rename(columns={"cod_rgi": "territorio", "curso": "curso_cnct"})
    m = cyc.merge(qall, on=["territorio", "curso_cnct", "ano_q"], how="left")
    tot = m.matriculas.sum()
    res["pnp_cobertura"] = {
        "ciclos": len(cyc),
        "pct_matriculas_curso_cnct": float(m.matriculas[m.curso_cnct.notna()].sum() / tot),
        "pct_matriculas_com_q": float(m.matriculas[m.log_q.notna()].sum() / tot),
        "pct_matriculas_ead_com_q": float(
            m.matriculas[m.log_q.notna() & m.ead].sum() / m.matriculas[m.ead].sum()
        ),
        "cursos_sem_cnct": cyc.loc[cyc.curso_cnct.isna(), "curso"]
        .value_counts()
        .head(15)
        .to_dict(),
    }
    # MDE rescale (§9): MDE per 1 SD of Q = MDE_idio / sqrt(f)
    f = float(np.median([v["f_idiossincratica_gt50"] for v in var]))
    res["mde_reescalado_pp"] = {
        "f_mediana": f,
        "h1a_evasao": 0.80 / np.sqrt(f),
        "h2_evasao_A": 4.65 / np.sqrt(f),
        "h2_evasao_B": 5.34 / np.sqrt(f),
        "h2_conclusao_A": 4.27 / np.sqrt(f),
        "h2_conclusao_B": 3.18 / np.sqrt(f),
    }
    with open(out_json, "w") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2, default=float)
    print(json.dumps(res, ensure_ascii=False, indent=1, default=float))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "verificacao.json")
