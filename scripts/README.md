# Scripts do pipeline

Ordem prevista: `ingest_*.py` → `build_territory_structure.py` → `classify_cnae.py` → `evaluate_classifier.py` → `build_index.py` → (pré-registro) → `run_models.py`.

## Disponíveis
- `verify_data.py`: verificação descritiva de viabilidade com a RAIS agregada (`data/interim/rais/`) e a PNP. Mede qualidade das chaves, totais contra o estoque oficial, ponte CBO, variação e estabilidade de Q (mapa O), cobertura PNP × Q e reescala o MDE. Não estima modelo de efeito. Uso: `python scripts/verify_data.py saida.json`.
- `sample_reference.py`: sorteia a amostra de referência (300 subclasses, seção × faixa de emprego, divisão dev/teste) em `data/reference/gold_v1.csv` e gera as planilhas `annotation/anotacao_avaliador_{A,B}.xlsx`. Reproduzível (seed do projeto).
- `evaluate_test.py`: avaliação **única** do classificador T no split de teste da referência (marco G2): TF-IDF, embeddings, caminho O, cada LLM e a regra combinada (`llm.combine`, fixada no dev), com macro-F1 e IC por bootstrap, alfa inter-LLM e convergência T × O. Monta `data/processed/map_cnae_curso.parquet`. Exige os `map_t_llm_*.parquet` já gerados. Resultado em `docs/resultados/avaliacao-classificador-t.json`.
