# CLAUDE.md — TCC Aderência territorial (EaD/EPT, IFSul)

Projeto **pessoal acadêmico** do Bruno (TCC). Não é produto Vennx.

## Regras do projeto
- **Não usar o plugin `vennx-dev`** (nem skills, nem agentes `vennx-dev:*`, nem Asana). Fluxo direto.
- **Commits sem coautoria do Claude:** nunca adicionar `Co-Authored-By: Claude` nem "Generated with Claude Code" em commits ou PRs. Só commitar/pushar quando o Bruno pedir.
- Responder em português do Brasil; código e identificadores em inglês; docs em português.
- Specs em `docs/spec/` são a fonte de verdade do que implementar. Mudou decisão → ADR em `docs/adr/`.
- **Pré-registro:** nenhum modelo de efeito (`src/tcc_aderencia/models/`) pode ser estimado sobre os dados reais antes do pré-registro no OSF (`docs/pre-registro/`). Desvios do plano vão para `docs/pre-registro/desvios.md`.
- Apenas dados públicos e agregados; nenhum dado pessoal. Nunca ler `.env*`.
- Versionados: `data/pnp/` (microdados de eficiência acadêmica da PNP em Parquet), `data/external/` (CNCT, CNAE, IBGE) e `data/reference/`. Fora do git: `dados/` (CSVs originais), `data/raw/` e `data/interim/` (RAIS, reproduzível pelo script). Arquivo > 100 MB nunca vai pro git.

## Comandos
- Instalar: `pip install -e ".[dev,llm]"`
- Testes: `pytest` · Lint: `ruff check src tests`

## Mapa
Ver `docs/INDEX.md`.
