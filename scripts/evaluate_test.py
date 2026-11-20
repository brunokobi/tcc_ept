"""Avaliação ÚNICA do classificador T no split de teste da referência (spec 02, marco G2).

Regra de decisão (`llm.combine`) fixada no dev antes de rodar este script. Também monta o mapa
final `data/processed/map_cnae_curso.parquet` (w_T do LLM + w_O do caminho O).

Uso: python scripts/evaluate_test.py
Saída: docs/resultados/avaliacao-classificador-t.json e o mapa em data/processed/.
"""

from __future__ import annotations

import json

import pandas as pd
from scipy.stats import spearmanr

from tcc_aderencia.classifier import llm
from tcc_aderencia.classifier.evaluate import (
    NAO_SE_APLICA,
    bootstrap_f1,
    inter_llm_agreement,
    per_axis_metrics,
)
from tcc_aderencia.config import DATA, PROCESSED, REFERENCE, ROOT
from tcc_aderencia.ingest.pnp import norm_course

OUT = ROOT / "docs" / "resultados" / "avaliacao-classificador-t.json"
MISSING = "(sem predição)"


def axis_from_o(w_o: pd.DataFrame) -> pd.DataFrame:
    """Path O as a classifier: axis with the largest summed w_O; no weight → não se aplica."""
    s = w_o.groupby(["cnae_subclasse", "eixo"]).w_O.sum().reset_index()
    s = s[s.w_O > 0].sort_values("w_O", ascending=False).drop_duplicates("cnae_subclasse")
    return s[["cnae_subclasse", "eixo"]].rename(columns={"eixo": "eixo_pred"})


def evaluate(gold: pd.DataFrame, pred: pd.DataFrame) -> dict:
    p = gold[["cnae_subclasse"]].merge(pred[["cnae_subclasse", "eixo_pred"]], how="left")
    p["eixo_pred"] = p.eixo_pred.fillna(MISSING)  # missing prediction counts as an error
    t = per_axis_metrics(gold, p)
    f1, lo, hi = bootstrap_f1(gold, p)
    return {
        "acuracia": round(float(t.loc[t.eixo == "micro", "f1"].iat[0]), 4),
        "macro_f1": round(f1, 4),
        "ic95": [round(lo, 4), round(hi, 4)],
        "n": len(p),
    }


def build_map(final: pd.DataFrame, preds: dict, cnct: pd.DataFrame, w_o: pd.DataFrame):
    """w_T: equal weights over the courses the deciding model listed, within the final axis."""
    civil = cnct[cnct.eixo != "Militar"]
    lookup = {norm_course(c): (c, e) for c, e in zip(civil.curso, civil.eixo, strict=True)}
    rows = []
    for r in final.itertuples():
        if pd.isna(r.eixo_pred) or r.eixo_pred == NAO_SE_APLICA:
            continue
        src = preds[llm.PRIMARY] if r.decisor == llm.PRIMARY else preds[r.decisor]
        hit = src[src.cnae_subclasse == r.cnae_subclasse]
        cursos = list(hit.cursos.iat[0]) if len(hit) and hit.cursos.iat[0] is not None else []
        just = hit.justificativa.iat[0] if len(hit) else ""
        found = {lookup[k] for k in map(norm_course, cursos) if k in lookup}
        found = [c for c, e in found if e == r.eixo_pred]
        for c in found:
            rows.append(
                {
                    "cnae_subclasse": r.cnae_subclasse,
                    "curso": c,
                    "eixo": r.eixo_pred,
                    "w_T": 1 / len(found),
                    "metodo_T": "llm_consenso" if r.consenso else "llm_primario",
                    "confianca_T": 1.0 if r.consenso else 0.5,
                    "justificativa_T": just,
                }
            )
    t = pd.DataFrame(rows)
    o = w_o[["cnae_subclasse", "curso", "eixo", "w_O"]]
    m = t.merge(o, on=["cnae_subclasse", "curso", "eixo"], how="outer")
    m["w_T"] = m.w_T.fillna(0.0)
    m["w_O"] = m.w_O.fillna(0.0)
    return m.assign(cnct_edicao=4)[
        ["cnae_subclasse", "curso", "eixo", "w_T", "w_O", "metodo_T", "confianca_T",
         "justificativa_T", "cnct_edicao"]
    ]


