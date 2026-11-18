# Spec 02 — Mapeamento CNAE → CNCT (v2)

## Objetivo
Pesos `w(s,c)` de cada subclasse CNAE *s* (1.332) para cada curso *c* (189 civis; 13 eixos), por **dois caminhos independentes**, e validação cruzada.

## Insumos (prospecção, ver `docs/prospeccao/relatorio-viabilidade.md`)
- `data/external/cnct4_cursos.csv`: 212 cursos (189 civis), campos `perfil`, `campo_atuacao`, `cbo_codes`, `ead` (permitido/vedado/não informado). 163 dos 189 civis têm CBO (média ≈ 2,4 códigos).
- `data/external/cnae_subclasses.csv`: 1.332 subclasses com `atividades` e `observacoes` (compreende / não compreende).

## Caminho T — texto com IA
1. **Baseline** (`classifier/baseline.py`): TF-IDF de descrição+notas CNAE × perfil+campo do curso.
2. **Embeddings** (`classifier/embeddings.py`): modelo multilíngue; texto CNAE = descrição + atividades + "compreende"; texto curso = nome + perfil + campo de atuação; top-k por cosseno.
3. **LLM** (`classifier/llm.py`): para `top1 < τ` ou `top1 − top2 < δ`; candidatos top-k; JSON `{eixo, cursos, peso, justificativa}`; temperatura 0; cache por hash; **2 provedores** para concordância.

## Caminho O — ocupações (CBO) via RAIS
`w_O(s,c) = Σ_{o ∈ CBO(c)} V(s,o) / Σ_o V(s,o)` com `V(s,o)` = vínculos nacionais na subclasse *s* e ocupação *o* (média de anos). Ou seja: que fração dos empregos da subclasse está nas ocupações do curso. Cursos sem CBO (26 civis) ficam só com o caminho T.

## Validação
- **Amostra de referência:** ~300 subclasses, estratificada por seção CNAE e por peso no emprego; **dois avaliadores** (pesquisador + segundo avaliador indicado pelo orientador) anotam eixo principal e secundários; o pesquisador reanota 20% após ≥ 4 semanas.
- **Concordância:** alfa de Krippendorff inter e intra-avaliador; divergências resolvidas por consenso → gold.
- **Split dev/teste** (seed fixa) antes de qualquer ajuste.
- **Métricas:** precisão, revocação e F1 por eixo (macro/micro) com IC por bootstrap: baseline × embeddings × embeddings+LLM × caminho O.
- **Convergência T × O:** correlação de Spearman entre `w_T` e `w_O` por curso; correlação entre os índices `Q` resultantes.
- **Critério de sucesso:** macro-F1 (T) > baseline com IC sem sobreposição; resultados principais estáveis entre T e O.

## Saída
`data/processed/map_cnae_curso.parquet`: `cnae_subclasse, curso, eixo, w_T, w_O, metodo_T, confianca_T, justificativa_T, cnct_edicao`.
