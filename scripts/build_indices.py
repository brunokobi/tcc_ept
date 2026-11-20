"""Índices de aderência por ciclo da PNP (spec 03): Q, S, B e variantes R1, R2, R3, R5.

Descritivo: não estima modelo de efeito (permitido antes do pré-registro).

Uso: python scripts/build_indices.py
Saídas: data/processed/indices.parquet, data/processed/emprego_{rgi,rgint}_subclasse.parquet
(cache) e docs/resultados/indices.json (cobertura, distribuição e convergência T × O).
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from tcc_aderencia.config import DATA, PROCESSED, ROOT
from tcc_aderencia.index.aderencia import cycle_indices, linked_employment, territory_employment

YEARS = range(2012, 2026)
OUT = ROOT / "docs" / "resultados" / "indices.json"


def employment(level: str) -> pd.DataFrame:
    path = PROCESSED / f"emprego_{level.removeprefix('cod_')}_subclasse.parquet"
    if not path.exists():
        territory_employment(YEARS, level).to_parquet(path)
    return pd.read_parquet(path)


def weights() -> dict[str, pd.DataFrame]:
    m = pd.read_parquet(PROCESSED / "map_cnae_curso.parquet")
    t = m[m.w_T > 0]
    o = m[m.w_O > 0]
    return {
        "T": t.rename(columns={"curso": "unidade", "w_T": "w"}),
        "O": o.rename(columns={"curso": "unidade", "w_O": "w"}),
        "T_eixo": t.groupby(["cnae_subclasse", "eixo"], as_index=False)
        .w_T.sum()
        .rename(columns={"eixo": "unidade", "w_T": "w"}),
    }


def cycles() -> pd.DataFrame:
    p = pd.read_parquet(PROCESSED / "pnp_ciclos.parquet")
    p = p[p.curso_cnct.notna()].copy()
    rgi = pd.read_csv(DATA / "external" / "ibge_municipios_rgi.csv", dtype=str)
    p["territorio_rgint"] = p.cod_mun7.map(dict(zip(rgi.cod_mun7, rgi.cod_rgint, strict=True)))
    p["oferta_id"] = p.campus + "|" + p.curso_cnct + "|" + p.ead.map({True: "EaD", False: "P"})
    p["t0"] = p.inicio.dt.year
    p["t1"] = p.fim_previsto.dt.year
    p = p.rename(columns={"curso": "curso_pnp"})
    return p.rename(columns={"ciclo": "ciclo_id", "curso_cnct": "curso"})


def spearman(a: pd.Series, b: pd.Series) -> dict:
    ok = a.notna() & b.notna() & np.isfinite(a) & np.isfinite(b)
    return {"rho": round(float(spearmanr(a[ok], b[ok]).statistic), 4), "n": int(ok.sum())}


def main() -> None:
    e_rgi, e_rgint = employment("cod_rgi"), employment("cod_rgint")
    w = weights()
    c = cycles()
    keys = ["edicao", "ciclo_id"]
    base = c[keys + ["oferta_id", "campus", "territorio", "territorio_rgint", "curso",
                     "eixo_cnct", "ead", "tipo_oferta", "t0", "t1", "matriculas", "evasao",
                     "conclusao"]]

    t = cycle_indices(base, e_rgi, w["T"], "curso")
    o = cycle_indices(base[keys + ["territorio", "curso", "t0", "t1"]], e_rgi, w["O"], "curso")
    ax = cycle_indices(
        base[keys + ["territorio", "eixo_cnct", "t0", "t1"]], e_rgi, w["T_eixo"], "eixo_cnct"
    )
    r5 = cycle_indices(
        base[keys + ["territorio_rgint", "curso", "t0", "t1"]].rename(
            columns={"territorio_rgint": "territorio"}
        ),
        e_rgint,
        w["T"],
        "curso",
    )
    idx = t.merge(o[keys + ["Q", "S"]].rename(columns={"Q": "R2", "S": "R2_S"}), on=keys)
    idx = idx.merge(ax[keys + ["Q"]].rename(columns={"Q": "R3"}), on=keys)
    idx = idx.merge(r5[keys + ["Q"]].rename(columns={"Q": "R5"}), on=keys)
    idx = idx.rename(columns={"lnP": "R1", "eixo_cnct": "eixo"})
    idx.to_parquet(PROCESSED / "indices.parquet")

    # Convergence T × O on territory × course cells (one base year) and on cycles
    yr = 2018
    lt = linked_employment(e_rgi[e_rgi.ano == yr], w["T"])
    lo = linked_employment(e_rgi[e_rgi.ano == yr], w["O"])
    cells = lt.merge(lo, on=["territorio", "unidade"], suffixes=("_T", "_O"))
    offered = cells.merge(
        idx[["territorio", "curso"]].drop_duplicates().rename(columns={"curso": "unidade"})
    )
    by_course = cells.groupby("unidade").apply(
        lambda d: spearmanr(d.QL_T, d.QL_O).statistic if len(d) > 9 else np.nan,
        include_groups=False,
    )

    valid = idx.Q.notna()
    out = {
        "ciclos": len(idx),
        "ciclos_ead": int(idx.ead.sum()),
        "cobertura": {
            "Q": round(float(valid.mean()), 4),
            "S": round(float(idx.S.notna().mean()), 4),
            "B": round(float(idx.B.notna().mean()), 4),
            "R2_caminho_O": round(float(idx.R2.notna().mean()), 4),
            "R3_eixo": round(float(idx.R3.notna().mean()), 4),
            "R5_rgint": round(float(idx.R5.notna().mean()), 4),
            "Q_nan_por_motivo": {
                "ano_base_fora_da_rais": int((~idx.t_base.isin(YEARS)).sum()),
                "L_zero_no_territorio": int((idx.L == 0).sum()),
            },
        },
        "distribuicao": {
            k: {q: round(float(v), 4) for q, v in idx[k].describe().items() if q != "count"}
            for k in ["Q", "S", "B", "R1", "R2", "R3", "R5"]
        },
        "convergencia_T_O": {
            "ciclos_Q_T_x_Q_O": spearman(idx.Q, idx.R2),
            "ciclos_S_T_x_S_O": spearman(idx.S, idx.R2_S),
            f"celulas_{yr}_QL_T_x_QL_O": spearman(cells.QL_T, cells.QL_O),
            f"celulas_ofertadas_{yr}": spearman(offered.QL_T, offered.QL_O),
            f"mediana_por_curso_{yr}": round(float(by_course.median()), 4),
            "cursos": int(by_course.notna().sum()),
        },
        "robustez_Q": {
            "Q_x_R1_participacao": spearman(idx.Q, idx.R1),
            "Q_x_R3_eixo": spearman(idx.Q, idx.R3),
            "Q_x_R5_rgint": spearman(idx.Q, idx.R5),
        },
        "primeiro_estagio_descritivo_S_x_B": spearman(idx.S, idx.B),
        "sentinelas": {
            "Agropecuaria_Q_medio_por_tercil_de_emprego_agro": None,
        },
    }
    # Sentinel: Agropecuária Q is higher where agriculture is a larger share of jobs
    agro = e_rgi[(e_rgi.ano == yr)].assign(a=lambda d: d.cnae_subclasse.str[:2].isin(["01", "02"]))
    sh = agro.groupby("territorio").apply(
        lambda d: d.vinculos[d.a].sum() / d.vinculos.sum(), include_groups=False
    )
    qa = lt[lt.unidade == "Técnico em Agropecuária"].set_index("territorio").QL
    terc = pd.qcut(sh.reindex(qa.index), 3, labels=["baixo", "medio", "alto"])
    out["sentinelas"]["Agropecuaria_Q_medio_por_tercil_de_emprego_agro"] = {
        str(k): round(float(v), 3) for k, v in np.log(qa).groupby(terc, observed=True).mean().items()
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