def main() -> None:
    gold_all = pd.read_csv(REFERENCE / "gold_v1.csv", dtype={"cnae_subclasse": str})
    gold = gold_all[gold_all.split == "teste"][["cnae_subclasse", "eixo_principal"]]
    cnct = pd.read_csv(DATA / "external" / "cnct4_cursos.csv")
    w_o = pd.read_parquet(PROCESSED / "map_w_o.parquet")

    preds = {
        m: pd.read_parquet(PROCESSED / f"map_t_llm_{m.split('/')[0]}.parquet")
        for m in llm.DEFAULT_MODELS
    }
    final = llm.combine(preds)
    wide = final.merge(
        preds[llm.PRIMARY][["cnae_subclasse", "eixo_pred"]].rename(columns={"eixo_pred": "p"}),
        how="left",
    )
    final["decisor"] = [
        llm.PRIMARY if pd.notna(p) else llm.DEFAULT_MODELS[1] for p in wide.p
    ]
    final.drop(columns="decisor").to_parquet(PROCESSED / "map_t_llm_final.parquet")

    methods = {
        "tfidf": pd.read_parquet(PROCESSED / "map_t_baseline_eixos.parquet"),
        "embeddings": pd.read_parquet(PROCESSED / "map_t_emb_eixos.parquet"),
        "caminho_O": axis_from_o(w_o),
        **{m: preds[m] for m in llm.DEFAULT_MODELS},
        "llm_final": final,
    }
    res = {k: evaluate(gold, v) for k, v in methods.items()}

    test_ids = set(gold.cnae_subclasse)
    labels = pd.DataFrame(
        {m: preds[m].set_index("cnae_subclasse").eixo_pred for m in llm.DEFAULT_MODELS}
    )
    lt = labels[labels.index.isin(test_ids)]
    g = gold.set_index("cnae_subclasse").eixo_principal
    ft = final.set_index("cnae_subclasse").loc[lambda d: d.index.isin(test_ids)]
    agree = ft.consenso
    acc = (ft.eixo_pred == g.reindex(ft.index))

    mp = build_map(final, preds, cnct, w_o)
    mp.to_parquet(PROCESSED / "map_cnae_curso.parquet")
    both = mp[(mp.w_T > 0) & mp.metodo_T.notna()]
    by_course = mp.groupby("curso").apply(
        lambda d: spearmanr(d.w_T, d.w_O).statistic if d.w_T.nunique() > 1 else float("nan"),
        include_groups=False,
    )

    base_hi = res["tfidf"]["ic95"][1]
    out = {
        "split": "teste",
        "n_teste": len(gold),
        "referencia": "LLM (ADR-0004), não gabarito humano",
        "regra": "consenso dos dois provedores; desacordo -> " + llm.PRIMARY,
        "metodos": res,
        "alfa_inter_llm_teste": round(inter_llm_agreement(lt), 4),
        "alfa_inter_llm_todas": round(inter_llm_agreement(labels), 4),
        "consenso_teste": {
            "n": int(agree.sum()),
            "acuracia_com_consenso": round(float(acc[agree].mean()), 4),
            "acuracia_sem_consenso": round(float(acc[~agree].mean()), 4),
        },
        "criterio_G2": {
            "llm_final_ic_inf": res["llm_final"]["ic95"][0],
            "tfidf_ic_sup": base_hi,
            "atingido": res["llm_final"]["ic95"][0] > base_hi,
        },
        "mapa": {
            "linhas": len(mp),
            "subclasses_com_w_T": int(both.cnae_subclasse.nunique()),
            "subclasses_nao_se_aplica": int((final.eixo_pred == NAO_SE_APLICA).sum()),
            "consenso_todas": round(float(final.consenso.mean()), 4),
            "spearman_wT_wO_mediana_por_curso": round(float(by_course.median()), 4),
            "cursos_com_spearman": int(by_course.notna().sum()),
        },
        "por_eixo_llm_final": per_axis_metrics(
            gold,
            gold[["cnae_subclasse"]].merge(final[["cnae_subclasse", "eixo_pred"]], how="left")
            .fillna({"eixo_pred": MISSING}),
        ).round(4).to_dict("records"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in out.items() if k != "por_eixo_llm_final"},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
