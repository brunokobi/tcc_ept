"""Segunda passada do LLM (ADR-0005, P20): pesos de TODOS os cursos ligados a cada subclasse.

Mantém o eixo principal avaliado no G2 (`map_t_llm_final.parquet`) e reconstrói o mapa
`data/processed/map_cnae_curso.parquet` com w_T multicurso. Depois rode
`python scripts/build_indices.py`.

Uso: OPENROUTER_API_KEY=... python scripts/run_course_weights.py
(a chave nunca vai para o repositório; respostas ficam em .cache/llm e o script retoma de onde parou)
"""

from __future__ import annotations

import pandas as pd

from tcc_aderencia.classifier import llm
from tcc_aderencia.classifier.texts import comprises
from tcc_aderencia.config import DATA, PROCESSED


def main() -> None:
    cnct = pd.read_csv(DATA / "external" / "cnct4_cursos.csv")
    cn = pd.read_csv(DATA / "external" / "cnae_subclasses.csv", dtype=str)
    cn = cn.assign(compreende=cn.observacoes.map(comprises))[
        ["cnae_subclasse", "descricao", "compreende"]
    ].sort_values("cnae_subclasse")
    final = pd.read_parquet(PROCESSED / "map_t_llm_final.parquet")

    w = llm.course_weights(cn, final, llm.PRIMARY, cnct)
    w.to_parquet(PROCESSED / "map_t_llm_cursos.parquet")

    f = final.set_index("cnae_subclasse")
    old = pd.read_parquet(PROCESSED / "map_cnae_curso.parquet")
    just = old.dropna(subset=["justificativa_T"]).drop_duplicates("cnae_subclasse")
    just = just.set_index("cnae_subclasse").justificativa_T
    t = w.assign(
        metodo_T="llm_multicurso",
        confianca_T=w.cnae_subclasse.map(f.consenso).map({True: 1.0, False: 0.5}),
        justificativa_T=w.cnae_subclasse.map(just),
    ).drop(columns="modelo")
    o = old[old.w_O > 0][["cnae_subclasse", "curso", "eixo", "w_O"]]
    m = t.merge(o, on=["cnae_subclasse", "curso", "eixo"], how="outer")
    m[["w_T", "w_O"]] = m[["w_T", "w_O"]].fillna(0.0)
    m = m.assign(cnct_edicao=4)[old.columns]
    m.to_parquet(PROCESSED / "map_cnae_curso.parquet")

    print(
        f"subclasses com w_T: {w.cnae_subclasse.nunique()}; cursos com alguma subclasse: "
        f"{w.curso.nunique()}; cursos por subclasse (média): "
        f"{w.groupby('cnae_subclasse').size().mean():.2f}"
    )


if __name__ == "__main__":
    main()
