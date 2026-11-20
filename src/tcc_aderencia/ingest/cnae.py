"""CNAE harmonization: RAIS subclasses from CNAE 2.0/2.1/2.2 → CNAE 2.3 (P17).

RAIS 2012–2017 (and a few later files) still carry 24 subclasses that were split or moved in
CNAE 2.1–2.3. Each old code maps to its 2.3 successors by meaning (`SUCCESSORS`, curated from the
subclass names; to be checked against IBGE's correspondence tables, liv101721 §4.2). Jobs are
split across successors in proportion to their national employment in `WEIGHT_YEAR`, the first
year fully coded in 2.3. Codes 9999997/9999999 ("ignorado") have no successor and are dropped.
"""

from __future__ import annotations

import duckdb
import pandas as pd

from tcc_aderencia.config import INTERIM, REFERENCE

CORRESPONDENCE = REFERENCE / "cnae_correspondencia_23.csv"
WEIGHT_YEAR = 2018
IGNORED = ("9999997", "9999999")

SUCCESSORS: dict[str, tuple[tuple[str, ...], str]] = {
    "1091100": (("1091101", "1091102"), "divisão 2.2"),
    "1610201": (("1610203",), "renumeração 2.2"),
    "1610202": (("1610204",), "renumeração 2.2"),
    "1822900": (("1822901", "1822999"), "divisão 2.2"),
    "2013400": (("2013401", "2013402"), "divisão 2.2"),
    "2539000": (("2539001", "2539002"), "divisão 2.2"),
    "3511500": (("3511501", "3511502"), "divisão 2.2"),
    "4541205": (("4541206", "4541207"), "divisão 2.2 (peças novas × usadas)"),
    "4713001": (("4713004",), "renumeração 2.1 (lojas de departamentos)"),
    "4713003": (("4713005",), "renumeração 2.1 (duty free)"),
    "4721101": (("1091102",), "padaria com produção própria vai para a indústria (2.2)"),
    "4751200": (("4751201", "4751202"), "divisão 2.1"),
    "5239700": (("5239701", "5239799"), "divisão 2.2"),
    "5611202": (("5611204", "5611205"), "divisão 2.2 (bares com × sem entretenimento)"),
    "5812300": (("5812301", "5812302"), "divisão 2.2"),
    "5822100": (("5822101", "5822102"), "divisão 2.2"),
    "6201500": (("6201501", "6201502"), "divisão 2.1"),
    "7410201": (("7410202", "7410203", "7410299"), "divisão 2.1 (design)"),
    "8020000": (("8020001", "8020002"), "divisão 2.1"),
    "8630505": ((), "a conferir: repartido pela classe 86305 inteira"),
    "9412000": (("9412001", "9412099"), "divisão 2.1"),
    "9609203": (("9609207", "9609208"), "divisão 2.2 (alojamento × higiene de animais)"),
}


def build_correspondence(subclasses_23: pd.Series) -> pd.DataFrame:
    """Rows (cnae_origem, cnae_23, peso, regra) with weights summing to 1 per origin."""
    valid = set(subclasses_23)
    w = (
        duckdb.sql(
            f"""select cnae_subclasse, sum(vinculos) v
                from '{INTERIM}/rais/{WEIGHT_YEAR}/*.parquet' group by 1"""
        )
        .df()
        .set_index("cnae_subclasse")["v"]
    )
    rows = []
    for old, (succ, rule) in SUCCESSORS.items():
        if not succ:  # class-level fallback
            succ = tuple(s for s in sorted(valid) if s[:5] == old[:5])
        missing = set(succ) - valid
        if missing:
            raise ValueError(f"{old}: successors not in CNAE 2.3: {missing}")
        v = pd.Series({s: float(w.get(s, 0.0)) for s in succ})
        v = v / v.sum() if v.sum() > 0 else pd.Series(1 / len(succ), index=v.index)
        rows += [(old, s, p, rule) for s, p in v.items()]
    return pd.DataFrame(rows, columns=["cnae_origem", "cnae_23", "peso", "regra"])


def load_correspondence() -> pd.DataFrame:
    return pd.read_csv(CORRESPONDENCE, dtype={"cnae_origem": str, "cnae_23": str})


def harmonize(df: pd.DataFrame, corr: pd.DataFrame | None = None, value: str = "vinculos"):
    """Recode `cnae_subclasse` to CNAE 2.3, splitting `value` by the correspondence weights.

    Codes not in the correspondence pass through; "ignorado" codes are dropped.
    """
    corr = load_correspondence() if corr is None else corr
    df = df[~df.cnae_subclasse.isin(IGNORED)]
    hit = df.cnae_subclasse.isin(corr.cnae_origem)
    split = df[hit].merge(corr, left_on="cnae_subclasse", right_on="cnae_origem")
    split[value] = split[value] * split["peso"]
    split["cnae_subclasse"] = split["cnae_23"]
    split = split[df.columns]
    return pd.concat([df[~hit], split], ignore_index=True)
