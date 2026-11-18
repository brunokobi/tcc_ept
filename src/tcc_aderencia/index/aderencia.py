"""Índice de aderência curso × território × ano (spec 03, variante A1/A2)."""

from __future__ import annotations

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


def location_quotient(shares: pd.DataFrame, employment: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
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
