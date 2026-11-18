# ADR-0003 — Stack técnica

- **Status:** aceita
- **Data:** 2026-11-18

## Decisão
Python ≥ 3.11; pandas + DuckDB + Parquet; statsmodels / linearmodels (econometria); scikit-learn + SHAP; sentence-transformers (embeddings); LLMs via API (≥ 2 provedores para concordância); Streamlit + Plotly (painel); SDK `mcp` oficial (servidor MCP); pytest + ruff.

## Consequências
Tudo reprodutível por scripts em `scripts/`; notebooks só para exploração.
