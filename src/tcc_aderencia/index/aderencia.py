"""Índice de aderência curso × território × ano (spec 03, variante A1/A2)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def axis_employment_share(employment: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    """Share of each territory's jobs linked to each CNCT axis (variant A1).

    employment: columns ``territorio, cnae_subclasse, ano, vinculos``
    mapping: columns ``cnae_subclasse, eixo, peso`` (weights sum to 1 per subclass
        among mapped subclasses; unmapped subclasses still count in the denominator)
    Returns columns ``territorio, ano, eixo, aderencia``.
    """
    total = (
        employment.groupby(["territorio", "ano"], as_index=False)["vinculos"]
        .sum()
        .rename(columns={"vinculos": "total"})
    )
    merged = employment.merge(mapping, on="cnae_subclasse", how="inner")
    merged["vinc_eixo"] = merged["vinculos"] * merged["peso"]
    by_axis = merged.groupby(["territorio", "ano", "eixo"], as_index=False)["vinc_eixo"].sum()
    out = by_axis.merge(total, on=["territorio", "ano"])
    out["aderencia"] = out["vinc_eixo"] / out["total"]
    return out[["territorio", "ano", "eixo", "aderencia"]]


def location_quotient(
    shares: pd.DataFrame, employment: pd.DataFrame, mapping: pd.DataFrame
) -> pd.DataFrame:
    """Variant A2: territory share divided by the national share of the same axis."""
    national = employment.assign(territorio="BR")
    br = axis_employment_share(national, mapping).rename(columns={"aderencia": "aderencia_br"})
    out = shares.merge(br[["ano", "eixo", "aderencia_br"]], on=["ano", "eixo"], how="left")
    out["ql"] = out["aderencia"] / out["aderencia_br"]
    return out.drop(columns="aderencia_br")


def attach_to_offers(offers: pd.DataFrame, shares: pd.DataFrame) -> pd.DataFrame:
    """Join axis shares to offers (``oferta_id, territorio, ano, eixo``); missing → 0."""
    out = offers.merge(shares, on=["territorio", "ano", "eixo"], how="left")
    out["aderencia"] = out["aderencia"].fillna(0.0)
    return out


# --- Spec 03 v2: Q, S and B per enrollment cycle --------------------------------------------

EMPLOYMENT = "emprego_rgi_subclasse.parquet"


def territory_employment(years, level: str = "cod_rgi") -> pd.DataFrame:
    """E(r, s, t): RAIS jobs by territory (IBGE `level` column of the RGI table), CNAE 2.3
    subclass (harmonized) and year. Columns territorio, ano, cnae_subclasse, vinculos."""
    import duckdb

    from tcc_aderencia.config import DATA, INTERIM
    from tcc_aderencia.ingest.cnae import harmonize

    rgi = pd.read_csv(DATA / "external" / "ibge_municipios_rgi.csv", dtype=str)
    rgi["mun6"] = rgi.cod_mun7.str[:6]
    con = duckdb.connect()
    con.register("rgi", rgi[["mun6", level]].rename(columns={level: "territorio"}))
    out = []
    for y in years:
        e = con.execute(
            f"""select r.territorio, cast(e.ano as int) ano, e.cnae_subclasse,
                       sum(e.vinculos)::double vinculos
                from read_parquet('{INTERIM}/rais/{y}/*.parquet') e
                join rgi r on r.mun6 = e.mun6
                group by all"""
        ).df()
        e = harmonize(e).groupby(["territorio", "ano", "cnae_subclasse"], as_index=False)
        out.append(e.vinculos.sum())
    return pd.concat(out, ignore_index=True)


def linked_employment(emp: pd.DataFrame, w: pd.DataFrame) -> pd.DataFrame:
    """L(r,c,t) = Σ_s w(s,c)·E(r,s,t), P = L / Σ_s E(r,s,t) and the location quotient
    QL = P(r,c,t) / P(Brasil,c,t).

    emp: territorio, ano, cnae_subclasse, vinculos. w: cnae_subclasse, unidade, w (unidade is a
    course or an axis). Returns territorio, ano, unidade, L, total, P, QL (only L > 0 cells;
    a missing cell means L = 0).
    """
    import duckdb

    con = duckdb.connect()
    con.register("e", emp)
    con.register("w", w[["cnae_subclasse", "unidade", "w"]])
    return con.execute(
        """
        with tot as (select territorio, ano, sum(vinculos) total from e group by all),
             l as (select e.territorio, e.ano, w.unidade, sum(w.w * e.vinculos) L
                   from e join w using (cnae_subclasse) group by all having sum(w.w * e.vinculos) > 0),
             br as (select l.ano, l.unidade, sum(L) / any_value(t.total) p_br
                    from l join (select ano, sum(total) total from tot group by ano) t using (ano)
                    group by all)
        select l.territorio, l.ano, l.unidade, l.L, tot.total, l.L / tot.total P,
               (l.L / tot.total) / br.p_br QL
        from l join tot using (territorio, ano) join br using (ano, unidade)
        """
    ).df()


def shift_share(emp: pd.DataFrame, w: pd.DataFrame, cells: pd.DataFrame) -> pd.DataFrame:
    """Bartik predictor of S per (territorio, unidade, t0, t1):

    B = Σ_s z(r,c,s) · g₋ᵣ(s, t0→t1), with z = w(s,c)·E(r,s,t0−1) / Σ_s' w(s',c)·E(r,s',t0−1)
    (subclass shares of the course-linked jobs in the base year) and
    g₋ᵣ = ln E₋ᵣ(s,t1) − ln E₋ᵣ(s,t0) (national growth leaving territory r out). Subclasses with
    E₋ᵣ = 0 at t0 or t1 are dropped and z renormalized. See ADR-0005.
    """
    import duckdb

    con = duckdb.connect()
    con.register("e", emp)
    con.register("w", w[["cnae_subclasse", "unidade", "w"]])
    con.register("cells", cells[["territorio", "unidade", "t0", "t1"]].drop_duplicates())
    return con.execute(
        """
        with nat as (select ano, cnae_subclasse, sum(vinculos) v from e group by all),
             z as (select c.territorio, c.unidade, c.t0, c.t1, e.cnae_subclasse,
                          w.w * e.vinculos zw
                   from cells c
                   join w on w.unidade = c.unidade
                   join e on e.territorio = c.territorio and e.cnae_subclasse = w.cnae_subclasse
                         and e.ano = c.t0 - 1),
             g as (select z.*,
                          n0.v - coalesce(e0.vinculos, 0) m0, n1.v - coalesce(e1.vinculos, 0) m1
                   from z
                   join nat n0 on n0.cnae_subclasse = z.cnae_subclasse and n0.ano = z.t0
                   join nat n1 on n1.cnae_subclasse = z.cnae_subclasse and n1.ano = z.t1
                   left join e e0 on e0.territorio = z.territorio
                        and e0.cnae_subclasse = z.cnae_subclasse and e0.ano = z.t0
                   left join e e1 on e1.territorio = z.territorio
                        and e1.cnae_subclasse = z.cnae_subclasse and e1.ano = z.t1)
        select territorio, unidade, t0, t1, sum(zw * (ln(m1) - ln(m0))) / sum(zw) B
        from g where m0 > 0 and m1 > 0
        group by all
        """
    ).df()


def cycle_indices(cycles: pd.DataFrame, emp: pd.DataFrame, w: pd.DataFrame, unit: str):
    """Q, S, B and log P for each cycle. cycles: territorio, `unit` (course or axis column),
    t0, t1. Q = ln QL(r,c,t0−1); S = ln L(r,c,t1) − ln L(r,c,t0); NaN where L = 0 or the
    year is outside the RAIS range."""
    lk = linked_employment(emp, w)
    c = cycles.rename(columns={unit: "unidade"})
    base = lk.rename(columns={"ano": "t_base"})
    out = c.assign(t_base=c.t0 - 1).merge(
        base[["territorio", "unidade", "t_base", "QL", "P", "L"]],
        on=["territorio", "unidade", "t_base"],
        how="left",
    )
    years = set(emp.ano)
    full = out.t_base.isin(years)
    out.loc[full, "L"] = out.loc[full, "L"].fillna(0.0)
    l0 = lk.rename(columns={"ano": "t0", "L": "L0"})[["territorio", "unidade", "t0", "L0"]]
    l1 = lk.rename(columns={"ano": "t1", "L": "L1"})[["territorio", "unidade", "t1", "L1"]]
    out = out.merge(l0, how="left").merge(l1, how="left")
    out["Q"] = np.log(out.QL)
    out["lnP"] = np.log(out.P)
    s_ok = out.t0.isin(years) & out.t1.isin(years)
    out["S"] = np.where(s_ok, np.log(out.L1) - np.log(out.L0), np.nan)
    b = shift_share(emp, w, out[s_ok & out.t_base.isin(years)])
    out = out.merge(b, on=["territorio", "unidade", "t0", "t1"], how="left")
    return out.rename(columns={"unidade": unit}).drop(columns=["L0", "L1"])
