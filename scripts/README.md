# Scripts do pipeline

Ordem do pipeline:

1. Ingestão: `python -m tcc_aderencia.ingest.rais <ano>` (2012–2025); PNP, CNCT, CNAE e IBGE pelas funções de `tcc_aderencia.ingest` (ver `data/README.md`).
2. `verify_data.py` (viabilidade, descritivo).
3. `sample_reference.py` (amostra de referência) → anotação (ADR-0004).
4. Classificador T: funções de `tcc_aderencia.classifier` (baseline, embeddings, `llm.classify`) e caminho O (`classifier.occupations`), que gravam os `map_t_*` e `map_w_o` em `data/processed/`.
5. `evaluate_test.py` → `run_course_weights.py` → `build_indices.py`.
6. `make_figures.py` (figuras descritivas e dados da página do orientador).
7. `search_literature.py` (revisão sistemática, independente do resto).
8. **Só depois do pré-registro no OSF:** modelos de efeito (`tcc_aderencia.models`, ainda sem script).

## Disponíveis
- `verify_data.py`: verificação descritiva de viabilidade com a RAIS agregada (`data/interim/rais/`) e a PNP. Mede qualidade das chaves, totais contra o estoque oficial, ponte CBO, variação e estabilidade de Q (mapa O), cobertura PNP × Q e reescala o MDE. Não estima modelo de efeito. Uso: `python scripts/verify_data.py saida.json`.
- `sample_reference.py`: sorteia a amostra de referência (300 subclasses, seção × faixa de emprego, divisão dev/teste) em `data/reference/gold_v1.csv` e gera as planilhas `annotation/anotacao_avaliador_{A,B}.xlsx`. Reproduzível (seed do projeto).
- `evaluate_test.py`: avaliação **única** do classificador T no split de teste da referência (marco G2): TF-IDF, embeddings, caminho O, cada LLM e a regra combinada (`llm.combine`, fixada no dev), com macro-F1 e IC por bootstrap, alfa inter-LLM e convergência T × O. Monta a primeira versão de `data/processed/map_cnae_curso.parquet` (reescrita depois por `run_course_weights.py`; ordem: `evaluate_test.py` → `run_course_weights.py` → `build_indices.py`). Exige os `map_t_llm_*.parquet` já gerados. Resultado em `docs/resultados/avaliacao-classificador-t.json`.
- `build_indices.py`: índices de aderência por ciclo da PNP (spec 03, ADR-0005): Q, S, B e variantes R1 (participação), R2 (caminho O), R3 (eixo) e R5 (região intermediária). Gera `data/processed/indices.parquet`, os caches `emprego_{rgi,rgint}_subclasse.parquet` e `docs/resultados/indices.json` (cobertura, distribuição, convergência T × O, sentinela). Descritivo, sem desfechos.
- `run_course_weights.py`: segunda passada do LLM (ADR-0005, P20): pesos de todos os cursos ligados a cada subclasse, mantendo o eixo do G2; reconstrói `map_cnae_curso.parquet`. Exige `OPENROUTER_API_KEY` no ambiente. Depois, rodar `build_indices.py`.
- `search_literature.py`: busca reproduzível da revisão sistemática na OpenAlex (4 strings, título + resumo, 2008+); grava os registros em `docs/revisao/busca/`. A triagem fica em `docs/revisao/triagem.csv` e a síntese em `docs/revisao/sintese.md`.
- `make_figures.py`: figuras descritivas para o artigo (`reports/figures/fig*.png|svg`: classificador, F1 por eixo, mapa do Q, convergência T × O, distribuições de Q/S/B, sentinela Agropecuária, PRISMA) e `reports/figures/pagina_dados.json`, que alimenta a página `reports/pagina/index.html` (publicada, lê `dados.json` ao lado). Gera também `reports/pagina/pagina_offline.html`, com os dados embutidos, para abrir direto do disco. Descarta evasão e conclusão ao carregar o painel (regra do pré-registro). Exige o extra `figures` (`pip install -e ".[figures]"`); baixa a malha de regiões imediatas do IBGE na primeira execução.
