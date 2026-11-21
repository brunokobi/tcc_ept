"""Busca reproduzível da revisão sistemática (docs/revisao/protocolo-revisao.md) na OpenAlex.

A OpenAlex indexa SciELO, periódicos da CAPES com DOI e boa parte dos repositórios institucionais.
Cada string roda em título + resumo, de 2008 em diante, e grava os registros brutos em
docs/revisao/busca/<id>.csv. Uso: python scripts/search_literature.py
"""

from __future__ import annotations

import time

import pandas as pd
import requests

from tcc_aderencia.config import ROOT

OUT = ROOT / "docs" / "revisao" / "busca"
API = "https://api.openalex.org/works"
MAX = 200  # one page per string, by relevance (deep paging needs an API key)

QUERIES = {
    "S1_pt_territorio_evasao_ept": (
        '(evasão OR permanência OR conclusão OR êxito OR "abandono escolar") AND '
        '("arranjo produtivo" OR "arranjos produtivos" OR território OR territorial OR '
        '"mercado de trabalho" OR "vocação regional" OR "desenvolvimento regional") AND '
        '("instituto federal" OR "educação profissional" OR "curso técnico" OR "cursos técnicos" '
        'OR "ensino técnico")'
    ),
    "S2_pt_ead_evasao_ept": (
        '(evasão OR permanência OR conclusão) AND ("educação a distância" OR EaD) AND '
        '("curso técnico" OR "cursos técnicos" OR "instituto federal" OR "educação profissional" '
        'OR "e-Tec")'
    ),
    "S3_en_vet_local_labor": (
        '(dropout OR attrition OR retention OR completion OR persistence) AND '
        '("vocational education" OR "technical education" OR "vocational training" OR TVET OR '
        '"career and technical education" OR "vocational school") AND '
        '("local labor market" OR "local labour market" OR "labor demand" OR "labour demand" OR '
        '"regional economy" OR "local industry" OR "skills mismatch" OR "industry structure" OR '
        '"field of study")'
    ),
    "S4_en_labor_shock_dropout": (
        '(dropout OR "school enrollment" OR "college enrollment" OR "educational attainment" OR '
        'completion) AND ("local labor demand" OR "local labour demand" OR "Bartik" OR '
        '"shift-share" OR "labor market shock" OR "labour market shock" OR "opportunity cost of '
        'schooling" OR "local employment shock")'
    ),
}


def abstract(inv: dict | None) -> str:
    if not inv:
        return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)


def search(q: str) -> list[dict]:
    rows = []
    r = requests.get(
        API,
        params={
            "filter": f"title_and_abstract.search:{q},from_publication_date:2008-01-01",
            "per_page": MAX,
            "sort": "relevance_score:desc",
            "select": "id,doi,display_name,publication_year,authorships,primary_location,"
            "abstract_inverted_index,type,language,cited_by_count",
        },
        timeout=120,
    )
    r.raise_for_status()
    j = r.json()
    for w in j["results"]:
        src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name")
        rows.append(
            {
                "openalex": w["id"],
                "doi": w.get("doi"),
                "titulo": w.get("display_name"),
                "ano": w.get("publication_year"),
                "autores": "; ".join(
                    a["author"]["display_name"] for a in (w.get("authorships") or [])[:6]
                ),
                "fonte": src,
                "tipo": w.get("type"),
                "idioma": w.get("language"),
                "citacoes": w.get("cited_by_count"),
                "resumo": abstract(w.get("abstract_inverted_index")),
                "total_base": j["meta"]["count"],
            }
        )
    time.sleep(1)
    return rows


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for k, q in QUERIES.items():
        d = pd.DataFrame(search(q))
        d.to_csv(OUT / f"{k}.csv", index=False)
        print(k, "total na base:", d.total_base.iat[0] if len(d) else 0, "baixados:", len(d))


if __name__ == "__main__":
    main()
