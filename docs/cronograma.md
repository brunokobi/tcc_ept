# Cronograma (v2)

Meses relativos ao início do TCC (M1); ajustar ao calendário oficial. **Núcleo** antes de **extensões**.

| # | Etapa | Meses | Tipo | Entregável | Spec |
|---|---|---|---|---|---|
| 1 | Revisão sistemática e refinamento com o orientador | 1–2 | núcleo | `docs/revisao/` | — |
| 2 | Coleta e harmonização (PNP, RAIS, CNCT, CNAE, IBGE) | 1–3 | núcleo | `data/processed/` | 01 |
| 3 | Anotação de referência (2 avaliadores) e reanotação | 2–4 | núcleo | `data/reference/` | 02 |
| 4 | Mapeamentos T (IA) e O (CBO) e validação | 3–4 | núcleo | mapa + métricas | 02 |
| 5 | Simulação de poder e **pré-registro no OSF** | 4 | núcleo | link OSF | 04, 06 |
| 6 | Índices Q, S, B; modelos; identificação | 4–6 | núcleo | `reports/` | 03, 04 |
| 7 | Redação do artigo e revisão | 6–8 | núcleo | `paper/` | — |
| 8 | Estudo de evento, SHAP, painel, MCP | 6–8 | extensão | — | 04, 05 |
| 9 | Entrega e defesa | 9 | — | — | — |

## Marcos
- **G1 (fim M3):** painel oferta × ciclo montado; números de ofertas EaD e de ciclos confirmados. ✅ 22.316 ciclos técnicos (1.855 EaD), edições 2018–2023 da PNP.
- **G2 (fim M4):** mapeamento T com macro-F1 > baseline; convergência T × O reportada. ✅ macro-F1 0,83 contra 0,46 (teste, 2026-11-20); T × O 0,65.
- **G3 (M4):** simulação de poder + pré-registro publicados. Sem G3, nada de estimar efeitos. ⏳ MDE calculado e rascunho pronto (`pre-registro/plano-osf.md`); falta o orientador e o OSF.
- **G4 (fim M6):** resultados principais e robustez fechados → extensões liberadas.

## Situação das etapas (2026-11-22)
| # | Situação |
|---|---|
| 1 | v1 feita (OpenAlex, 43 incluídos); faltam bases manuais, bola de neve e leitura completa (P9) |
| 2 | feita (RAIS 2012–2025, PNP 2018–2023); falta conferir a correspondência CNAE com o IBGE (P21) |
| 3 | feita por LLM (ADR-0004); validação humana de subamostra pendente (P12) |
| 4 | feita (G2) |
| 5 | MDE pronto; pré-registro em rascunho |
| 6 | índices prontos (`docs/resultados/indices.json`); modelos bloqueados até o OSF |
| 7 | figuras descritivas prontas (`reports/figures/`); redação não iniciada |
| 8 | antecipada só a página descritiva em https://tccept.brunokobi.tech (ADR-0006); painel com desfechos, MCP e chat seguem pós-G4 |
| 9 | — |
