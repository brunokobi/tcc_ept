# Scripts do pipeline

Ordem prevista: `ingest_*.py` → `build_territory_structure.py` → `classify_cnae.py` → `evaluate_classifier.py` → `build_index.py` → (pré-registro) → `run_models.py`.

## Disponíveis
- `verify_data.py`: verificação descritiva de viabilidade com a RAIS agregada (`data/interim/rais/`) e a PNP. Mede qualidade das chaves, totais contra o estoque oficial, ponte CBO, variação e estabilidade de Q (mapa O), cobertura PNP × Q e reescala o MDE. Não estima modelo de efeito. Uso: `python scripts/verify_data.py saida.json`.
