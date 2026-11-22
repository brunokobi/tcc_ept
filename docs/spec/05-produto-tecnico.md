# Spec 05 — Produto técnico: painel, MCP e chat (EXTENSÃO)

> Começa após G4 (resultados principais fechados).
>
> **Antecipado (ADR-0006, 2026-11-22):** página estática só descritiva em https://tccept.brunokobi.tech (`reports/pagina/`, `scripts/make_figures.py`, `scripts/deploy_pagina.sh`), sem desfechos. O painel abaixo, com evasão e conclusão, continua pós-G4.

## Painel web (`dashboard/`)
- Mapa coroplético de aderência por território (região imediata).
- Filtros: eixo, modalidade, tipo de curso, ano.
- Indicadores: evasão, conclusão, eficiência; tabela de ofertas.
- Stack sugerida: Streamlit + Plotly (ADR-0003). Dados servidos de DuckDB/Parquet.

## Servidor MCP (`mcp_server/`)
Ferramentas (somente leitura), mesmas consultas do painel:

| tool | parâmetros | retorno |
|---|---|---|
| `list_eixos` | — | eixos CNCT |
| `get_aderencia` | territorio?, eixo?, ano?, modalidade? | linhas de aderência |
| `get_indicadores` | campus?, curso?, ano?, modalidade? | evasão/conclusão por ciclo |
| `compare_modalidades` | eixo?, ano? | EaD × presencial |
| `get_territorio` | municipio ou codigo | território e estrutura produtiva top-N |
| `run_query_template` | template_id, params | consultas pré-definidas (sem SQL livre) |

Cada resposta inclui `query` (template + parâmetros) e `source` (tabelas/anos).

## Chat (`chat/`)
- LLM com acesso **apenas** às ferramentas do MCP; prompt de sistema exige citar consulta e números de origem; recusa quando não há dado.
- UI integrada ao painel.

## Avaliação do chat (`chat/eval/`)
- ~100 perguntas em `chat/eval/questions.jsonl` (`id, pergunta, tipo, resposta_esperada, consulta_referencia`), respostas conferidas por consulta direta.
- Tipos: factual simples, comparação, agregação, pergunta sem resposta nos dados (deve recusar).
- Métricas: % corretas; % sem base nos dados (alucinação); % recusa correta.
- Sem participação de pessoas.
